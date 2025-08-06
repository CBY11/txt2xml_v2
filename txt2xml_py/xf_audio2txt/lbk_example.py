from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

dir = "./txt2xml_py/audio2txt"
model_dir = f"{dir}/SenseVoiceSmall"
code_dir = f"{dir}/model.py"

model = AutoModel(
    model=model_dir,
    trust_remote_code=True,
    remote_code=code_dir,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
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