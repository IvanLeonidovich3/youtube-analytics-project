import os
from datetime import timedelta

import isodate
from googleapiclient.discovery import build


class PlayList:
    api_key: str = os.getenv('API_Key')
    youtube = build('youtube', 'v3', developerKey=api_key)

    def __init__(self, playlist_id):
        self.playlist_id = playlist_id
        playlist_videos = self.youtube.playlistItems().list(playlistId=playlist_id,
                                                            part='contentDetails,snippet',
                                                            maxResults=50, ).execute()
        self.title = playlist_videos['items'][0]['snippet']['title']

        self.url = f"https://www.youtube.com/playlist?list={self.playlist_id}"
        self.duration = playlist_videos

    # def __str__(self):
    #     return self.title

    @property
    def total_duration(self) -> timedelta:
        """
        Возвращает объект класса datatime.timedelta с суммарной длительностью плэйлиста
        """

        playlist_videos = self.youtube.playlistItems().list(playlistId=self.playlist_id,
                                                            part='contentDetails',
                                                            maxResults=50,
                                                            ).execute()
        video_ids: list[str] = [video['contentDetails']['videoId'] for video in playlist_videos['items']]
        video_response = self.youtube.videos().list(part='contentDetails,statistics',
                                                    id=','.join(video_ids)
                                                    ).execute()

        total: timedelta = timedelta(hours=0, minutes=0)
        for video in video_response['items']:
            iso_8601_duration = video['contentDetails']['duration']
            duration = isodate.parse_duration(iso_8601_duration)
            total += duration

        return total

    def show_best_video(self):
        """
        Возвращает ссылку на популярное видео из плэйлиста (по количеству лайков)
        """
        playlist_videos = self.youtube.playlistItems().list(playlistId=self.playlist_id,
                                                            part='contentDetails',
                                                            maxResults=50,
                                                            ).execute()
        video_ids: list[str] = [video['contentDetails']['videoId'] for video in playlist_videos['items']]
        video_response = self.youtube.videos().list(part='contentDetails,statistics',
                                                    id=','.join(video_ids)
                                                    ).execute()

        max_like_count = 0

        for video in video_response['items']:
            if max_like_count < int(video['statistics']['likeCount']):
                max_like_count = int(video['statistics']['likeCount'])
                url = f"https://youtu.be/{video['id']}"
        return url
