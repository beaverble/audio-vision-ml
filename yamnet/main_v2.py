import os
import json
import random
import time
from collections import OrderedDict

import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio
from paho.mqtt import client as mqtt_client

# YAMNet 모델 로컬 로드
yamnet_local_path = './saved_models/yamnet_model'
yamnet_model = hub.load(yamnet_local_path)

# 클래스 이름 로드
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = list(pd.read_csv(class_map_path)['display_name'])

# WAV 파일 로딩 함수
def load_wav_16k_mono(filename):
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

# YAMNet 예측 함수
def predict_audio(file_path):
    wav_data = load_wav_16k_mono(file_path)
    scores, embeddings, spectrogram = yamnet_model(wav_data)
    class_scores = tf.reduce_mean(scores, axis=0)
    top_class = tf.math.argmax(class_scores)
    inferred_class = class_names[top_class]
    top_score = class_scores[top_class].numpy()
    return inferred_class, float(top_score)

# ClassType 매핑 함수
def get_class_type(predicted_label):
    label = predicted_label.lower()

    if "scream" in label or "screaming" in label:
        return 101
    elif "police car" in label and "siren" in label:
        return 102
    elif "groan" in label:
        return 103
    elif "dog" in label:
        return 104
    elif any(x in label for x in ["vehicle horn", "car horn", "honking"]):
        return 105
    else:
        return 101  # 기본값 (매핑되지 않음)


# MQTT 연결
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT 연결 완료")
        else:
            print(f"MQTT 연결 실패: {rc}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(mqtt, int(mqtt_port))
    return client

# MQTT publish
def publish(topic, client, message):
    result = client.publish(topic, message)
    if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"전송 완료: {message}")
    else:
        print(f"전송 실패: {message}")

# JSON 메시지 구성 및 전송
def json_msg(inferred_class, score, timestamp_ms, class_type):
    audio_list = ["Audio_01", "Audio_02", "Audio_03", "Audio_04", "Audio_05"]
    name = random.choice(audio_list)
    data = OrderedDict()
    data["name"] = name
    data["cmd"] = "AudioDetectionEventReport"
    data["AudioDetectionEventReport"] = {
        "SensorId": name,
        "ClassType": class_type,
        "Confidence": round(score, 4),
        "DetectionTime": timestamp_ms
    }

    data_json = json.dumps(data, ensure_ascii=False, indent="\t")
    client = connect_mqtt()
    client.loop_start()
    publish(topic, client, data_json)
    client.loop_stop()

# test_data 폴더에서 랜덤 WAV 파일 선택
def get_random_wav_file(directory='./test_data'):
    wav_files = [f for f in os.listdir(directory) if f.endswith('.wav')]
    if not wav_files:
        raise FileNotFoundError("test_data 폴더에 WAV 파일이 없습니다.")
    return os.path.join(directory, random.choice(wav_files))

# 실행 메인 루프
if __name__ == "__main__":
    mqtt = 'HOST'
    mqtt_port = 'PORT'
    client_id = f'publish-{random.randint(0, 1000)}'
    topic = "DataTopic"

    while True:
        try:
            file_path = get_random_wav_file('./test_data')
            print(f"\n처리 중 파일: {file_path}")
            AD_class, AD_score = predict_audio(file_path)
            class_type = get_class_type(AD_class)
            epoch_time_ms = int(time.time() * 1000)
            json_msg(AD_class, AD_score, epoch_time_ms, class_type)

        except Exception as e:
            print(f"오류 발생: {e}")
        time.sleep(5)