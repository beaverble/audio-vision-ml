import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio

yamnet_model = hub.load('https://tfhub.dev/google/yamnet/1')

# 오디오 파일 경로
file_path = './test_data/siren1_16k.wav'

# 오디오 로드 함수
def load_wav_16k_mono(filename):
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

# 로드 및 예측
wav_data = load_wav_16k_mono(file_path)
scores, embeddings, spectrogram = yamnet_model(wav_data)
class_scores = tf.reduce_mean(scores, axis=0)
top_class = tf.math.argmax(class_scores)


# 클래스 이름 불러오기
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = list(pd.read_csv(class_map_path)['display_name'])

inferred_class = class_names[top_class]
top_score = class_scores[top_class].numpy()

print(f'The main sound is: {inferred_class} ({top_score * 100:.2f}% confidence)')