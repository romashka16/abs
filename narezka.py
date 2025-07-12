import os
import sys
import shutil
import subprocess
import whisper
import torch
from tqdm import tqdm
import ffmpeg
import pysubs2
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.AudioClip import concatenate_audioclips


# ─── КОНФИГУРАЦИЯ ───────────────────────────────────────────
BASE_FOLDER    = r"C:\Users\Леонид\Desktop\Videos"
TOP_FOLDER = os.path.join(BASE_FOLDER, "top_clips")
SEGMENT_TIME   = 120   # длина сегмента в секундах


STACKED_FOLDER   = os.path.join(BASE_FOLDER, "stacked_videos")
AUDIO_FOLDER     = os.path.join(BASE_FOLDER, "audio_wavs")
SUBTITLED_FOLDER = os.path.join(BASE_FOLDER, "subtitled_videos")
SEGMENTS_ROOT    = os.path.join(BASE_FOLDER, "segments")
BOTTOM_FOLDER = os.path.join(BASE_FOLDER, "bottom_clips")


for d in (STACKED_FOLDER, AUDIO_FOLDER, SUBTITLED_FOLDER, SEGMENTS_ROOT,BOTTOM_FOLDER):
    os.makedirs(d, exist_ok=True)
# ────────────────────────────────────────────────────────────

def list_top_videos():
    return [os.path.join(TOP_FOLDER, f) for f in sorted(os.listdir(TOP_FOLDER)) if is_video_file(f)]

def check_ffmpeg():
    if shutil.which("ffmpeg") is None:
        print("❌ FFmpeg не найден в PATH.")
        sys.exit(1)

def is_video_file(fn):
    return fn.lower().endswith(('.mp4','.mkv','.avi','.mov'))

def list_bottom_videos(TOP_VIDEO):
    outs = []
    for fn in sorted(os.listdir(BOTTOM_FOLDER)):
        full = os.path.join(BOTTOM_FOLDER, fn)
        if not os.path.isfile(full) or not is_video_file(fn):
            continue
        # Сравниваем нормализованные пути, чтобы исключить top
        if os.path.normcase(full) == os.path.normcase(TOP_VIDEO):
            continue
        outs.append(full)
    return outs


import subprocess
import os

def stack_loop_with_fade(bottom, top, out_path, BASE_FOLDER):
    # Используем абсолютные пути
    abs_top = os.path.abspath(top)
    abs_bottom = os.path.abspath(bottom)
    abs_out = os.path.abspath(out_path)

    # Получаем длительность верхнего видео с помощью ffprobe
    try:
        video_info = ffmpeg.probe(abs_top, v='error', select_streams='v:0', show_entries='format=duration')
        duration = float(video_info['format']['duration'])
        print(f"Длительность верхнего видео: {duration} секунд.")
    except ffmpeg._run.Error as e:
        print(f"Ошибка при получении информации о видео: {e.stderr.decode()}")
        return

    # Собираем команду для ffmpeg
    cmd = [
        "ffmpeg", "-y",
        "-i", abs_top,
        "-i", abs_bottom,
        "-t", str(duration),
        "-filter_complex",
        "[0:v]scale=1280:360[top];"
        "[1:v]scale=1280:360[bottom];"
        "[top][bottom]vstack=inputs=2[stacked];"
        "[stacked]split=2[main][blur];"
        "[blur]crop=1280:20:0:350,boxblur=5:1[bluredline];"
        "[main][bluredline]overlay=0:350",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        abs_out
    ]

    print(f"🔨 Стэкаем с мягкой границей → {abs_out}")

    # Выполняем команду
    try:
        result = subprocess.run(cmd, cwd=BASE_FOLDER, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)

        result.check_returncode()  # Проверяем, что команда прошла успешно
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при выполнении ffmpeg: {e.stderr}")
        return

    print("Процесс завершен успешно!")


