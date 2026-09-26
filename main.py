from dotenv import load_dotenv
load_dotenv()

from utils.audio_processing import audio_preprocessing
from core.transcribe import get_transcription
from core.summarizer import summarizer,generate_summary_title
from core.notes import get_notes,generate_notes_title
from core.rag_engine import build_rag_chain

def transcript_pipeline(source : str, language : str = "english", progress_callback = None) -> str:
    if progress_callback:
        progress_callback(1, 4, "Downloading video...")

    audio_chunks = audio_preprocessing(source)

    if progress_callback:
        progress_callback(2, 4, "Extracting audio...")
    
    transcript = get_transcription(audio_chunks,language)

    if progress_callback:
        progress_callback(3, 4, "Processing transcript...")

    print(f"Transcription - {transcript[:300]}")

    if progress_callback:
        progress_callback(4, 4, "Complete")

    return transcript

def pipeline(transcript:str , choice:int = 1) -> dict :
    print("Starting Application.....\n")

    print("Menu\n1.Summary\n2.Notes\n3.RAG ChatBot")

    if choice==1:
        summary = summarizer(transcript)
        title = generate_summary_title(summary)

        result = { "title" : title , "summary" : summary}

        return result

    elif choice==2:
        notes = get_notes(transcript)
        title = generate_notes_title(notes)

        result = { "title" : title , "notes" : notes}

        return result

    elif choice==3:
        rag_chain = build_rag_chain(transcript)

        return {"chain" : rag_chain}

    return {"error" : "Invalid Choice"}