# Whisper model size: "tiny", "base", "small", "medium", "large"
WHISPER_MODEL_SIZE = "medium"

# Путь к шрифту для TikTok-субтитров (установленному в системе или локально)
FONT_PATH = "C:/Windows/Fonts/Anton.ttf"  # убедись, что шрифт установлен

# Цвет текста и обводки
SUBTITLE_FILL_COLOR = "&H00A95EFF"  # оранжевый (BGR)
SUBTITLE_BORDER_COLOR = "&H00000000"  # чёрный

# Размер и стиль шрифта
SUBTITLE_FONT_SIZE = 32
SUBTITLE_BORDER_SIZE = 2

# Сдвиг субтитров вверх (в пикселях от низа)
SUBTITLE_MARGIN_V = 80

# Эффекты субтитров
SUBTITLE_ANIMATION_IN = "\\fad(200,0)"  # плавное появление
SUBTITLE_ANIMATION_OUT = ""             # без исчезновения

# Фоновый цвет для стэкинга (если видео меньше по высоте)
STACK_BACKGROUND = "black"

# Параметры ffmpeg логирования
FFMPEG_LOGLEVEL = "error"  # или "info", "warning", "quiet"

# Плавное появление субтитров (в секундах)
WORD_OFFSET_BEFORE = 0.5  # на сколько раньше показывать слово

# Переход между видео в стэке (если видео разной длины)
FADE_DURATION = 0.4  # в секундах
