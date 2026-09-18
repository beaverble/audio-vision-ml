import tensorflow_hub as hub
import tensorflow as tf

# 최초 다운로드
yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# 저장할 경로
yamnet_local_path = './saved_models/yamnet_model'

# 저장
tf.saved_model.save(yamnet_model, yamnet_local_path)
print("✅ 모델 저장 완료:", yamnet_local_path)