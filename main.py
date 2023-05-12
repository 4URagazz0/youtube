import numpy as np
import pandas as pd

from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime


# API ключ здесь
api_key = 'AIzaSyDbQPJGfwACUP8PRydURogt5o6l19MJgoQ'
# Cоздание объекта YouTube API
youtube = build('youtube', 'v3', developerKey=api_key)

# ID канала "Python Programmer"
channel_id = ['UCfxnN0xALQR6OtznIj35ypQ', 'UCGVgpNgVwiWmimN-lFazj6w']
# ID плейлиста "Uploads" на канале "Python Programmer"
playlist_id = ['PLxiU3nwEQ4PFFbQhddlom7ZgivN9OmFTc']


df_channel = pd.DataFrame({'id': [], 'channel_name': [], 'channel_description': [], 'channel_published_date': []})
c_id = []
names = []
descriptions = []
published_dates = []


def parse_channel(ch_id):
    # Метод channels().list() - для получения информации о канале по его ID
    channel_info = youtube.channels().list(part='snippet,contentDetails', id=ch_id).execute()
    # Извлекаем информацию о канале
    channel_title = channel_info['items'][0]['snippet']['title']
    channel_description = channel_info['items'][0]['snippet']['description']
    channel_published_date = channel_info['items'][0]['snippet']['publishedAt']
    return channel_title, channel_description, channel_published_date


def channel_df():
    for ch_id in channel_id:
        channel_title, channel_description, channel_published_date = parse_channel(ch_id)
        c_id.append(ch_id)
        names.append(channel_title)
        descriptions.append(channel_description)
        published_dates.append(channel_published_date)
    df_channel.id = c_id
    df_channel.channel_name = names
    df_channel.channel_description = descriptions
    df_channel.channel_published_date = published_dates
    return df_channel


def video():
    df = channel_df()
    for n, ch_id in enumerate(df['id'], start=1):
        playlist_items = []
        # Используйте метод playlistItems().list() для получения списка видео на канале
        channel_info = youtube.channels().list(part='contentDetails', id=ch_id).execute()

        # Получение ID списка воспроизведения канала
        uploads_list_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Получение списка всех видео на канале
        next_page_token = None

        while True:
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_list_id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()

            playlist_items += playlist_response['items']
            next_page_token = playlist_response.get('nextPageToken')

            if next_page_token is None:
                break

        # Получение URL-адресов всех видео на канале
        video_urls = []
        video_ids = [np.NaN]
        video_titles = [np.NaN]
        video_descriptions = [np.NaN]
        for item in playlist_items:
            video_id = item['snippet']['resourceId']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'

            # # Получите субтитры с таймкодом видео
            # try:
            #     transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            #     print(transcript_list)
            #     # for transcript in transcript_list:
            #     #     for i in transcript.translate().fetch():
            #     #         print(i)
            # except:
            #     print('no sub', video_url)

            # with open(f"sub/{video_titles}.txt", "w") as f:
            #     f.write("{}\n".format(i))

            video_ids.append(video_id)
            video_urls.append(video_url)
            video_titles.append(item['snippet']['title'])
            video_descriptions.append(item['snippet']['description'])

        # Вывод всех URL-адресов видео на канале
        u_video = pd.DataFrame({'video_urls': video_urls})
        df1 = df[n - 1:n]
        df_v = pd.concat([df1.iloc[:n+1], u_video, df1.iloc[n+1:]]).reset_index(drop=True)
        df_v['video_id'] = video_ids
        df_v['video_titles'] = video_titles
        df_v['video_descriptions'] = video_descriptions
        print(df_v)
        df_v.to_excel(f'data{ch_id}.xlsx')


video()
