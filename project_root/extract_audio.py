import subprocess
from paths import AUDIO_FOLDER

def extract_audio(input_video_path: str, output_wav_path: str) -> None:
    command = [
        'ffmpeg',
        '-y',
        '-i', input_video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',  # ← ОБЯЗАТЕЛЬНО: моно-канал
        output_wav_path
    ]
    subprocess.run(command, check=True)

