import os
import subprocess
import ffmpeg

def stack_loop_with_fade(bottom, top, out_path, BASE_FOLDER):
    import subprocess
    import ffmpeg
    import os

    abs_top = os.path.abspath(top)
    abs_bottom = os.path.abspath(bottom)
    abs_out = os.path.abspath(out_path)

    try:
        video_info = ffmpeg.probe(abs_top, v='error', select_streams='v:0', show_entries='format=duration')
        duration = float(video_info['format']['duration'])
        print(f"🎬 Длительность верхнего видео: {duration:.2f} сек.")
    except ffmpeg._run.Error as e:
        print(f"❌ Ошибка при получении информации о видео: {e.stderr.decode()}")
        return

    # filter_complex как строка
    filter_complex = (
        f"[0:v]scale=1280:360:force_original_aspect_ratio=decrease,pad=1280:360:(ow-iw)/2:(oh-ih)/2,setsar=1[top];"
        f"[1:v]trim=duration={duration},scale=1280:360:force_original_aspect_ratio=decrease,pad=1280:360:(ow-iw)/2:(oh-ih)/2,setsar=1[bottom];"
        f"[top][bottom]vstack=inputs=2[stacked];"
        f"[stacked]split=2[main][blur];"
        f"[blur]crop=1280:20:0:360,boxblur=5:1[blurline];"
        f"[main][blurline]overlay=0:360[overlay]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", abs_top,          # верхнее видео
        "-i", abs_bottom,       # нижнее видео
        "-filter_complex", filter_complex,
        "-map", "[overlay]",    # использовать стэканное видео с блюром
        "-map", "0:a?",         # взять звук из верхнего видео (если есть)
        "-c:v", "libx264",
        "-c:a", "aac",
        "-crf", "23",
        "-preset", "medium",
        "-shortest",            # ограничить длительность верхним видео
        abs_out
    ]

    print(f"🔨 Стэкаем с мягкой границей → {abs_out}")

    try:
        result = subprocess.run(cmd, cwd=BASE_FOLDER, capture_output=True, text=True, encoding="utf-8", errors="replace")
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
        result.check_returncode()
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении ffmpeg: {e.stderr}")
        return

    print("✅ Успешно: видео сохранено →", abs_out)

def get_video_duration(video_path: str) -> float:
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())
