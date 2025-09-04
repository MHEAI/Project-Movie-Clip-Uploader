from flask import Blueprint, render_template, request, jsonify
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from Classes.utils import Utilities
from Classes.youtube_downloader import YoutubeDownloader
from Classes.workflows import Workflows

routes = Blueprint("routes", __name__)
@routes.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
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
@routes.route('/process', methods=['POST', 'GET'])
def process_form():
    option = request.form.get('option')
    amount_of_vids = int(request.form.get("videoCount"))

    if option == 'playlist':
        playlist_url = request.form.get("playlistUrl")
        id_list = main(playlist=playlist_url, max_vids=amount_of_vids, type="playlist")
    elif option == 'upload':
        logging.info(f"Amount of vids requested: {amount_of_vids}")
        movie = request.files.get("movieFile")
        movie.save("movie.mp4")
        logging.info(f"Uploaded movie file: {movie}")
        id_list = main(type="movie", movie="movie.mp4", max_vids=amount_of_vids)
    else:
        return jsonify({"message": "Invalid option", "success": False})

    return jsonify({"message": ("Uploaded videos with the id's of: ", id_list), "success": True})
