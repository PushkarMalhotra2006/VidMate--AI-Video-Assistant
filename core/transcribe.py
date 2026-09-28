import os
from faster_whisper import WhisperModel
import requests
from pydub import AudioSegment

WHISPER_MODEL = os.getenv("WHISPER_MODEL","small")

transcription_model = None

def load_model():

    global transcription_model

    if transcription_model is None:
        print("Loading Whisper Model")
        transcription_model = WhisperModel(WHISPER_MODEL,device="cuda",compute_type="float16")
        print("Model Loaded")

    return transcription_model

def transcribe_chunk(chunk_path : str,lang:str = "english") -> str:

    model = load_model()

    lang_code = "en" if lang.lower()=="english" else None
    task = "transcribe" if lang.lower() == "english" else "translate"

    segments,info = model.transcribe(chunk_path,task = task,language=lang_code)

    result = "".join([segment.text for segment in segments])

    return result

def get_transcription(chunks: list , language : str = "english") -> str:

    transcript = ""

    for i,chunk in enumerate(chunks):
        print(f"sending {i} for translate")
        text = transcribe_chunk(chunk,language)

        transcript += text + " \n\n"

    print("Transcription Complete")

    return transcript.strip()