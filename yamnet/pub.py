import json
#import zmq
import random
from paho.mqtt import client as mqtt_client
#from cbor2 import loads
from collections import OrderedDict
import time

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT broker connect")
        else:
            print(f"MQTT broker connect fail: {rc}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(mqtt, int(mqtt_port))
    return client

def publish(topic, client, message):
    result = client.publish(topic, message)
    if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"message Publish: {message}")
    else:
        print(f"message Publish Fail: {message}")


def json_msg(inferred_class,score,time):

    data = OrderedDict()
    data["name"] = str("Audio_") + str("01")
    data["cmd"] = "AudioDetectionEventReport"
    data["AudioDetectionEventReport"] = {
        "AudioNo": str("Audio_C") + str("01"),
        "ClassType": inferred_class,
        "Confidence": score,
        "DetectionTime": time,
    }

    data_json = json.dumps(data, ensure_ascii=False, indent="\t")

    client = connect_mqtt()
    client.loop_start()
    publish(topic, client, data_json)
    print("publish clear")
    client.loop_stop()

if __name__ == "__main__":
    OUT_ADDR = "tcp://HOST:PORT"
    mqtt = 'HOST'
    mqtt_port = 'PORT'
    client_id = f'publish-{random.randint(0, 1000)}'
    topic = "DataTopic"
    epoch_time_ms = int(time.time() * 1000)

    while True:
        AD_class, AD_score = test
        json_msg(AD_class,AD_score,time)
