import subprocess
from paths import AUDIO_FOLDER

def extract_audio(input_video_path: str, output_wav_path: str) -> None:
    print(f"🎵 Извлекаем аудио: {input_video_path}")
    
    command = [
        'ffmpeg',
        '-y',
        '-i', input_video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',  # ← ОБЯЗАТЕЛЬНО: моно-канал
        '-af', 'highpass=f=200,lowpass=f=3000,volume=2.0',  # Улучшение качества
        output_wav_path
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ Аудио извлечено: {output_wav_path}")
    else:
        print(f"❌ Ошибка извлечения аудио: {result.stderr}")
        raise subprocess.CalledProcessError(result.returncode, command)

