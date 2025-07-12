import subprocess
import os
from paths import BASE_FOLDER

def burn_subtitles(input_video_path: str, subtitle_path: str, output_path: str) -> None:
    # Относительные пути относительно BASE_FOLDER с unix-слешами
    rel_vid = os.path.relpath(input_video_path, BASE_FOLDER).replace("\\", "/")
    rel_sub = os.path.relpath(subtitle_path, BASE_FOLDER).replace("\\", "/")
    rel_out = os.path.relpath(output_path, BASE_FOLDER).replace("\\", "/")

    print(f"🔥 Прижигаем субтитры → {rel_out}")

    # Предполагается, что subtitle_path — .ass файл
    subtitle_filter = f"ass={rel_sub}"

    command = [
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-i", rel_vid,
        "-vf", subtitle_filter,
        "-c:v", "libx264", "-crf", "23", "-preset", "medium",
        "-c:a", "copy",
        rel_out
    ]
    subprocess.run(command, check=True, cwd=BASE_FOLDER)