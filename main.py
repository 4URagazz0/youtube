import numpy as np
import pandas as pd
import os

from pytube import YouTube

from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build


api_key = 'AIzaSyDzDjhZyqed6yVte90FeCS3VIxNQ35bSZw'
youtube = build('youtube', 'v3', developerKey=api_key)

channel_id = ['UCAW3t2rRd7v2zYCuNlFMkxQ', 'UCrWWcscvUWaqdQJLQQGO6BA']

df_channel = pd.DataFrame({'id': [], 'channel_name': [], 'channel_description': [], 'channel_published_date': []})
c_id = []
names = []
descriptions = []
published_dates = []


def save_file_with_directory(path):
    """
    This function creates a directory for saving a file.

    Args:
        path (str): The path to the file for which the directory needs to be created.
    """
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)


def url_by_id(video_id):
    """
    This function generates the URL for a YouTube video based on its ID.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        video_url (str): The URL of the YouTube video.
    """
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    return video_url


def dowloand_video(video_id):
    """
    Downloads a YouTube video based on its ID.

    Args:
        video_id (str): The ID of the YouTube video.
    """
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    video_date = response['items'][0]['snippet']['publishedAt']
    channelId = response['items'][0]['snippet']['channelId']

    video_url = url_by_id(video_id)
    path = f'video/{channelId}/{video_date}/{video_id}'
    save_file_with_directory(path)
    YouTube(video_url).streams.get_highest_resolution().download(output_path=path)


def parse_channel(ch_id):
    """
    This function parses the information of a YouTube channel and retrieves its title, description, and published date.

    Args:
        ch_id (str): The ID of the YouTube channel.

    Returns:
        channel_title (str): The title of the channel
        channel_description (str): The description of the channel
        channel_published_date (datetime): published date
    """
    channel_info = youtube.channels().list(part='snippet,contentDetails', id=ch_id).execute()
    channel_title = channel_info['items'][0]['snippet']['title']
    channel_description = channel_info['items'][0]['snippet']['description']
    channel_published_date = channel_info['items'][0]['snippet']['publishedAt']
    return channel_title, channel_description, channel_published_date


def channel_df():
    """
    Retrieves channel information and creates a DataFrame.

    Returns:
        DataFrame: A DataFrame containing channel information with columns 'id', 'channel_name', 'channel_description', and 'channel_published_date'.
    """
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


def parse_playlist(playlist_id):
    """
    Parses a YouTube playlist and retrieves its information.

    Args:
        playlist_id (str): The ID of the YouTube playlist.

    Returns:
        published_at (datetime): playlist's published date
        title (str): The title of the playlist.
        videos_id (str): ID of the YouTube video
    """
    playlist_response = youtube.playlists().list(
        part='snippet',
        id=playlist_id
    ).execute()

    playlist_data = playlist_response['items'][0]['snippet']
    published_at = playlist_data['publishedAt']
    title = playlist_data['title']

    videos_id = []
    next_page_token = None
    max_results = 1

    playlist_items_response = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=max_results,
        pageToken=next_page_token
    ).execute()

    while 'nextPageToken' in playlist_items_response:
        for item in playlist_items_response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            videos_id.append({'id': video_id, 'title': video_title})

        next_page_token = playlist_items_response['nextPageToken']

        playlist_items_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=max_results,
            pageToken=next_page_token
        ).execute()

    return published_at, title, videos_id


def get_channel_video_ids(ch_id):
    """
    Retrieves the video IDs, published dates, and titles of all videos uploaded to a YouTube channel.

    Args:
        ch_id (str): The ID of the YouTube channel.

    Returns:
        videos (str): he ID of the YouTube video
        videosPublishedAt (datetime): video published dates
        videos_title: The title of the video.
    """
    playlist_response = youtube.channels().list(
        part='contentDetails',
        id=ch_id
    ).execute()

    playlist_id = playlist_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    videosPublishedAt = []
    videos_title = []
    next_page_token = None
    while True:
        playlist_items_response = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=1,  # Максимальное количество видео на одной странице
            pageToken=next_page_token
        ).execute()

        # Извлечение идентификаторов видео
        for item in playlist_items_response['items']:
            response = youtube.videos().list(
                part='snippet',
                id=item['contentDetails']['videoId']
            ).execute()
            videos.append(item['contentDetails']['videoId'])
            videosPublishedAt.append(item['contentDetails']['videoPublishedAt'])
            videos_title.append(response['items'][0]['snippet']['title'])
        next_page_token = playlist_items_response.get('nextPageToken')

        if not next_page_token:
            break

        if 0 < len(videos) < 2:
            break

    return videos, videosPublishedAt, videos_title


