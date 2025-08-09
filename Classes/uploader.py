import os
from subprocess import run
import logging

import yt_dlp
from yt_dlp.utils import DownloadError



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Uploader:
    def __init__(self):
        pass

    def _get_description(self):
        return (r"""🔥 Watch more amazing movie moments every day! 🔥
Catch the coolest scenes, epic fights, and unforgettable moments from your favorite films.

🎬 Don’t forget to Subscribe for daily Shorts!
👇 Check out more clips here: MovieBytes

#Shorts #MovieClips #EpicScenes #MustWatch #FilmLovers""")

    def _get_keywords(self):
        keywords = [
            "movie clips",
            "movie scenes",
            "epic scenes",
            "funny movie clips",
            "action scenes",
            "classic movie moments",
            "must watch",
            "viral",
            "trending",
            "best of",
            "top moments",
            "unbelievable",
            "new release",
            "behind the scenes",
            "exclusive clip"
        ]
        return ",".join(keywords)

    def _build_command(self, file, title, description, keyword_string):
        return [
            "python", "upload_video.py",
            "--file", file,
            "--title", title,
            "--description", description,
            "--keywords", keyword_string,
            "--category", "24"
        ]

    def _run_upload_command(self, command):
        try:
            result = run(command, capture_output=True, text=True, check=True)
        except Exception as e:
            logging.error("Upload failed")
            logging.error("STDOUT: %s", getattr(e, 'stdout', ''))
            logging.error("STDERR: %s", getattr(e, 'stderr', ''))
            logging.error("RETURN CODE: %s", getattr(e, 'returncode', ''))
            raise
        return result.stdout

    def _extract_video_id(self, output):
        return output.split("Uploaded video with id: ")[1].strip()

    def upload_to_youtube(self, file, title):
        description = self._get_description()
        keyword_string = self._get_keywords()

        logging.info(f"Uploading file({file}) to youtube....")
        command = self._build_command(file, title, description, keyword_string)
        output = self._run_upload_command(command)
        video_id = self._extract_video_id(output)
        return video_id
