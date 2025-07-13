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

    print(f"[ШАГ 1] Верхнее видео (abs_top): {abs_top}")
    print(f"[ШАГ 1] Нижнее видео (abs_bottom): {abs_bottom}")

    # Определяем минимальную ширину
    def get_width(path):
        probe = ffmpeg.probe(path, v='error', select_streams='v:0', show_entries='stream=width')
        return int(probe['streams'][0]['width'])
    min_width = min(get_width(abs_top), get_width(abs_bottom))
    half_h = int(min_width * 8 / 9)
    out_h = half_h * 2

    try:
        video_info = ffmpeg.probe(abs_top, v='error', select_streams='v:0', show_entries='format=duration')
        duration = float(video_info['format']['duration'])
        print(f"🎬 Длительность верхнего видео: {duration:.2f} сек.")
    except ffmpeg._run.Error as e:
        print(f"❌ Ошибка при получении информации о видео: {e.stderr.decode()}")
        return

    print(f"[ШАГ 2] Фоновый верхний слой (top_blur) из: {abs_top}")
    print(f"[ШАГ 2] Фоновый нижний слой (bot_blur) из: {abs_bottom}")
    print(f"[ШАГ 3] Главный стек: снизу {abs_bottom}, сверху {abs_top}")
    print(f"[ШАГ 4] Итоговый стек накладывается на фон: стек ({abs_bottom} + {abs_top}) на фон ({abs_top} + {abs_bottom})")

    filter_complex = (
        # Обрезаем по минимальной ширине и приводим к одинаковой ширине
        f"[0:v]crop={min_width}:ih:(iw-{min_width})/2:0,setsar=1,scale={min_width}:-1[top_main];"
        f"[1:v]trim=duration={duration},setpts=PTS-STARTPTS,crop={min_width}:ih:(iw-{min_width})/2:0,setsar=1,scale={min_width}:-1[bot_main];"
        # Верхний размытый фон: blur, tile, crop сверху
        f"[top_main]boxblur=10:1,tile=1x2,crop={min_width}:{half_h}:0:0[top_blur];"
        # Нижний размытый фон: blur, tile, crop снизу (чтобы целое видео было внизу, дублирование — вверх)
        f"[bot_main]boxblur=10:1,tile=1x2,crop={min_width}:{half_h}:0:(2*ih-{half_h})[bot_blur];"
        # Стекаем фоны в 9:16
        f"[top_blur][bot_blur]vstack=inputs=2[bg];"
        # Основные видео без масштабирования - нижнее снизу, верхнее сверху
        f"[bot_main][top_main]vstack=inputs=2[main_stack];"
        # Наложение стакнутого видео на фон по центру
        f"[bg][main_stack]overlay=(W-w)/2:(H-h)/2[stacked]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", abs_top,
        "-i", abs_bottom,
        "-filter_complex", filter_complex,
        "-map", "[stacked]",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-crf", "23",
        "-preset", "medium",
        abs_out
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print("=== FFmpeg STDOUT ===\n", result.stdout)
    print("=== FFmpeg STDERR ===\n", result.stderr)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, output=result.stdout, stderr=result.stderr)

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