# def prepare_mfa_corpus(wav_path, text_path, transcript_text):
#     # Создаём plain text файл с расшифровкой для MFA (например, text_path.lab)
#     with open(text_path, 'w', encoding='utf-8') as f:
#         f.write(transcript_text)
#
# def run_mfa_align(wav_path, text_path, output_dir):
#     # Вызов MFA с командой, например:
#     # mfa align corpus_path dictionary_path output_dir
#     # Здесь corpus_path - папка с wav и текстом
#     # Пример команды:
#     cmd = [
#         "mfa", "align",
#         "--clean",
#         "--output_format", "textgrid",
#         "path_to_corpus",
#         "path_to_dictionary",
#         output_dir
#     ]
#     subprocess.run(cmd, check=True)

# def parse_textgrid(textgrid_path):
#     # Парсим текстгрид и возвращаем тайминги слов
#     # Можно использовать библиотеку textgrid (pip install textgrid)
#     pass
#
# def create_ass_from_mfa(word_timings, ass_path):
#     # Создаём субтитры с точными таймингами слов и TikTok стилем
#     pass



def extract_audio(video_path, wav_path):
    rel_video = os.path.relpath(video_path, BASE_FOLDER).replace("\\", "/")
    rel_wav   = os.path.relpath(wav_path, BASE_FOLDER).replace("\\", "/")

    cmd = [
        "ffmpeg","-y","-i", rel_video,
        "-vn","-ac","1","-ar","16000",
        rel_wav
    ]
    subprocess.run(cmd, check=True, cwd=BASE_FOLDER)


def transcribe_srt(wav_path, srt_path, model):
    print(f"📝 Транскрибируем аудио → {os.path.basename(srt_path)}")

    result = model.transcribe(wav_path, language="ru")

    def fmt(t):
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        milliseconds = int((t * 1000) % 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], start=1):
            start = seg["start"]
            end = seg["end"]
            text = seg["text"].strip().replace("-->", "→")  # Предотвращаем конфликт с SRT-синтаксисом

            f.write(f"{i}\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")


def convert_srt_to_ass(srt_path, ass_path):
    print(f"🎯 Конвертируем SRT → ASS с появлением по одному слову: {srt_path} → {ass_path}")
    subs = pysubs2.load(srt_path, encoding="utf-8")

    style = pysubs2.SSAStyle()
    style.name = "SimpleStyle"
    style.fontname = "Arial"
    style.fontsize = 24
    style.primarycolor = pysubs2.Color(255, 255, 255)  # белый
    style.alignment = 5  # центр экрана
    subs.styles[style.name] = style

    new_subs = pysubs2.SSAFile()

    for line in subs:
        words = line.text.strip().split()
        total_duration = line.end - line.start
        if not words:
            continue

        word_duration = total_duration // len(words)

        for i, word in enumerate(words):
            start_time = line.start + i * word_duration
            end_time = start_time + word_duration

            new_line = pysubs2.SSAEvent(
                start=start_time,
                end=end_time,
                text=word,
                style=style.name,
                layer=0,
                marginl=line.marginl,
                marginr=line.marginr,
                marginv=line.marginv,
            )
            new_subs.append(new_line)

    new_subs.styles = subs.styles
    new_subs.save(ass_path)

def convert_srt_to_ass_tiktok_style(srt_path, ass_path):
    import pysubs2

    subs = pysubs2.load(srt_path, encoding="utf-8")

    style = pysubs2.SSAStyle()
    style.name = "TikTokStyle"
    style.fontname = "Anton"
    style.fontsize = 28
    style.primarycolor = pysubs2.Color(255, 128, 0)  # оранжевый
    style.outlinecolor = pysubs2.Color(0, 0, 0)      # черная обводка
    style.backcolor = pysubs2.Color(0, 0, 0)         # тень
    style.bold = True
    style.shadow = 0
    style.outline = 1
    style.alignment = 2  # центр снизу
    subs.styles[style.name] = style

    new_lines = pysubs2.SSAFile()
    new_lines.styles = subs.styles

    for line in subs:
        words = line.text.strip().split()
        if not words:
            continue

        total_duration = line.end - line.start
        word_duration = total_duration / len(words)
        min_duration = 2.0
        current_start = line.start

        for word in words:
            duration = max(word_duration, min_duration)
            start = current_start
            end = start + duration

            # Просто слово без анимаций
            text = f"{{\\an5}}{word}"

            new_line = pysubs2.SSAEvent(
                start=int(start * 1000),
                end=int(end * 1000),
                text=text,
                style=style.name,
                layer=0,
                marginl=0,
                marginr=0,
                marginv=0,
            )
            new_lines.append(new_line)

            current_start = end

    new_lines.save(ass_path)


