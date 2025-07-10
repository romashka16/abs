import os
import time
import schedule
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Константы
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_FILE')
VIDEO_DIRECTORY = os.getenv('VIDEO_DIRECTORY')
# Устанавливаем время на 2 минуты вперед от текущего времени
UPLOAD_TIME = (datetime.now() + timedelta(seconds=1)).strftime('%H:%M')

def get_authenticated_service():
    """Создание авторизованного сервиса YouTube."""
    credentials = None
    
    # Проверка наличия токена
    if os.path.exists('token.json'):
        try:
            from google.oauth2.credentials import Credentials
            credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Ошибка при загрузке токена: {e}")
            credentials = None
    
    # Если нет токена или он недействителен, запрашиваем новый
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except Exception as e:
                print(f"Не удалось обновить токен: {e}")
                print("Удаляем старый токен и создаем новый...")
                if os.path.exists('token.json'):
                    os.remove('token.json')
                credentials = None
        
        # Если все еще нет валидных credentials, создаем новые
        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        # Сохраняем токен
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    
    return build('youtube', 'v3', credentials=credentials)

def upload_video(youtube, video_path):
    """Загрузка видео на YouTube."""
    try:
        # Получаем имя файла без расширения для заголовка
        video_title = os.path.splitext(os.path.basename(video_path))[0]
        
        # Создаем запрос на загрузку
        request_body = {
            'snippet': {
                'title': video_title,
                'description': f'Автоматически загружено {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                'tags': ['автозагрузка', 'python'],
                'categoryId': '22'  # Категория "People & Blogs"
            },
            'status': {
                'privacyStatus': 'private',  # Можно изменить на 'public' или 'unlisted'
                'selfDeclaredMadeForKids': False
            }
        }

        # Создаем объект медиа для загрузки
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True
        )

        # Выполняем загрузку
        request = youtube.videos().insert(
            part=','.join(request_body.keys()),
            body=request_body,
            media_body=media
        )

        response = request.execute()
        print(f'Видео успешно загружено! ID: {response["id"]}')
        return True

    except Exception as e:
        print(f'Ошибка при загрузке видео: {str(e)}')
        return False

def get_next_video():
    """Получение следующего видео для загрузки из директории."""
    if not os.path.exists(VIDEO_DIRECTORY):
        print(f'Директория {VIDEO_DIRECTORY} не существует')
        return None
    
    videos = [f for f in os.listdir(VIDEO_DIRECTORY) if f.endswith(('.mp4', '.avi', '.mov'))]
    if not videos:
        print('Нет доступных видео для загрузки')
        return None
    
    return os.path.join(VIDEO_DIRECTORY, videos[0])

def upload_job():
    """Задача для ежедневной загрузки."""
    print(f'Запуск задачи загрузки в {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    youtube = get_authenticated_service()
    video_path = get_next_video()
    
    if video_path:
        if upload_video(youtube, video_path):
            # После успешной загрузки перемещаем файл в папку uploaded
            uploaded_dir = os.path.join(VIDEO_DIRECTORY, 'uploaded')
            os.makedirs(uploaded_dir, exist_ok=True)
            os.rename(video_path, os.path.join(uploaded_dir, os.path.basename(video_path)))

def main():
    print('Запуск сервиса автоматической загрузки видео на YouTube')
    print(f'Время загрузки установлено на {UPLOAD_TIME}')
    now = datetime.now().strftime('%H:%M')
    print(f'Текущее время: {now}')

    # Если текущее время совпадает с UPLOAD_TIME — загружаем сразу
    if now == UPLOAD_TIME:
        print('Время загрузки совпадает с текущим временем, выполняем загрузку...')
        upload_job()
    elif now > UPLOAD_TIME:
        print('Время загрузки уже прошло сегодня, следующая загрузка будет завтра.')
    else:
        print('Время загрузки еще не наступило сегодня.')

    print('Ожидание времени следующей загрузки...')
    schedule.every().day.at(UPLOAD_TIME).do(upload_job)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main() 