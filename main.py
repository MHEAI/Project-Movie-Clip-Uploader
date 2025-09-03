import logging
import argparse

from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask
from Flask_Handler.flask_handler import routes

from Classes.utils import Utilities
from Classes.youtube_downloader import YoutubeDownloader
from Classes.workflows import Workflows


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024
app.register_blueprint(routes)

def main(playlist=None, max_vids=0, type=None, movie=None):
    downloader = YoutubeDownloader()
    utilizer = Utilities()
    workflows = Workflows()


    id_list = []

    if type == "playlist":
        utilizer.cleanup_folder("Movie Clips")
        info = downloader.extract_playlist(playlist)

        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i, video in enumerate(info['entries']):
                if i > max_vids or not video:
                    continue
                futures.append(executor.submit(workflows.process, video))
            for future in as_completed(futures):
                video_id = future.result()
                if video_id:
                    id_list.append(video_id)

    elif type == "movie":
        logging.info("Analyzing movie")

        paths = workflows.edit_movie(movie,max_vids)
        for path in paths:
            video_id = workflows.process(path)
            id_list.append(video_id)

    return id_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("playlist", type=str, nargs="?", help="The playlist URL to be processed")
    parser.add_argument("max_vids",type=int, nargs="?", help="Amount of videos to process")
    args = parser.parse_args()

    if args.playlist:
        main(playlist=args.playlist, max_vids=args.max_vids or 2, type="playlist")
    else:
        app.run(debug=True)
