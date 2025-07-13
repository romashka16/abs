import whisper
import os

def transcribe_srt(wav_path: str, srt_output_path: str, model) -> None:
    print(f"🎤 Начинаем распознавание речи: {wav_path}")
    
    # Улучшенные параметры для лучшего распознавания с пословными таймингами
    result = model.transcribe(
        wav_path, 
        language='ru',
        task='transcribe',
        verbose=True,
        word_timestamps=True,
        condition_on_previous_text=True,
        temperature=0.0  # Более стабильные результаты
    )
    
    print("Whisper определил язык как:", result.get('language'))
    print(f"📝 Распознано сегментов: {len(result['segments'])}")

    # Создаем обычные SRT субтитры (сегментные)
    segments = result['segments']
    with open(srt_output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, start=1):
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            f.write(f"{i}\n")
            f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
            f.write(f"{text}\n\n")

def transcribe_word_level(wav_path: str, output_path: str, model) -> dict:
    """Транскрипция с пословными таймингами для MFA-подобного выравнивания"""
    print(f"🎯 Начинаем пословную транскрипцию: {wav_path}")
    
    result = model.transcribe(
        wav_path, 
        language='ru',
        task='transcribe',
        verbose=True,
        word_timestamps=True,
        condition_on_previous_text=True,
        temperature=0.0
    )
    
    # Извлекаем пословные тайминги
    word_timings = []
    for segment in result['segments']:
        if 'words' in segment:
            for word_info in segment['words']:
                word_timings.append({
                    'word': word_info['word'].strip(),
                    'start': word_info['start'],
                    'end': word_info['end']
                })
    
    print(f"📝 Распознано слов с таймингами: {len(word_timings)}")
    
    # Сохраняем результат
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'words': word_timings,
            'segments': result['segments'],
            'language': result.get('language', 'ru')
        }, f, ensure_ascii=False, indent=2)
    
    return {'words': word_timings, 'segments': result['segments']}

def create_word_level_ass(word_timings: list, ass_output_path: str) -> None:
    """Создание ASS субтитров с пословными таймингами (начало строго, конец регулируется для избежания наложения)"""
    print(f"🎨 Создаем ASS субтитры с пословными таймингами (начало строго, конец регулируется)")
    
    import pysubs2
    
    subs = pysubs2.SSAFile()
    
    # Стиль: желтый, круглый, с тенью
    style = pysubs2.SSAStyle()
    style.fontname = "Comic Sans MS"
    style.fontsize = 32
    style.primarycolor = pysubs2.Color(255, 255, 0)  # Желтый
    style.outlinecolor = pysubs2.Color(0, 0, 0)      # Черная окантовка
    style.backcolor = pysubs2.Color(0, 0, 0)
    style.bold = True
    style.shadow = 2
    style.outline = 1
    style.alignment = 2  # По центру
    subs.styles["MainStyle"] = style

    # Эффект: быстрое появление из центра
    effect = "\\fad(120,0)\\fscx120\\fscy120\\t(0,120,\\fscx100\\fscy100)"

    min_duration = 0.35  # минимальная длительность слова (сек)
    n = len(word_timings)
    for i, word_info in enumerate(word_timings):
        word = word_info['word']
        if not word or word in ['<s>', '</s>', '[BLANK_AUDIO]']:
            continue
        start = word_info['start']
        # Определяем конец: либо оригинальный, либо до старта следующего слова
        if i < n - 1:
            next_start = word_timings[i+1]['start']
            end = min(word_info['end'], next_start)
            # Но не короче минимальной длительности
            if end - start < min_duration:
                end = min(start + min_duration, next_start)
        else:
            end = word_info['end']
            if end - start < min_duration:
                end = start + min_duration
        text = f"{{\\an5{effect}}}{word}"
        event = pysubs2.SSAEvent(
            start=int(start * 1000),
            end=int(end * 1000),
            text=text,
            style="MainStyle"
        )
        subs.append(event)

    subs.save(ass_output_path)
    print(f"✅ ASS файл с пословными таймингами создан: {ass_output_path}")
    print(f"🎨 Начало слова строго по Whisper, конец регулируется для избежания наложения")

def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
