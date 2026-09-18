from pydub import AudioSegment
import tensorflow as tf
import tensorflow_io as tfio
import os


def convert_mp3_to_wav(mp3_path, wav_path):
    audio = AudioSegment.from_mp3(mp3_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    audio.export(wav_path, format="wav")
    return wav_path

def load_wav_16k_mono(filename):
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(file_contents, desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

# 변환 및 사용 예시
mp3_path = "./test_data/siren.mp3"
wav_path = "./test_data/siren1.wav"
convert_mp3_to_wav(mp3_path, wav_path)
wav_tensor = load_wav_16k_mono(wav_path)

def force_wav_to_16bit(input_path, output_path):
    audio = AudioSegment.from_wav(input_path)

    # 샘플 포맷 설정
    audio = audio.set_sample_width(2)  # 16-bit = 2 bytes
    audio = audio.set_channels(1)  # mono
    audio = audio.set_frame_rate(16000)  # 16kHz

    # 출력 경로 디렉토리 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 파일 저장
    audio.export(output_path, format="wav")
    print(f"변환 완료: {output_path}")

# wav 25bit -> 16bit
input_path = "./test_data/siren1.wav"
output_path = "./test_data/siren1_16k.wav"

force_wav_to_16bit(input_path, output_path)