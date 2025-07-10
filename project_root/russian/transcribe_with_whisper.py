import whisper
import os
def transcribe_srt(wav_path: str, srt_output_path: str, model) -> None:
    result = model.transcribe(wav_path, language='ru')  # ← обязательно указать язык
    print("Whisper определил язык как:", result.get('language'))

    segments = result['segments']
    print(segments)
    with open(srt_output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
