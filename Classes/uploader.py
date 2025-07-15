import os
from subprocess import run

import yt_dlp
from yt_dlp.utils import DownloadError

class Uploader:
    def __init__(self):
        pass
    
    def upload_to_youtube(self,file,title):
        description = (r"""🔥 Watch more amazing movie moments every day! 🔥
    Catch the coolest scenes, epic fights, and unforgettable moments from your favorite films.

    🎬 Don’t forget to Subscribe for daily Shorts!
    👇 Check out more clips here: MovieBytes

    #Shorts #MovieClips #EpicScenes #MustWatch #FilmLovers""")
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
        keyword_string = ",".join(keywords)
        print("Uploading file....")
        command = ["python","upload_video.py","--file",file,"--title",title,"--description",description,"--keywords",keyword_string,"--category","24"]
        try:
            result = run(command, capture_output=True, text=True, check=True)
        except Exception as e:
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            print("RETURN CODE:", e.returncode)
            raise

        output = result.stdout
        id = output.split("Uploaded video with id: ")[1].strip()
        return id
            