def burn_subtitles(video_in, subtitle_path, out_path):
    if subtitle_path.endswith(".srt"):
        ass_path = subtitle_path.rsplit('.', 1)[0] + ".ass"
        convert_srt_to_ass(subtitle_path, ass_path)
        subtitle_path = ass_path  # заменяем путь на .ass файл

    rel_vid = os.path.relpath(video_in, BASE_FOLDER).replace("\\", "/")
    rel_ass = os.path.relpath(subtitle_path, BASE_FOLDER).replace("\\", "/")
    rel_out = os.path.relpath(out_path, BASE_FOLDER).replace("\\", "/")

    print(f"🔥 Прижигаем субтитры → {rel_out}")

    cmd = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-i", rel_vid,
        "-vf", f"ass={rel_ass}",
        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-c:a", "copy",
        rel_out
    ]
    subprocess.run(cmd, check=True, cwd=BASE_FOLDER)



def split_segments(video_path, name, ext):

    parts_dir = os.path.join(SEGMENTS_ROOT, f"{name}_parts")
    os.makedirs(parts_dir, exist_ok=True)
    clip = VideoFileClip(video_path)

    chunks = []
    for i in tqdm(range(0, int(clip.duration), SEGMENT_TIME), desc="Разделение видео на сегменты", unit="сегмент"):
        end = min(i + SEGMENT_TIME, clip.duration)
        sub_clip = clip.subclipped(i, end)
        chunks.append(sub_clip)

    if len(chunks) >= 2 and chunks[-1].duration < 0.9 * SEGMENT_TIME:
        chunks[-2] = concatenate_videoclips([chunks[-2], chunks[-1]])
        chunks.pop()

    for i, chunk in enumerate(chunks):
        out_file = os.path.join(parts_dir, f"{name}_part_{i:03}.mp4")
        chunk.write_videofile(out_file, codec='libx264', audio_codec='aac', temp_audiofile='temp.m4a', remove_temp=True)


def main():
    check_ffmpeg()

    top_videos = list_top_videos()
    if not top_videos:
        print("❌ Нет верхнего видео в папке top_clips.")
        sys.exit(1)
    TOP_VIDEO = top_videos[0]
    print(f"TOP_VIDEO: {TOP_VIDEO}")

    if not os.path.isfile(TOP_VIDEO):
        print("❌ Не найден верхний файл:", TOP_VIDEO)
        sys.exit(1)

    bottoms = list_bottom_videos(TOP_VIDEO)
    if not bottoms:
        print("❌ Нет нижних видео для обработки.")
        sys.exit(1)

    for b in bottoms:
        print(f"BOTTOM: {b}")

    if not top_videos:
        print("❌ Нет верхнего видео в папке top_clips.")
        sys.exit(1)


    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("► Whisper работает на", device.upper())
    model = whisper.load_model("small", device=device)

    for bottom in bottoms:
        base, _ = os.path.splitext(os.path.basename(bottom))

        stacked_path  = os.path.join(STACKED_FOLDER,   base + "_stacked.mp4")
        wav_path      = os.path.join(AUDIO_FOLDER,     base + ".wav")
        srt_path      = os.path.splitext(stacked_path)[0] + ".srt"
        subtitled_path= os.path.join(SUBTITLED_FOLDER, base + "_subtitled.mp4")

        stack_loop_with_fade(TOP_VIDEO, bottom, stacked_path,BASE_FOLDER)
        extract_audio(stacked_path, wav_path)
        transcribe_srt(wav_path, srt_path, model)
        burn_subtitles(stacked_path, srt_path, subtitled_path)
        split_segments(subtitled_path, base + "_subtitled", ".mp4")

        print(f"✅ Готово для «{base}»\n")

    print("🎉 Все файлы обработаны!")

if __name__ == "__main__":
    main()
