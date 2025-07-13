import subprocess
import os
import shutil
from pathlib import Path
import pysubs2
from paths import MFA_CORPUS_TXTS, MFA_CORPUS_WAVS, MFA_OUTPUT, RUSSIAN_DICT, RUSSIAN_MFA_MODEL_DIR
from config import CLEAN_MFA_CORPUS, MFA_TIMEOUT

USE_WORD_LEVEL_WHISPER = True  # ✅ Включено
USE_MFA_ALIGNMENT = False      # ❌ Отключено

def check_mfa_available():
    """Проверка доступности MFA"""
    try:
        import subprocess
        result = subprocess.run(["mfa", "--version"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def clean_mfa_corpus():
    """Очистка MFA корпуса"""
    print("🧹 Очищаем MFA корпус...")
    try:
        if MFA_CORPUS_TXTS.exists():
            shutil.rmtree(MFA_CORPUS_TXTS)
        if MFA_CORPUS_WAVS.exists():
            shutil.rmtree(MFA_CORPUS_WAVS)
        if MFA_OUTPUT.exists():
            shutil.rmtree(MFA_OUTPUT)
        print("✅ MFA корпус очищен")
    except Exception as e:
        print(f"⚠️ Ошибка при очистке корпуса: {e}")

def prepare_mfa_corpus(audio_path: str, srt_path: str, video_name: str):
    """Подготовка корпуса для MFA"""
    print(f"📁 Подготавливаем корпус MFA для {video_name}")
    
    # Создаем папки если их нет
    MFA_CORPUS_TXTS.mkdir(parents=True, exist_ok=True)
    MFA_CORPUS_WAVS.mkdir(parents=True, exist_ok=True)
    MFA_OUTPUT.mkdir(parents=True, exist_ok=True)
    
    # Копируем аудио
    wav_dest = MFA_CORPUS_WAVS / f"{video_name}.wav"
    subprocess.run(["copy", str(audio_path), str(wav_dest)], shell=True, check=True)
    
    # Создаем текстовый файл из SRT
    txt_dest = MFA_CORPUS_TXTS / f"{video_name}.txt"
    with open(srt_path, 'r', encoding='utf-8') as srt_file:
        lines = srt_file.readlines()
    
    # Извлекаем только текст из SRT
    text_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.isdigit() and '-->' not in line:
            text_lines.append(line)
    
    with open(txt_dest, 'w', encoding='utf-8') as txt_file:
        txt_file.write(' '.join(text_lines))
    
    print(f"✅ Корпус подготовлен: {txt_dest}")

def run_mfa_alignment():
    """Запуск MFA выравнивания"""
    print("🎯 Запускаем MFA выравнивание...")
    
    if not check_mfa_available():
        print("❌ MFA не установлен или не работает")
        print("💡 Для установки MFA на Windows:")
        print("   1. Скачайте релиз с GitHub: https://github.com/MontrealCorpusTools/Montreal-Forced-Aligner/releases")
        print("   2. Или используйте conda: conda install -c conda-forge montreal-forced-aligner")
        return False
    
    try:
        # Запускаем выравнивание с таймаутом
        subprocess.run([
            "mfa", "align",
            str(MFA_CORPUS_WAVS),
            str(RUSSIAN_DICT),
            str(RUSSIAN_MFA_MODEL_DIR),
            str(MFA_OUTPUT),
            "--clean", "--verbose"
        ], check=True, timeout=MFA_TIMEOUT)
        print("✅ MFA выравнивание завершено")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка MFA: {e}")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ MFA превысил время ожидания ({MFA_TIMEOUT} сек)")
        return False
    except FileNotFoundError:
        print("❌ MFA не установлен. Установите: pip install montreal-forced-aligner")
        return False

def parse_textgrid_to_ass(textgrid_path, ass_path):
    """Конвертация TextGrid в ASS субтитры"""
    print(f"🔄 Конвертируем TextGrid в ASS: {textgrid_path}")
    
    try:
        # Пробуем разные способы импорта TextGrid
        try:
            from praatio import tgio as textgrid
            tg = textgrid.openTextGrid(textgrid_path)
        except ImportError:
            try:
                from textgrid import TextGrid
                tg = TextGrid.fromFile(textgrid_path)
            except ImportError:
                print("❌ Не удалось импортировать TextGrid. Установите: pip install praatio")
                return False
        
        word_tier = next((tier for tier in tg.tiers if tier.name.lower() in ["word", "words"]), None)
        
        if not word_tier:
            print("❌ Нет слоя 'word' в TextGrid.")
            return False

        subs = pysubs2.SSAFile()
        style = pysubs2.SSAStyle()
        style.fontname = "Anton"
        style.fontsize = 28
        style.primarycolor = pysubs2.Color(255, 128, 0)  # Оранжевый
        style.outlinecolor = pysubs2.Color(0, 0, 0)      # Черный
        style.bold = True
        style.shadow = 0
        style.outline = 1
        style.alignment = 2  # По центру (2 = center)
        subs.styles["TikTokStyle"] = style

        for interval in word_tier.intervals:
            word = interval.mark.strip()
            if not word:
                continue
            
            # Добавляем небольшой отступ для лучшего восприятия
            start = max(interval.minTime - 0.2, 0)
            end = interval.maxTime + 0.1

            text = f"{{\\an5}}{word}"
            event = pysubs2.SSAEvent(
                start=int(start * 1000),
                end=int(end * 1000),
                text=text,
                style="TikTokStyle"
            )
            subs.append(event)

        subs.save(ass_path)
        print(f"✅ ASS файл создан: {ass_path}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при конвертации TextGrid: {e}")
        return False

def process_with_mfa(audio_path: str, srt_path: str, video_name: str, output_ass_path: str):
    """Полный процесс MFA обработки"""
    print(f"🚀 Начинаем MFA обработку для {video_name}")
    
    # Проверяем доступность MFA
    if not check_mfa_available():
        print("❌ MFA недоступен")
        print("💡 Для использования MFA:")
        print("   1. Установите MFA: pip install montreal-forced-aligner")
        print("   2. Или скачайте релиз с GitHub")
        print("   3. Или используйте conda: conda install -c conda-forge montreal-forced-aligner")
        return False
    
    try:
        # 1. Подготавливаем корпус
        prepare_mfa_corpus(audio_path, srt_path, video_name)
        
        # 2. Запускаем MFA
        if not run_mfa_alignment():
            print("⚠️ MFA не удался, используем обычные субтитры")
            return False
        
        # 3. Конвертируем результат
        textgrid_path = MFA_OUTPUT / f"{video_name}.TextGrid"
        if textgrid_path.exists():
            if parse_textgrid_to_ass(str(textgrid_path), output_ass_path):
                # Очищаем корпус если включено
                if CLEAN_MFA_CORPUS:
                    clean_mfa_corpus()
                return True
            else:
                print("❌ Ошибка при конвертации TextGrid")
                return False
        else:
            print(f"❌ TextGrid файл не найден: {textgrid_path}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка в MFA процессе: {e}")
        return False
