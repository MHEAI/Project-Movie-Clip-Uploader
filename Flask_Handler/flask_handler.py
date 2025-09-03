from flask import Blueprint, render_template, request, jsonify
import logging
from main import main  # import the function from main.py

routes = Blueprint("routes", __name__)
@routes.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

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
