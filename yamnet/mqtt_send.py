import json
import random
import time
import paho.mqtt.client as mqtt

broker = "HOST"
port = 0
topic = "DataTopic"

# MQTT Client 생성
client = mqtt.Client()

client.connect(broker, port, 60)
client.loop_start()

audio_list = ["Audio_01", "Audio_02", "Audio_03", "Audio_04", "Audio_05"]

while True:
    name = random.choice(audio_list)
    class_type = random.randint(101, 105)
    detection_time = time.time_ns()  # 현재 시간 ns단위

    data = {
        "name": "Audio_01",
        "cmd": "AudioDetectionEventReport",
        "AudioDetectionEventReport": {
            "SensorId": "Audio_01",
            "ClassType": 103,
            "Confidence": round(random.uniform(0.5, 0.99), 2),
            "DetectionTime": detection_time
        }
    }

    json_data = json.dumps(data, ensure_ascii=False)
    client.publish(topic, json_data)

    print("Send:", json_data)
    time.sleep(10)