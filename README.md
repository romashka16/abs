# YouTube Auto Uploader

Скрипт для автоматической загрузки видео на YouTube.

## Настройка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Создайте проект в Google Cloud Console:
   - Перейдите на https://console.cloud.google.com
   - Создайте новый проект
   - Включите YouTube Data API v3
   - Создайте учетные данные OAuth 2.0
   - Скачайте JSON файл с учетными данными и сохраните его как `client_secrets.json`

3. Создайте структуру директорий:
```
project/
├── videos/           # Папка с видео для загрузки
│   └── uploaded/     # Папка для загруженных видео
├── client_secrets.json
├── .env
└── youtube_uploader.py
```

4. Настройте файл `.env`:
```
CLIENT_SECRETS_FILE=client_secrets.json
VIDEO_DIRECTORY=videos
UPLOAD_TIME=12:00
```

## Использование

1. Поместите видео для загрузки в папку `videos/`
2. Запустите скрипт:
```bash
python youtube_uploader.py
```

Скрипт будет:
- Загружать одно видео каждый день в указанное время
- Перемещать загруженные видео в папку `videos/uploaded/`
- Выводить информацию о процессе загрузки в консоль

## Примечания

- При первом запуске потребуется авторизация через браузер
- Видео загружаются как приватные (можно изменить в коде)
- Поддерживаются форматы: MP4, AVI, MOV
- Имя видео будет использовано как заголовок на YouTube 