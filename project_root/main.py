import os
from paths import TOP_FOLDER, BOTTOM_FOLDER, AUDIO_FOLDER, SUBTITLED_FOLDER, STACKED_FOLDER, BASE_FOLDER
from extract_audio import extract_audio
from transcribe_with_whisper import transcribe_srt, transcribe_word_level, create_word_level_ass
from subtitles import convert_srt_to_ass_tiktok_style
from ffmpeg_utils import burn_subtitles
from stacker import stack_loop_with_fade, get_video_duration
from config import WHISPER_MODEL_SIZE, USE_MFA_ALIGNMENT, MFA_FALLBACK_TO_NORMAL, USE_WORD_LEVEL_WHISPER
from mfa_align import process_with_mfa
import whisper
import subprocess


def process_video(top_video_path, model):
    basename = os.path.splitext(os.path.basename(top_video_path))[0]
    wav_path = os.path.join(AUDIO_FOLDER, f"{basename}.wav")
    srt_path = os.path.join(SUBTITLED_FOLDER, f"{basename}.srt")
    ass_path = os.path.join(SUBTITLED_FOLDER, f"{basename}.ass")

    print(f"\n=== Обработка видео: {basename} ===")

    extract_audio(str(top_video_path), str(wav_path))
    
    # Выбираем метод создания субтитров
    if USE_MFA_ALIGNMENT:
        # Пытаемся использовать MFA для точного выравнивания
        print("🎯 Пытаемся использовать MFA для точного выравнивания...")
        mfa_success = process_with_mfa(str(wav_path), str(srt_path), basename, str(ass_path))
        
        if not mfa_success and MFA_FALLBACK_TO_NORMAL:
            print("⚠️ MFA не сработал, используем обычные субтитры")
            transcribe_srt(str(wav_path), str(srt_path), model)
            convert_srt_to_ass_tiktok_style(str(srt_path), str(ass_path))
        elif not mfa_success:
            print("❌ MFA не сработал и fallback отключен")
            return
        else:
            print("🎯 Видео обработано с MFA выравниванием")
            
    elif USE_WORD_LEVEL_WHISPER:
        # Используем пословные тайминги Whisper
        print("🎯 Используем пословные тайминги Whisper...")
        word_data = transcribe_word_level(str(wav_path), str(srt_path) + ".json", model)
        create_word_level_ass(word_data['words'], str(ass_path))
        print("🎯 Видео обработано с пословными таймингами Whisper")
        
    else:
        # Обычная обработка без пословных таймингов
        print("📝 Используем обычные субтитры...")
        transcribe_srt(str(wav_path), str(srt_path), model)
        convert_srt_to_ass_tiktok_style(str(srt_path), str(ass_path))
        print("📝 Видео обработано с обычными субтитрами")

    bottom_videos = [
        os.path.join(BOTTOM_FOLDER, f)
        for f in os.listdir(BOTTOM_FOLDER)
        if f.lower().endswith(('.mp4', '.mkv'))
    ]
    if not bottom_videos:
        print("❌ Нет нижних видео для стэкинга.")
        return

    bottom_path = bottom_videos[0]
    stacked_out_path = os.path.join(STACKED_FOLDER, f"{basename}_stacked.mp4")
    subtitled_video_path = os.path.join(SUBTITLED_FOLDER, f"{basename}_subtitled.mp4")
    stack_loop_with_fade(bottom_path, top_video_path, stacked_out_path, str(BASE_FOLDER))
    print(stacked_out_path, ass_path, subtitled_video_path)
    burn_subtitles(stacked_out_path, ass_path, subtitled_video_path)

    print(f"✅ Завершено: {subtitled_video_path}")


def main():
    top_videos = [
        os.path.join(TOP_FOLDER, f)
        for f in os.listdir(TOP_FOLDER)
        if f.lower().endswith(('.mp4', '.mkv'))
    ]

    if not top_videos:
        print("❌ В папке top_clips нет видео.")
        return

    model = whisper.load_model(WHISPER_MODEL_SIZE)
    for video_path in top_videos:
        process_video(video_path, model=model)


if __name__ == "__main__":
    main()
