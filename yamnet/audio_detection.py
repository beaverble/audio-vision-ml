#!pip install -q "tensorflow==2.11.*"
# tensorflow_io 0.28 is compatible with TensorFlow 2.11
#!pip install -q "tensorflow_io==0.28.*

import os
#from IPython import display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_io as tfio

yamnet_model_handle = 'https://tfhub.dev/google/yamnet/1'
yamnet_model = hub.load(yamnet_model_handle)

testing_wav_file_name = tf.keras.utils.get_file('man-scream_16k.wav',
                                                'https://storage.googleapis.com/audioset/miaow_16k.wav',
                                                cache_dir='./',
                                                cache_subdir='test_data')

#print(testing_wav_file_name)

# Utility functions for loading audio files and making sure the sample rate is correct.
def load_wav_16k_mono(filename):
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

# 4. 오디오 로드 및 예측
testing_wav_data = load_wav_16k_mono(testing_wav_file_name)
scores, embeddings, spectrogram = yamnet_model(testing_wav_data)

# 5. 클래스 매핑
class_map_path = yamnet_model.class_map_path().numpy().decode('utf-8')
class_names = list(pd.read_csv(class_map_path)['display_name'])

# 6. 가장 높은 점수 클래스 추출
class_scores = tf.reduce_mean(scores, axis=0)
top_class = tf.math.argmax(class_scores)
inferred_class = class_names[top_class]
top_score = class_scores[top_class].numpy()

print(f'The main sound is: {inferred_class} ({top_score * 100:.2f}% confidence)')


"""
# 7. 시각화
waveform = testing_wav_data.numpy()
scores_np = scores.numpy()
spectrogram_np = spectrogram.numpy()

plt.figure(figsize=(12, 8))

# 1) 파형
plt.subplot(3, 1, 1)
plt.plot(waveform)
plt.title("Waveform")
plt.xlabel("Sample")
plt.ylabel("Amplitude")
plt.xlim([0, len(waveform)])

# 2) 스펙트로그램
plt.subplot(3, 1, 2)
plt.imshow(spectrogram_np.T, aspect='auto', interpolation='nearest', origin='lower')
plt.title("Log-Mel Spectrogram")
plt.ylabel("Mel Bands")
plt.xlabel("Time Frames")

# 3) Top-N 클래스 점수 시각화
mean_scores = np.mean(scores_np, axis=0)
top_n = 10
top_class_indices = np.argsort(mean_scores)[::-1][:top_n]

plt.subplot(3, 1, 3)
plt.imshow(scores_np[:, top_class_indices].T, aspect='auto', interpolation='nearest', cmap='gray_r')

patch_padding = (0.025 / 2) / 0.01  # 모델 문서 기준
plt.xlim([-patch_padding-0.5, scores.shape[0] + patch_padding-0.5])
plt.yticks(range(top_n), [class_names[i] for i in top_class_indices])
plt.title("Top-10 Class Scores Over Time")
plt.xlabel("Time Frames")
plt.ylabel("Classes")

plt.tight_layout()
plt.show()
"""