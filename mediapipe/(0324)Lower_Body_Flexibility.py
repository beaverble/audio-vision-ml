import cv2
import mediapipe as mp
import time
import math

# MediaPipe 초기화
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.9, min_tracking_confidence=0.9)

# 비디오 설정
video_path = "./testVideo5/test1.mp4"
cap = cv2.VideoCapture(video_path)
preview_width = 1280
preview_height = 720
cap.set(3, preview_width)
cap.set(4, preview_height)

# 상태 변수
current_stage = 0
score = 0
threshold = 0.155
hold_duration = 3
timeout_duration = 6
hold_start_time = {"left": None, "right": None}
touch_timeout_start = {"left": None, "right": None}
side_checked = {"left": False, "right": False}
current_side = None
knee_bent_time = None
paused = False


# 각도 계산 함수
def calculate_angle(a, b, c):
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)
    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    mag_ba = math.hypot(*ba)
    mag_bc = math.hypot(*bc)
    if mag_ba * mag_bc == 0:
        return 0
    angle_rad = math.acos(dot_product / (mag_ba * mag_bc))
    return math.degrees(angle_rad)


# 준비 자세 확인
def check_ready_position(landmarks):
    global current_stage
    epsilon = 0.025

    def is_leg_straight(hip, knee, ankle):
        if hip.visibility < 0.7 or knee.visibility < 0.7 or ankle.visibility < 0.7:
            return False
        return (
            abs(hip.y - knee.y) < epsilon and
            abs(knee.y - ankle.y) < epsilon and
            abs(hip.y - ankle.y) < epsilon
        )

    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

    left_leg_ready = is_leg_straight(left_hip, left_knee, left_ankle)
    right_leg_ready = is_leg_straight(right_hip, right_knee, right_ankle)

    if left_leg_ready or right_leg_ready:
        current_stage = 1
        return True
    return False


# 무릎 굽힘 확인
def check_knee_bent(landmarks):
    global current_stage, current_side, knee_bent_time

    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

    left_mid = (left_shoulder.y + left_hip.y) / 2
    right_mid = (right_shoulder.y + right_hip.y) / 2

    if left_knee.y < left_mid and not side_checked["right"]:
        current_side = "right"
        current_stage = 3
        knee_bent_time = time.time()
    elif right_knee.y < right_mid and not side_checked["left"]:
        current_side = "left"
        current_stage = 3
        knee_bent_time = time.time()


# 손-발 닿음 및 유지 확인
def check_touch_and_hold(landmarks, side):
    global hold_start_time, touch_timeout_start, score, current_stage, side_checked

    # 손: 왼손 vs 오른손 → visibility 비교
    left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
    hand = left_hand if left_hand.visibility >= right_hand.visibility else right_hand

    # 발: 왼발 vs 오른발 → visibility 비교
    left_foot = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_foot = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]
    foot = left_foot if left_foot.visibility >= right_foot.visibility else right_foot

    distance = math.hypot(hand.x - foot.x, hand.y - foot.y)

    if distance < threshold:
        if hold_start_time[side] is None:
            hold_start_time[side] = time.time()
        elapsed = time.time() - hold_start_time[side]
        if elapsed >= hold_duration:
            score += 1
            side_checked[side] = True
            current_stage = 1
            hold_start_time[side] = None
            touch_timeout_start[side] = None
    else:
        hold_start_time[side] = None
        if touch_timeout_start[side] is None:
            touch_timeout_start[side] = time.time()
        elif time.time() - touch_timeout_start[side] > timeout_duration:
            side_checked[side] = True
            current_stage = 1
            touch_timeout_start[side] = None


# 메인 루프
while cap.isOpened():
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (preview_width, preview_height))
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            if current_stage == 0:
                check_ready_position(landmarks)
            elif current_stage == 1:
                check_knee_bent(landmarks)
            elif current_stage == 3:
                if knee_bent_time and time.time() - knee_bent_time >= 2.0:
                    check_touch_and_hold(landmarks, current_side)

            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # 화면 출력
        cv2.putText(frame, f"Stage: {current_stage}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
        cv2.putText(frame, f"Score: {score}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 2)

        if current_side:
            hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value] if current_side == "right" else landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            foot = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value] if current_side == "right" else landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
            distance = math.hypot(hand.x - foot.x, hand.y - foot.y)
            cv2.putText(frame, f"Side: {current_side}", (50, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 100, 0), 2)
            cv2.putText(frame, f"Distance: {distance:.3f}", (50, 170), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 100, 100), 2)
            if hold_start_time[current_side]:
                elapsed = time.time() - hold_start_time[current_side]
                cv2.putText(frame, f"Hold: {elapsed:.1f}s", (50, 210), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 100), 2)

    cv2.imshow("Lower Body Flexibility Test", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 32:  # Space 키
        paused = not paused

cap.release()
cv2.destroyAllWindows()
