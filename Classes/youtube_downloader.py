import os
import logging

import yt_dlp
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class YoutubeDownloader:
    def __init__(self, folder_name="Movie Clips"):
        self.folder_name = folder_name
        os.makedirs(self.folder_name, exist_ok=True)
        self.output_path = os.path.join(self.folder_name, "%(title)s.%(ext)s")

    def download_video(self, url):
        try:
            ydl_opts = {
                'format': "bestvideo+bestaudio/best",
                'merge_output_format': 'mp4',
                'outtmpl': self.output_path,
                'extractor_args': {
                    'youtube': ['formats=missing_pot']
                },
                'cookies' : r'C:\Users\dell\Desktop\Coding\TOP SECRET PROJECTS\Project Movie Clip Uploader\www.youtube.com.cookies.json',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android']
                    }
    }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        except DownloadError as e:
            logging.error(f"Download Error {e}")
            raise e
        except Exception as e:
            logging.error(f"Other error: {e}")

    def extract_playlist(self, playlist_url):
        ydl_opts = {
            "quiet": True,
            "ignoreerrors": True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

        if info.get("_type") == "playlist":
            return info
        else:
            return {"entries": [info]}

    def get_time(self):
        pass

    def is_duration_valid(self, video):
        """Returns whether the duration is viable for downloading"""
        duration = video.get('duration')
        if duration is None:
            logging.info("No duration info")
            return False
        if duration >= 60:
            logging.info("Too long")
            return False
        return True

    def extract_video_info(self, video_url):
        with YoutubeDL({"quiet": True}) as ydl:
            return ydl.extract_info(video_url, download=False)
