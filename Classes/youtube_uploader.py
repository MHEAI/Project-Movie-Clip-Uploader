from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL
import yt_dlp
import os
class YoutubeUploader:
    def __init__(self,folder_name="Movie Clips"):
        self.folder_name = folder_name
        os.makedirs(self.folder_name,exist_ok=True)
        self.output_path = os.path.join(self.folder_name, "%(title)s.%(ext)s")
        
    def extract_playlist(self,playlist_url):
        ydl_opts = {
            "quiet" : True,
            "extract_flat" : True,
            "ignoreerrors": True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url,download=False)
        return info
        
    def download_video(self,url):
        try:
            ydl_opts = {
                'format':"bestvideo+bestaudio/best",
                'merge_output_format':'mp4',
                'outtmpl': self.output_path
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        except DownloadError as e :
            print(f"Download Error {e}")
            raise e
        except Exception as e:
            print(f"Other error: {e}")
            
            