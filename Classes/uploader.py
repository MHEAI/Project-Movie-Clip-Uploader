import os
import logging
import subprocess
from tiktok_uploader.upload import upload_video

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Uploader:
    def __init__(self):
        self.description = r""" Watch more amazing movie moments every day! 
Catch the coolest scenes, epic fights, and unforgettable moments from your favorite films.

 Don’t forget to Subscribe for daily Shorts!
 Check out more clips here: MovieBytes

#Shorts #MovieClips #EpicScenes #MustWatch #FilmLovers"""

    def upload_to_youtube(self, file, title):
        keywords = [
            "movie clips", "movie scenes", "epic scenes", "funny movie clips",
            "action scenes", "classic movie moments", "must watch", "viral",
            "trending", "best of", "top moments", "unbelievable", "new release",
            "behind the scenes", "exclusive clip"
        ]
        keyword_string = ",".join(keywords)

        logging.info(f"Uploading file({file}) to YouTube...")
        command = [
            "python", "upload_video.py",
            "--file", file,
            "--title", title,
            "--description", self.description,
            "--keywords", keyword_string,
            "--category", "24"
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            video_id = result.stdout.strip()
            if video_id and not video_id.startswith("ERROR"):
                return video_id
            else:
                logging.error(f"Upload succeeded but no video ID returned. Output: {result.stdout}")
                return None
        except subprocess.CalledProcessError as e:
            logging.error("Upload failed")
            logging.error(f"Return code: {e.returncode}")
            logging.error(f"STDOUT: {e.stdout}")
            logging.error(f"STDERR: {e.stderr}")
            raise

    def upload_to_tiktok(self, file, title):
        safe_text = ''.join(c for c in title if ord(c) <= 0xFFFF)
        logging.info(f"Uploading file({file}) to TikTok...")
        try:
            upload_video(
                filename=file,
                description= title + self.description,
                sessionid=os.getenv("SESSION_ID")
            )
        except Exception as e:
            logging.error(f"Error while uploading to TikTok: {e}")
            
