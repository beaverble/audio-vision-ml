import time
import random
import sys

# --- 1. 시뮬레이션 설정 ---
# YAMNet의 권장 샘플링 레이트와 유사하게 설정
SAMPLE_RATE = 16000
# YAMNet이 처리하는 프레임 크기 (0.96초)보다 작은 청크 크기 (예: 0.5초)
CHUNK_DURATION = 0.5  # 0.5초당 한 번 데이터 수신 시도
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)
TOTAL_DURATION = 5  # 총 시뮬레이션 시간 (5초)


# --- 2. 시뮬레이션 함수 ---
def simulate_realtime_audio_stream(total_time, chunk_size, chunk_duration):
    """
    실시간 오디오 스트림 수신 및 끊김을 시뮬레이션하는 함수.
    """
    start_time = time.time()
    current_time = 0

    # 2.1. 데이터 수신 횟수 계산
    num_chunks = int(total_time / chunk_duration)

    # 2.2. 끊김이 발생할 시점 정의 (예: 시작 후 3번째 청크)
    # 0부터 시작하므로 인덱스 2는 3번째 반복을 의미합니다.
    FAILURE_CHUNK_INDEX = 3

    print(f"--- Real-time Stream Simulation Started ({total_time}s) ---")

    for i in range(num_chunks):
        current_time = time.time() - start_time
        timestamp = time.strftime('%H:%M:%S', time.localtime(current_time + start_time))

        if i < FAILURE_CHUNK_INDEX:
            # 1. 오디오 데이터 받는 중 시뮬레이션
            print(f"({timestamp}, 오디오 데이터 받는 중 {i + 1}/{num_chunks})")

            # 실제 오디오를 읽는 시간 시뮬레이션
            time.sleep(chunk_duration)

        elif i == FAILURE_CHUNK_INDEX:
            # 2. 오디오 데이터 끊김 발생 시뮬레이션

            # 실제 읽기 함수에서 데이터가 없거나, I/O 오류가 발생했다고 가정
            is_data_read_successful = False

            if not is_data_read_successful:
                # 2.1. 끊김 발생 출력
                print(f"({timestamp}, 오디오 데이터 끊김 발생  {i + 1}/{num_chunks})")

                # 3. 예외 상황 탐지 및 처리
                try:
                    # 끊김이 발생한 상황에서 데이터 처리를 시도했다고 가정
                    # 이 시점에서 오류를 발생시켜 예외 상황을 시뮬레이션합니다.
                    raise IOError("스트림에서 데이터를 읽을 수 없습니다.")

                except IOError as e:
                    # 3.1. 예외상황 탐지 출력
                    # (실제 애플리케이션에서는 여기서 복구 로직이나 연결 재시도를 수행해야 합니다.)
                    exception_timestamp = time.strftime('%H:%M:%S', time.localtime())
                    print(f"({exception_timestamp}, 예외상황 탐지 - Error: {e})")
                    break  # 시뮬레이션 종료

        else:
            # 끊김 이후 복구되었다고 가정하고 계속 진행하고 싶다면 이 부분을 사용
            # 현재 시나리오에서는 끊김 발생 후 종료합니다.
            pass

    print("--- Simulation Finished ---")


# --- 3. 시뮬레이션 실행 ---
simulate_realtime_audio_stream(TOTAL_DURATION, CHUNK_SIZE, CHUNK_DURATION)