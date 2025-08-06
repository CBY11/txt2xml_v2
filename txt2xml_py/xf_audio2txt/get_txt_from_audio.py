from . import get_audio, xf_example, lbk_example

def get_txt_from_audio():
    audio_file = get_audio.get_audio_file()
    txt_command = lbk_example.audio_to_text(audio_file)
    print(txt_command)
    return txt_command