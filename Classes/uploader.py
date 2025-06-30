from yt_dlp.utils import DownloadError
import yt_dlp
import os
from subprocess import run
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
        
        command = ["python","upload_video.py","--file",file,"--title",title,"--description",description,"--keywords",keyword_string,"--category","24"]
        run(command)        
            