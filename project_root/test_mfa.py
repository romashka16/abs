#!/usr/bin/env python3
"""
Тестовый скрипт для проверки MFA интеграции
"""

import os
import sys
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config import USE_MFA_ALIGNMENT, MFA_FALLBACK_TO_NORMAL
from mfa_align import process_with_mfa, clean_mfa_corpus
from paths import MFA_CORPUS_TXTS, MFA_CORPUS_WAVS, MFA_OUTPUT, RUSSIAN_DICT, RUSSIAN_MFA_MODEL_DIR

def test_mfa_installation():
    """Проверка установки MFA"""
    print("🔍 Проверяем установку MFA...")
    
    try:
        import subprocess
        result = subprocess.run(["mfa", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ MFA установлен: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ MFA не работает: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ MFA не установлен")
        print("📦 Установите: pip install montreal-forced-aligner")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки MFA: {e}")
        return False

def test_mfa_paths():
    """Проверка путей MFA"""
    print("\n📁 Проверяем пути MFA...")
    
    paths_to_check = [
        ("RUSSIAN_DICT", RUSSIAN_DICT),
        ("RUSSIAN_MFA_MODEL_DIR", RUSSIAN_MFA_MODEL_DIR),
        ("MFA_CORPUS_TXTS", MFA_CORPUS_TXTS),
        ("MFA_CORPUS_WAVS", MFA_CORPUS_WAVS),
        ("MFA_OUTPUT", MFA_OUTPUT)
    ]
    
    all_good = True
    for name, path in paths_to_check:
        if path.exists():
            print(f"✅ {name}: {path}")
        else:
            print(f"❌ {name}: {path} (не существует)")
            all_good = False
    
    return all_good

def test_mfa_dependencies():
    """Проверка зависимостей"""
    print("\n📦 Проверяем зависимости...")
    
    dependencies = [
        ("TextGrid", "TextGrid"),
        ("pysubs2", "pysubs2"),
        ("subprocess", "subprocess"),
        ("pathlib", "pathlib")
    ]
    
    all_good = True
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}: установлен")
        except ImportError:
            print(f"❌ {name}: не установлен")
            all_good = False
    
    return all_good

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование MFA интеграции")
    print("=" * 50)
    
    # Проверяем конфигурацию
    print(f"⚙️ USE_MFA_ALIGNMENT: {USE_MFA_ALIGNMENT}")
    print(f"⚙️ MFA_FALLBACK_TO_NORMAL: {MFA_FALLBACK_TO_NORMAL}")
    
    # Тестируем установку
    mfa_installed = test_mfa_installation()
    
    # Тестируем зависимости
    deps_ok = test_mfa_dependencies()
    
    # Тестируем пути
    paths_ok = test_mfa_paths()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"🔧 MFA установлен: {'✅' if mfa_installed else '❌'}")
    print(f"📦 Зависимости: {'✅' if deps_ok else '❌'}")
    print(f"📁 Пути: {'✅' if paths_ok else '❌'}")
    
    if mfa_installed and deps_ok and paths_ok:
        print("\n🎉 MFA готов к использованию!")
        print("💡 Запустите main.py для обработки видео с MFA")
    else:
        print("\n⚠️ MFA не готов к использованию")
        print("🔧 Исправьте проблемы выше и повторите тест")
    
    # Очищаем тестовые данные
    if paths_ok:
        print("\n🧹 Очищаем тестовые данные...")
        clean_mfa_corpus()

if __name__ == "__main__":
    main() 