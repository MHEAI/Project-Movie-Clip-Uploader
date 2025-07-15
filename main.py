import logging
from flask import Flask, render_template, request, jsonify
import asyncio

from Classes.movie_handler import MovieHandler
from Classes.subtitle_handler import SubtitleHandler
from Classes.title_cleaner import TitleCleaner
from Classes.uploader import Uploader
from Classes.utils import Utilities
from Classes.video_editor import VideoEditor
from Classes.youtube_downloader import YoutubeDownloader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 * 1024

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST', 'GET'])
def process_form():
    option = request.form.get('option')
    amount_of_vids = int(request.form.get("videoCount"))
    if option == 'playlist':
        playlist_url  = request.form.get("playlistUrl")
        id_list = main(playlist_url, amount_of_vids, "playlist")
    elif option == 'upload':
        logging.info(f"Amount of vids requested: {amount_of_vids}")
        movie = request.files.get("movieFile")
        movie.save("movie.mp4")
        logging.info(f"Uploaded movie file: {movie}")
        id_list = main(type="movie", movie="movie.mp4", max_vids=amount_of_vids)
        
    return jsonify({"message": ("Uploaded videos with the id's of: ", id_list), "success": True})

def main(playlist=None, max_vids=0, type=None, movie=None):
    downloader = YoutubeDownloader()
    title_cleaner = TitleCleaner()
    editor = VideoEditor()
    subtitler = SubtitleHandler()
    uploader = Uploader()
    utilizer = Utilities()
    moviehandler = MovieHandler()
    id_list = []

    if type == "playlist":
        info = downloader.extract_playlist(playlist)
        for i, video in enumerate(info['entries']):
            if i > max_vids:
                break
            if not video:
                continue

            try:
                video = downloader.extract_video_info(video["webpage_url"])
            except Exception as e:
                logging.warning(f"Skipped video because it could not be fetched: {e}")
                continue

            if (
                video.get("availability") == "private"
                or video.get("is_private")
                or video.get("availability") == "unavailable"
            ):
                logging.info(f"Skipped {video.get('id')} because it is private or unavailable")
                continue

            title = title_cleaner.clean_and_summarize_title(video.get("title"))
            video_file = downloader.download_video(video["webpage_url"])
            logging.info(f"Download returned: {video_file}")

            clipped_file = editor.clip_video(video_file)
            if clipped_file is None:
                logging.warning("Skipping because clip_video failed.")
                continue

            portrait_clipped_file = editor.convert_to_portrait(clipped_file)
            audio_file = editor.extract_audio(portrait_clipped_file)

            language, segments = subtitler.transcribe(audio_file)
            srt_file = subtitler.generate_srt(segments, language)
            ass_file = subtitler.convert_to_ass(srt_file)

            subbed_video = editor.burn_subtitles(portrait_clipped_file, ass_file, language)
            id_list.append(uploader.upload_to_youtube(subbed_video, title))

            utilizer.cleanup_files([
                video_file,
                clipped_file,
                portrait_clipped_file,
                subbed_video,
                audio_file,
                srt_file,
                ass_file
            ])
        return id_list

    elif type == "movie":
        logging.info("Analyzing movie")
        audio_file = editor.extract_audio(movie)

        language, segments = subtitler.transcribe(audio_file)
        srt_file = subtitler.generate_srt(segments, language)

        time_stamps = asyncio.run(moviehandler.find_most_interesting_scene_async(srt_file))


        paths = moviehandler.clip_video(movie, time_stamps, max_vids)
        utilizer.cleanup_files([
            audio_file,
            srt_file,
            time_stamps
        ])
        for path in paths:
            portrait_clipped_file = editor.convert_to_portrait(path)
            audio_file = editor.extract_audio(path)

            language, segments = subtitler.transcribe(audio_file)
            srt_file = subtitler.generate_srt(segments, language)
            ass_file = subtitler.convert_to_ass(srt_file)

            subbed_video = editor.burn_subtitles(portrait_clipped_file, ass_file, language)

            id_list.append(uploader.upload_to_youtube(
                subbed_video,
                r"#ShortFilm #MovieClip #EpicMoment #FilmLovers #Cinematic #DramaScene #MustWatch #Shorts #Viral"
            ))
            utilizer.cleanup_files([
                portrait_clipped_file,
                audio_file,
                srt_file,
                ass_file,
                subbed_video
            ])

        return id_list

if __name__ == "__main__":
    app.run(debug=True)
