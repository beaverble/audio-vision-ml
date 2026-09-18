import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio
import json
import random
from paho.mqtt import client as mqtt_client

from collections import OrderedDict
import time

# 모델 로드
yamnet_local_path = './saved_models/yamnet_model'
yamnet_model = hub.load(yamnet_local_path)

# 클래스 이름 불러오기
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = list(pd.read_csv(class_map_path)['display_name'])

# 오디오 파일 로딩
def load_wav_16k_mono(filename):
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

# YAMNet
def predict_audio(file_path):
    wav_data = load_wav_16k_mono(file_path)
    scores, embeddings, spectrogram = yamnet_model(wav_data)
    class_scores = tf.reduce_mean(scores, axis=0)
    top_class = tf.math.argmax(class_scores)
    inferred_class = class_names[top_class]
    top_score = class_scores[top_class].numpy()
    return inferred_class, float(top_score)

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
def json_msg(inferred_class, score, timestamp_ms):
    data = OrderedDict()
    data["name"] = "Audio_01"
    data["cmd"] = "AudioDetectionEventReport"
    data["AudioDetectionEventReport"] = {
        "AudioNo": "Audio_C01",
        "ClassType": 201,
        "Confidence": round(score, 4),
        "DetectionTime": timestamp_ms
    }

    data_json = json.dumps(data, ensure_ascii=False, indent="\t")
    client = connect_mqtt()
    client.loop_start()
    publish(topic, client, data_json)
    client.loop_stop()

if __name__ == "__main__":
    mqtt = 'HOST'
    mqtt_port = 'PORT'
    client_id = f'publish-{random.randint(0, 1000)}'
    topic = "DataTopic"

    file_path = './test_data/miaow_16k.wav'

    while True:
        AD_class, AD_score = predict_audio(file_path)
        epoch_time_ms = int(time.time() * 1000)
        json_msg(AD_class, AD_score, epoch_time_ms)
        time.sleep(5)