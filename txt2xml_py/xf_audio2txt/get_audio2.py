import pyaudio
import wave
import uuid
import keyboard
from pydub import AudioSegment
import os

# 设置临时环境变量来指定音频文件存储路径
os.environ['AUDIO_DIR'] = r"F:\SY_files\硕士_xml_提示词工程\code_file\txt2xml_v2\tmp\audio"

# 从环境变量中获取音频文件存储路径
audio_dir = os.environ.get('AUDIO_DIR', os.path.join(os.path.dirname(__file__), 'audio'))

def record_audio():
    # 配置PyAudio
    p = pyaudio.PyAudio()

    # 配置音频流参数
    sample_rate = 44100  # 采样率
    channels = 1  # 单声道
    sample_width = 2  # 16位
    frames_per_buffer = 1024

    # 打开音频流
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=frames_per_buffer)

    frames = []
    print("按空格键开始录音，按空格键停止录音。")

    recording = False
    while True:
        if keyboard.is_pressed('space'):  # 检测空格键按下
            if not recording:
                # 开始录音
                print("开始录音...")
                recording = True
                frames = []
            else:
                # 停止录音
                print("停止录音...")
                break
            while keyboard.is_pressed('space'):  # 防止空格键重复触发
                pass

        if recording:
            # 录制音频数据
            data = stream.read(frames_per_buffer)
            frames.append(data)

    # 停止流
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存录音为WAV临时文件
    temp_wave_filename = f"{uuid.uuid4()}.wav"
    with wave.open(temp_wave_filename, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

    # 将WAV文件转换为MP3
    mp3_filename = temp_wave_filename.replace(".wav", ".mp3")
    audio = AudioSegment.from_wav(temp_wave_filename)
    audio.export(mp3_filename, format="mp3")

    # 删除临时WAV文件
    import os
    os.remove(temp_wave_filename)

    print(f"录音保存为：{mp3_filename}")
    return mp3_filename

if __name__ == '__main__':
    # 调用录音函数
    record_audio()