def parse_video(video_id):
    """
    Retrieves various details of a YouTube video.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        video_id (str): The ID of the YouTube video.
        video_url (str): The URL of the YouTube video.
        sub_time_code (list or str): The subtitles of the video, represented as a list of subtitle dictionaries with 'start', 'duration', and 'text' keys. If the video has no subtitles, it will be set to "the video has no subtitles".
        video_tag (list): The tags associated with the video.
        published_at (str): The published date of the video.
        video_title (str): The title of the video.
        video_description (str): The description of the video.
    """
    path_sub_file = []
    response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()
    video_tag = response['items'][0]['snippet']['tags']
    published_at = response['items'][0]['snippet']['publishedAt']
    video_url = url_by_id(video_id)
    video_title = response['items'][0]['snippet']['title']
    video_description = response['items'][0]['snippet']['description']
    channelId = response['items'][0]['snippet']['channelId']
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['ru', 'en'])
        sub_time_code = []
        path = f'sub/{channelId}/{published_at}/{video_id}'
        save_file_with_directory(path)
        with open(f"{path}.txt", "w") as f:
            for t in transcript.fetch():
                sub = dict({'start': t['start'],
                            'duration': t['duration'],
                            'text': t['text']})
                f.write("{}\n".format(sub))
                sub_time_code.append(sub)
                path_sub_file.append(str(f"path: sub/{video_title}.txt"))
    except:
        sub_time_code = str("the video has't subtitles")
        path_sub_file.append(str("the video has't subtitles"))
    return video_id, video_url, sub_time_code, video_tag, published_at, video_title, video_description


def test_parse():
    """
    Parses the channel data and retrieves video details for each channel.

    Returns:
        DataFrame: A pandas DataFrame containing the parsed data for each channel. The DataFrame includes columns for channel ID, channel name, channel description, and channel published date.
        Video (mp4): [Downloaded a YouTube video](Downloads_video.md) on system by path video/channel_id/video_published/video_id.
        Subtitle (txt): Downloaded a Subtitles with timecode on system by path sub/channel_id/video_published/video_id.
        Data (excel): all information's of channel
    """
    df = channel_df()
    for n, ch_id in enumerate(df['id'], start=1):
        videos_id, videosPublishedAt, videos_title = get_channel_video_ids(ch_id)
        video_urls = []
        video_ids = [np.NaN]
        video_titles = [np.NaN]
        video_descriptions = [np.NaN]
        video_sub = [np.NaN]
        video_tags = [np.NaN]
        video_published = [np.NaN]
        # video_updated = [np.NaN]
        for video_id in videos_id:
            dowloand_video(video_id)
            video_id, \
                video_url, \
                sub_time_code, \
                video_tag, \
                published_at, \
                video_title, \
                video_description = parse_video(video_id)
            video_sub.append(sub_time_code)
            video_tags.append(video_tag)
            video_published.append(published_at)
            video_ids.append(video_id)
            video_urls.append(video_url)
            video_titles.append(video_title)
            video_descriptions.append(video_description)

        u_video = pd.DataFrame({'video_urls': video_urls})
        df1 = df[n - 1:n]
        df_v = pd.concat([df1.iloc[:n + 1], u_video, df1.iloc[n + 1:]]).reset_index(drop=True)
        df_v['video_id'] = video_ids
        df_v['video_titles'] = video_titles
        df_v['video_descriptions'] = video_descriptions
        df_v['video_sub'] = video_sub
        df_v['video_tags'] = video_tags
        df_v['video_published'] = video_published
        # df_v['video_updated'] = video_updated
        df_v.to_excel(f'data{ch_id}.xlsx')
        return df_v


def main():
    """
    This function executes the data parsing and saving process.
    It checks if data files already exist for the provided channel IDs and skips those channels.
    For each channel ID, it calls the test_parse() function to parse and save the data.
    The data is saved in an Excel file with the format 'data{channel_id}.xlsx'.
    """
    for c_id in channel_id:
        output_file = f'data{c_id}.xlsx'

        if os.path.exists(output_file):
            print('Data file already exists. Exiting...')
            return
        df = test_parse()
        df.to_excel(f'data{c_id}.xlsx')
        print('Data saved successfully.')


if __name__ == '__main__':
    main()
