import os
import yt_dlp
from pydub import AudioSegment

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

import os
import subprocess
import yt_dlp

BGUTIL_DIR = os.path.join("/tmp", "bgutil-ytdlp-pot-provider")


def setup_bgutil():
    """Download and prepare bgutil PO-token provider on Streamlit Cloud."""

    if os.path.exists(os.path.join(BGUTIL_DIR, "server")):
        return

    print("Setting up bgutil PO-token provider...")

    # Clone the exact current bgutil release
    subprocess.run(
        [
            "git",
            "clone",
            "--depth", "1",
            "--branch", "2.0.0",
            "https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git",
            BGUTIL_DIR,
        ],
        check=True,
    )

    server_dir = os.path.join(BGUTIL_DIR, "server")

    # Install the server dependencies using Deno
    subprocess.run(
        [
            "deno",
            "install",
            "--allow-scripts=npm:canvas",
            "--frozen",
        ],
        cwd=server_dir,
        check=True,
    )

    print("bgutil PO-token provider ready.")


def download_yt_audio(url: str) -> str:

    setup_bgutil()

    output_path = os.path.join(
        DOWNLOAD_DIR,
        "%(title)s.%(ext)s"
    )

    ydl_opts = {
        "format": "bestaudio/best",

        "outtmpl": output_path,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],

        # Let yt-dlp use its normal YouTube logic.
        # Do NOT force android/mweb/tv/etc.
        "extractor_args": {
            "youtubepot-bgutilscript": {
                "server_home": os.path.join(
                    BGUTIL_DIR,
                    "server"
                )
            }
        },

        # EJS JavaScript challenge solver
        "js_runtimes": {
            "deno": {}
        },

        "remote_components": [
            "ejs:github"
        ],

        "quiet": False,
        "verbose": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        base_name = ydl.prepare_filename(info)

        filename = (
            os.path.splitext(base_name)[0]
            + ".wav"
        )

    return filename

def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path

def get_audio_chunks(wav_path : str, minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = minutes * 60 * 1000 

    chunks = []

    for i,start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start+chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)

    return chunks

def audio_preprocessing(source : str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_yt_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    #creating chunks
    chunks = get_audio_chunks(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks