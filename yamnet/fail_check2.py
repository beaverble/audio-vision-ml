import time
import json
import random

# --- 1. 시뮬레이션 설정 ---
# 탐지 장치 리스트 (Audio_01 ~ Audio_05)
DEVICE_NAMES = [f"Audio_{i:02d}" for i in range(1, 6)]

# 가능한 ClassType 리스트 (101 ~ 105)
CLASS_TYPES = list(range(101, 106))

# 시뮬레이션 주기 (각 장치에서 결과를 보내는 간격, 0.5초)
REPORT_INTERVAL = 0.5

# 총 시뮬레이션 시간 (10초)
TOTAL_DURATION = 10

# 끊김 시나리오 설정
# Audio_03이 끊기기 시작하는 시간 (예: 시작 후 3.0초)
FAILURE_START_TIME = 3.0
# Audio_03이 끊기는 시나리오 지속 시간 (예: 4.0초 동안 끊김)
FAILURE_DURATION = 4.0
# Audio_03이 다시 복구되는 시간
RECOVERY_TIME = FAILURE_START_TIME + FAILURE_DURATION


# --- 2. 탐지 결과 JSON 생성 함수 ---
def generate_detection_report(device_name, class_type, confidence):
    """
    요청된 형식으로 탐지 결과를 JSON 문자열로 생성합니다.
    """
    # 현재 시간을 밀리초 단위로 생성 (timestamp)
    # 173156543672253와 같은 매우 큰 숫자는 마이크로초 또는 나노초 단위일 수 있으나,
    # 여기서는 간단히 밀리초로 시뮬레이션
    timestamp_ms = int(time.time() * 1000) * 100

    report = {
        "name": device_name,
        "cmd": "AudioDetectionEventReport",
        "AudioDetectionEventReport": {
            "DeviceNo": f"{device_name.replace('Audio_', 'Audio_C')}",  # Audio_01 -> Audio_C01
            "ClassType": class_type,
            "Confidence": round(confidence, 2),
            "DetectionTime": timestamp_ms
        }
    }
    return json.dumps(report, indent=4)  # 보기 좋게 들여쓰기하여 출력


# --- 3. 실시간 시뮬레이션 루프 ---
def run_simulation():
    start_time = time.time()

    print("--- Audio Detection Simulation Started ---")

    while True:
        elapsed_time = time.time() - start_time

        if elapsed_time > TOTAL_DURATION:
            break

        current_time_str = time.strftime('%H:%M:%S', time.localtime())

        # 모든 장치에 대해 반복
        for device_name in DEVICE_NAMES:
            device_index = int(device_name.split('_')[-1])

            is_sending = True
            status_message = "오디오 데이터 받는 중"

            # --- Audio_03 끊김 시나리오 적용 ---
            if device_name == "Audio_03":
                if FAILURE_START_TIME <= elapsed_time < RECOVERY_TIME:
                    # 2. Audio_03이 끊김 (FAILURE_START_TIME 부터 RECOVERY_TIME 사이)
                    is_sending = False
                    status_message = "오디오 데이터 끊김 발생"

                    # 끊김 발생 시점을 표시 (매 프레임마다 출력되면 너무 많으므로, 한 번만 출력하도록 로직 조정 필요)
                    if elapsed_time < FAILURE_START_TIME + REPORT_INTERVAL:
                        print(f"({current_time_str}, {device_name} : {status_message})")
                        print(f"({current_time_str}, {device_name} : 예외상황 탐지 - 끊김 감지)")
                        continue  # 데이터 전송 스킵

                elif elapsed_time >= RECOVERY_TIME:
                    # 복구 후 정상 전송
                    status_message = "오디오 데이터 복구 후 전송"
                    pass

            # --- 데이터 전송 및 출력 ---
            if is_sending:
                # 1. 탐지 결과 시뮬레이션
                # ClassType과 Confidence를 랜덤하게 생성
                simulated_class = CLASS_TYPES[device_index % len(CLASS_TYPES)]
                simulated_confidence = random.uniform(0.6, 0.95)

                report_json = generate_detection_report(
                    device_name,
                    simulated_class,
                    simulated_confidence
                )

                # 시뮬레이션 상태와 JSON 출력
                print(f"({current_time_str}, {device_name} : {status_message})")
                print(report_json)
                print("-" * 30)

        # 다음 주기까지 대기
        time.sleep(REPORT_INTERVAL)


# --- 4. 시뮬레이션 실행 ---
try:
    run_simulation()
except KeyboardInterrupt:
    print("\n--- Simulation Stopped by User ---")