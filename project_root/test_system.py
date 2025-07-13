#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы системы без MFA
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config import USE_MFA_ALIGNMENT, MFA_FALLBACK_TO_NORMAL, USE_WORD_LEVEL_WHISPER
from paths import TOP_FOLDER, BOTTOM_FOLDER, AUDIO_FOLDER, SUBTITLED_FOLDER, STACKED_FOLDER, BASE_FOLDER

def test_system_configuration():
    """Проверка конфигурации системы"""
    print("🔧 Проверка конфигурации системы")
    print("=" * 50)
    
    print(f"⚙️ USE_MFA_ALIGNMENT: {USE_MFA_ALIGNMENT}")
    print(f"⚙️ USE_WORD_LEVEL_WHISPER: {USE_WORD_LEVEL_WHISPER}")
    print(f"⚙️ MFA_FALLBACK_TO_NORMAL: {MFA_FALLBACK_TO_NORMAL}")
    
    if USE_MFA_ALIGNMENT:
        print("🎯 MFA включен - будет использоваться для точного выравнивания")
    elif USE_WORD_LEVEL_WHISPER:
        print("🎯 Пословные тайминги Whisper включены - отличная альтернатива MFA!")
        print("   ✅ Дает пословные тайминги без сложной установки")
        print("   ✅ Работает стабильно на Windows")
        print("   ✅ Качество близко к MFA")
    else:
        print("📝 Обычные субтитры - базовый режим")

def test_paths():
    """Проверка путей"""
    print("\n📁 Проверка путей")
    print("=" * 50)
    
    paths_to_check = [
        ("BASE_FOLDER", BASE_FOLDER),
        ("TOP_FOLDER", TOP_FOLDER),
        ("BOTTOM_FOLDER", BOTTOM_FOLDER),
        ("AUDIO_FOLDER", AUDIO_FOLDER),
        ("SUBTITLED_FOLDER", SUBTITLED_FOLDER),
        ("STACKED_FOLDER", STACKED_FOLDER)
    ]
    
    all_good = True
    for name, path in paths_to_check:
        if os.path.exists(path):
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (не существует)")
            all_good = False
    
    return all_good

def test_video_files():
    """Проверка наличия видео файлов"""
    print("\n🎬 Проверка видео файлов")
    print("=" * 50)
    
    # Проверяем верхние видео
    if os.path.exists(TOP_FOLDER):
        top_videos = [f for f in os.listdir(TOP_FOLDER) if f.lower().endswith(('.mp4', '.mkv'))]
        if top_videos:
            print(f"✅ Верхние видео найдены: {len(top_videos)} файлов")
            for video in top_videos[:3]:  # Показываем первые 3
                print(f"   📹 {video}")
            if len(top_videos) > 3:
                print(f"   ... и еще {len(top_videos) - 3} файлов")
        else:
            print("❌ В папке top_clips нет видео файлов")
    else:
        print("❌ Папка top_clips не существует")
    
    # Проверяем нижние видео
    if os.path.exists(BOTTOM_FOLDER):
        bottom_videos = [f for f in os.listdir(BOTTOM_FOLDER) if f.lower().endswith(('.mp4', '.mkv'))]
        if bottom_videos:
            print(f"✅ Нижние видео найдены: {len(bottom_videos)} файлов")
            for video in bottom_videos[:3]:  # Показываем первые 3
                print(f"   📹 {video}")
            if len(bottom_videos) > 3:
                print(f"   ... и еще {len(bottom_videos) - 3} файлов")
        else:
            print("❌ В папке bottom_clips нет видео файлов")
    else:
        print("❌ Папка bottom_clips не существует")

def test_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверка зависимостей")
    print("=" * 50)
    
    dependencies = [
        ("whisper", "openai-whisper"),
        ("ffmpeg-python", "ffmpeg-python"),
        ("pysubs2", "pysubs2"),
        ("numpy", "numpy"),
        ("pathlib", "pathlib")
    ]
    
    all_good = True
    for name, module in dependencies:
        try:
            __import__(name)
            print(f"✅ {name}: установлен")
        except ImportError:
            print(f"❌ {name}: не установлен")
            all_good = False
    
    return all_good

def test_ffmpeg():
    """Проверка ffmpeg"""
    print("\n🎬 Проверка ffmpeg")
    print("=" * 50)
    
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ ffmpeg установлен и работает")
            return True
        else:
            print("❌ ffmpeg не работает")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg не установлен")
        print("💡 Установите ffmpeg:")
        print("   - Скачайте с https://ffmpeg.org/download.html")
        print("   - Или используйте: winget install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки ffmpeg: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование системы обработки видео")
    print("=" * 60)
    
    # Тестируем конфигурацию
    test_system_configuration()
    
    # Тестируем зависимости
    deps_ok = test_dependencies()
    
    # Тестируем ffmpeg
    ffmpeg_ok = test_ffmpeg()
    
    # Тестируем пути
    paths_ok = test_paths()
    
    # Тестируем видео файлы
    test_video_files()
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"📦 Зависимости: {'✅' if deps_ok else '❌'}")
    print(f"🎬 ffmpeg: {'✅' if ffmpeg_ok else '❌'}")
    print(f"📁 Пути: {'✅' if paths_ok else '❌'}")
    
    if deps_ok and ffmpeg_ok and paths_ok:
        print("\n🎉 Система готова к работе!")
        print("💡 Запустите main.py для обработки видео")
        
        if USE_WORD_LEVEL_WHISPER:
            print("🎯 Система будет использовать пословные тайминги Whisper!")
            print("   Это даст вам точные тайминги каждого слова без MFA!")
        elif USE_MFA_ALIGNMENT:
            print("🎯 Система будет использовать MFA (если доступен)")
        else:
            print("📝 Система будет использовать обычные субтитры")
    else:
        print("\n⚠️ Система не готова к работе")
        print("🔧 Исправьте проблемы выше и повторите тест")
    
    print("\n💡 Рекомендации:")
    if not ffmpeg_ok:
        print("   1. Установите ffmpeg для обработки видео")
    if USE_MFA_ALIGNMENT:
        print("   2. Для MFA: установите conda и выполните conda install -c conda-forge montreal-forced-aligner")
    if not USE_WORD_LEVEL_WHISPER:
        print("   3. Рекомендуем включить USE_WORD_LEVEL_WHISPER = True для пословных таймингов")

if __name__ == "__main__":
    main() 