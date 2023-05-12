from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# API ключ здесь
api_key = 'AIzaSyDbQPJGfwACUP8PRydURogt5o6l19MJgoQ'
# ID канала "Python Programmer"
channel_id = 'UCfxnN0xALQR6OtznIj35ypQ'
# ID плейлиста "Uploads" на канале "Python Programmer"
playlist_id = 'PLxiU3nwEQ4PFFbQhddlom7ZgivN9OmFTc'

def parse_channel(
        api_key=str,
        channel_id=str,
        playlist_id=str
):
    # Cоздание объекта YouTube API
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Метод channels().list() для получения информации о канале по его ID
    channel_info = youtube.channels().list(part='snippet,contentDetails', id=channel_id).execute()
    # Извлекаем информацию о канале
    channel_title = channel_info['items'][0]['snippet']['title']
    channel_description = channel_info['items'][0]['snippet']['description']
    channel_published_date = channel_info['items'][0]['snippet']['publishedAt']

    # Получаем список видео на канале
    playlist_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    playlist_items = []
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()
        playlist_items += playlist_response['items']
        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    # Получаем текст субтитров для каждого видео
    # for video in playlist_items:
    #     video_id = video['snippet']['resourceId']['videoId']
    #     try:
    #         captions = youtube.captions().list(
    #             part='snippet',
    #             videoId=video_id
    #         ).execute()
    #         # Получаем текст субтитров
    #         captions_text = captions['items'][0]['snippet']['text']
    #     except HttpError as e:
    #         # Обрабатываем ошибки
    #         if e.resp.status in [403, 404]:
    #             print(f'Субтитры для видео {video_id} не найдены.')
    #         else:
    #             raise e

    # Метод playlistItems().list() для получения списка видео на канале
    playlist_items = youtube.playlistItems().list(part='snippet', playlistId=playlist_id).execute()
    # Выводим названия и описания всех видео на канале
    for item in playlist_items['items']:
        video_title = item['snippet']['title']
        video_description = item['snippet']['description']

    # Дата последнего добавленного видео на канале
    latest_video = playlist_items[0]['snippet']['publishedAt']
    latest_video = datetime.strptime(latest_video, '%Y-%m-%dT%H:%M:%SZ')
