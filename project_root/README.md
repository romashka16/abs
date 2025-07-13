# Video Stacker with Subtitles

Проект для создания вертикальных видео с наложением субтитров. Создает видео в формате 9:16 с размытым фоном и синхронизированными субтитрами.

## Возможности

- Вертикальное наложение двух видео (верхнее и нижнее)
- Размытый фон из исходных видео
- Автоматическое создание субтитров с помощью Whisper
- Поддержка MFA (Montreal Forced Aligner) для точного выравнивания
- Пословные тайминги субтитров
- Автоматическое масштабирование до минимальной ширины
- Формат вывода 9:16

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd video-stacker
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Установите FFmpeg (обязательно):
   - Windows: скачайте с https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

4. Для MFA выравнивания (опционально):
```bash
conda install -c conda-forge montreal-forced-aligner
```

## Использование

1. Создайте папки для видео:
```
C:\Videos\
├── top_clips\      # Верхние видео
├── bottom_clips\   # Нижние видео
├── stacked_videos\ # Результат стэкинга
├── subtitled_videos\ # Финальные видео с субтитрами
└── audio_wavs\     # Временные аудио файлы
```

2. Поместите видео в соответствующие папки

3. Запустите обработку:
```bash
python main.py
```

## Конфигурация

Отредактируйте `config.py` для настройки:

- `WHISPER_MODEL_SIZE`: размер модели Whisper (tiny, base, small, medium, large)
- `USE_MFA_ALIGNMENT`: использовать MFA для точного выравнивания
- `USE_WORD_LEVEL_WHISPER`: использовать пословные тайминги Whisper
- `SUBTITLE_FONT_SIZE`: размер шрифта субтитров

## Алгоритм работы

1. **Извлечение аудио** из верхнего видео
2. **Транскрипция** с помощью Whisper или MFA
3. **Создание субтитров** в формате ASS
4. **Стэкинг видео**:
   - Обрезка обоих видео до минимальной ширины
   - Создание размытого фона из каждого видео
   - Вертикальное наложение видео
   - Наложение на размытый фон
5. **Наложение субтитров** на финальное видео

## Структура проекта

```
project_root/
├── main.py              # Главный скрипт
├── stacker.py           # Логика стэкинга видео
├── transcribe_with_whisper.py # Транскрипция
├── mfa_align.py         # MFA выравнивание
├── subtitles.py         # Конвертация субтитров
├── ffmpeg_utils.py      # Утилиты FFmpeg
├── extract_audio.py     # Извлечение аудио
├── config.py            # Конфигурация
├── paths.py             # Пути к папкам
└── russian/             # Русские модели MFA
```

## Требования

- Python 3.8+
- FFmpeg
- Whisper (OpenAI)
- Montreal Forced Aligner (опционально)
- ffmpeg-python
- openai-whisper

## Лицензия

MIT License 