import cv2
import mediapipe as mp
import numpy as np

# Mediapipe 설정
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)

    c = np.array(c)

    ab = a - b
    cb = c - b

    cosine_angle = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def check_pushup(landmarks, w, h):
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                     landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w,
                  landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w,
                  landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]

    elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    return 160 >= elbow_angle >= 140  # 팔이 적당히 펴져 있는지 확인


video_path = "./testVideo2/pushup_fail.mp4"
cap = cv2.VideoCapture(video_path)
pose = mp_pose.Pose()

pushup_count = 0
position = None
current_stage = 0  # 0: 초기, 1: 준비 완료, 3: 카운트 시작

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        h, w, _ = frame.shape

        if current_stage == 0 and check_pushup(landmarks, w, h):
            current_stage = 1  # 준비 완료 상태로 변경

        if current_stage == 3:
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]

            elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

            if elbow_angle <= 110:
                position = "DOWN"
            elif elbow_angle >= 160 and position == "DOWN":
                pushup_count += 1
                position = "UP"

            cv2.putText(frame, f'Push-ups: {pushup_count}', (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, f'Stage: {current_stage}', (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    cv2.imshow("Push-up Counter", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == 13:  # 엔터 키
        if current_stage == 1:
            current_stage = 3  # 푸쉬업 카운트 시작
            pushup_count = 0  # 카운트 초기화
        elif current_stage == 3:
            current_stage = 0  # 초기 상태로 돌아감
            pushup_count = 0

cap.release()
cv2.destroyAllWindows()
pose.close()
