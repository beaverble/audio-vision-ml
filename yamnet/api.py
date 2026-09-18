import os
import requests
import json

# 서버·자격증명은 환경변수로 주입 (실제 값은 저장소에 포함하지 않음)
SERVER = os.getenv("AIOT_API_HOST", "HOST")
PORT = os.getenv("AIOT_API_PORT", "")
user_id = os.getenv("AIOT_USER", "")
password = os.getenv("AIOT_PASSWORD", "")

BASE_URL = f"http://{SERVER}:{PORT}/api/v1"
AUTH_BASIC = os.getenv("AIOT_AUTH_BASIC", "")  # "Basic <base64>" 형식, 환경변수로 주입


TOKEN_INFO = {
    "user_id": user_id,
    "password": password,
    "grant_type": "password",
    "scope": "read"
}

APPLICATION_INFO = {
    "app_id": "AUDIO_APP",
    "app_type": "MIN",
    "protocol": "MQTT",
    "address": "mqtt-broker",
    "port": 8883,
    "username": os.getenv("MQTT_APP_USER", ""),
    "password": os.getenv("MQTT_APP_PASSWORD", ""),
    "description": "SN Audio Service Application"
}

OBJECT_TYPE_INFO = {
    "name": "AudioDetectionVO",
    "object_properties": [
        {"name": "AudioNo", "value_type": "string", "units": ""},
        {"name": "ClassType", "value_type": "int8", "units": ""},
        {"name": "Confidence", "value_type": "float32", "units": ""},
        {"name": "DetectionTime", "value_type": "int64", "units": ""}
    ]
}

def get_token():
    url = f"{BASE_URL}/oauth/token"
    headers = {
        "Content-Type": "application/json",
        "authorization": AUTH_BASIC
    }
    response = requests.post(url, headers=headers, json=TOKEN_INFO)
    print(f"[토큰발급] status: {response.status_code}, body: {response.text}")
    response.raise_for_status()
    json_resp = response.json()
    access_token = f"bearer {json_resp['access_token']}"
    return access_token


def register_application(access_token):
    url = f"{BASE_URL}/application"
    headers = {
        "Content-Type": "application/json",
        "authorization": access_token
    }
    response = requests.post(url, headers=headers, json=APPLICATION_INFO)
    print(f"[Application등록] status: {response.status_code}, body: {response.text}")
    response.raise_for_status()


def register_object_type(access_token):
    url = f"{BASE_URL}/profile/device/objectType"
    headers = {
        "Content-Type": "application/json",
        "authorization": access_token
    }
    response = requests.post(url, headers=headers, json=OBJECT_TYPE_INFO)

    print(f"[객체타입등록] status: {response.status_code}, body: {response.text}")
    response.raise_for_status()

def register_device_profile(access_token):
    url = f"{BASE_URL}/profile/device"
    headers = {
        "Content-Type": "application/json",
        "authorization": access_token
    }

    device_profile_data = {
        "name": "SN-Audio-Detection-Event-Profile",
        "manufacturer": "MyOrg",
        "description": "Audio Device Profile",
        "model": "AudioModel-2024",
        "labels": ["MyOrg", "Audio", "Obect-Detection"],
        "resources": [
            {
                "name": "AudioDetectionEventReport",
                "description": "Audio Object Detection Event Report",
                "type": "Object",
                "value_type": "AudioDetectionVO",
                "read_write": "R",
                "units": "",
                "media_type": "application/json"
            }
        ],
        "commands": [
            {
                "name": "AudioDetectionEventReportCmd",
                "read_write": "R",
                "resources": ["AudioDetectionEventReport"]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=device_profile_data)
    print(f"[디바이스프로파일등록] status: {response.status_code}, body: {response.text}")
    response.raise_for_status()


if __name__ == "__main__":
    try:
        token = get_token()
        register_application(token)
        register_object_type(token)
        register_device_profile(token)
        print("Audio 관련 API 호출 완료")
    except requests.HTTPError as e:
        print(f"API 호출 에러: {e.response.status_code} - {e.response.text}")

