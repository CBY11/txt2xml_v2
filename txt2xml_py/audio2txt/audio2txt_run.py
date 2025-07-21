import os

from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

import pyaudio
import wave

from . import get_audio

# 定义音频流参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# os.environ['ASR_DIR'] = r"F:\SY_files\SY_xml_prompt_work\code_file\txt2xml_v2\txt2xml_py\audio2txt"

model_dir = os.path.join(os.getenv('ASR_DIR', r".\audio2txt"), "SenseVoiceSmall")
model = AutoModel(
    model=model_dir,
    # vad_model="fsmn-vad",
    # vad_kwargs={"max_single_segment_time": 30000},
    device="cuda:0",
    disable_update=True
)


def audio_to_text(path):
    res = model.generate(
        input=path,
        cache={},
        language="auto",  # "zh", "en", "yue", "ja", "ko", "nospeech"
        use_itn=True,
        batch_size_s=60,
        merge_vad=True,  #
        merge_length_s=15,
    )
    text = rich_transcription_postprocess(res[0]["text"])
    return text
    # print("识别结果：", text)


def record_audio(path):
    p = pyaudio.PyAudio()

    # 打开音频流
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始录制音频...")

    frames = []

    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        print("录制结束")

    # 停止音频流
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 保存录制的音频
    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # print("音频已保存为output.wav")


def record_and_get_txt():
    audio_file = get_audio.get_audio_file()
    return audio_to_text(audio_file)

if __name__ == '__main__':
    while True:
        path = "tmp/tmp.wav"
        record_audio(path)
        audio_to_text(path)
        os.remove(path)
        print("是否继续？(y/[n])")
        c = input()
        if c != "y":
            break
