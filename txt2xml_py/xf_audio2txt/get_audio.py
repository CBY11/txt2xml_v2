import time

import pyaudio
import wave
import keyboard
import threading
import uuid
import os


# 设置临时环境变量来指定音频文件存储路径
# os.environ['AUDIO_DIR'] = r"F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\tmp\audio"

# 从环境变量中获取音频文件存储路径
audio_dir = os.environ.get('AUDIO_DIR', os.path.join(os.path.dirname(__file__), 'audio'))

res_file = ''

# 设置录音的参数
FORMAT = pyaudio.paInt16  # 音频格式
CHANNELS = 1  # 单声道
RATE = 16000  # 采样率
CHUNK = 1280    # 每次读取的数据块大小

# 创建pyaudio对象
p = pyaudio.PyAudio()

# 设置全局变量
is_recording = False
frames = []


# 录音函数
def record():
    global is_recording, frames, res_file
    # 生成唯一的文件名
    unique_filename = f"recording_{uuid.uuid4().hex}.wav"
    unique_filename = os.path.join(audio_dir, unique_filename)


    # 打开麦克风进行录音
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    # print("正在录音... 按空格结束录音")

    while is_recording:
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束，保存文件...")

    # 停止录音
    stream.stop_stream()
    stream.close()

    # 保存录音文件
    with wave.open(unique_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        # # 将WAV文件转换为MP3
        # mp3_filename = unique_filename.replace(".wav", ".mp3")
        # audio = AudioSegment.from_wav(unique_filename)
        # audio.export(mp3_filename, format="mp3")

    print(f"录音保存为文件: {unique_filename}")
    res_file = os.path.abspath(unique_filename)
    # return os.path.abspath(unique_filename)  # 返回文件的绝对路径


# 主线程控制录音的开始和结束
def start_stop_recording():
    global is_recording
    print("点击空格开始录音")
    while True:
        if keyboard.is_pressed('space'):  # 按空格键开始或停止录音
            if not is_recording:
                is_recording = True
                threading.Thread(target=record).start()  # 在新线程中开始录音
                print("正在录音... 按空格结束录音")
            else:
                is_recording = False
                break
            while keyboard.is_pressed('space'):  # 防止空格键被重复触发
                pass
    time.sleep(1)

def get_audio_file():
    start_stop_recording()
    return res_file

if __name__ == '__main__':
    # 启动录音控制线程
    txt = get_audio_file()
    print(txt)