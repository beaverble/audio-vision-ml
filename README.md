# 오디오·비전 AI (전이학습 · 자세추정)

오디오 이벤트 분류(YAMNet)와 영상 자세추정(MediaPipe)을 활용한 AI 응용 모음이다.
이상음향 탐지와 체력측정 자동화(PAPS)에 사용한 코드이며, 데이터·모델 가중치는 포함하지 않는다.

<br>

## 오디오 — YAMNet 이상음향 탐지 (`yamnet/`, `notebooks-audio/`)

- YAMNet(TF Hub) 오디오 이벤트 521종 분류 기반 **전이학습** — 비명·사이렌·고함 등 이상음향 탐지
- 실시간 감지 후 결과를 **MQTT로 발행**해 미들웨어와 연동 (`main.py`, `main_v2.py`, `mqtt_send.py`, `pub.py`)
- mp3→wav 변환·모델 다운로드 등 유틸 포함
- 전이학습 실험 노트북 (`transfer_learning_audio.ipynb`, `0708_yamnet.ipynb`)

<br>

## 비전 — MediaPipe 자세추정 (`mediapipe/`, `notebooks-mediapipe/`)

- MediaPipe 자세추정으로 체력측정 자동화
- 팔굽혀펴기 카운팅 (`(0221)pushup.py`) — 관절 각도 상태머신으로 판정
- 하지 유연성 측정 (`(0324)Lower_Body_Flexibility.py`)

<br>

## 메모

- 서버 주소·인증정보는 환경변수로 주입하며 저장소에 포함하지 않는다.
- 오디오/영상 데이터와 모델 가중치(`*.h5/.tflite`)는 제외했다.

<br>

## 기술 스택

Python · TensorFlow Hub · YAMNet · MediaPipe · OpenCV · paho-mqtt
