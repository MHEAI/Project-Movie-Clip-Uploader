from flask import Flask, render_template, request, flash,redirect,url_for,jsonify
from time import sleep
from Classes.youtube_downloader import YoutubeDownloader 
from Classes.title_cleaner import TitleCleaner
from Classes.video_editor import VideoEditor
from Classes.subtitle_handler import SubtitleHandler
from Classes.uploader import Uploader
from Classes.utils import Utilities

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process', methods = ['POST','GET'])
def process_form():
    option = request.form.get('option')
    
    if option == 'playlist':
        playlist_url  = request.form.get("playlistUrl")
        amount_of_vids = int(request.form.get("videoCount"))
        print(amount_of_vids)
        video_file = main(playlist_url,amount_of_vids)
    
    elif option == 'upload':
        movie_file = request.files.get('movieFile')
        
        print(f"Acting like i am processing the file as the func has not been created yet: {movie_file}")
    return jsonify({"message": "", "success": True})
    
        

def main(playlist,max_vids):

    downloader = YoutubeDownloader()
    title_cleaner = TitleCleaner()
    editor = VideoEditor()
    subtitler = SubtitleHandler()
    uploader = Uploader()
    utilizer = Utilities()

    info = downloader.extract_playlist(playlist)
    
    for i,video in enumerate(info['entries']):
        if i > max_vids:
            break
        if not video:
            continue

        try:
            video = downloader.extract_video_info(video["webpage_url"])
        except Exception as e:
            print(f"Skipped video because it could not be fetched: {e}")
            continue

        if (
            video.get("availability") == "private"
            or video.get("is_private")
            or video.get("availability") == "unavailable"
        ):
            print(f"Skipped {video.get('id')} because it is private or unavailable")
            continue

        title = title_cleaner.clean_and_summarize_title(video.get("title"))
        video_file = downloader.download_video(video["webpage_url"])
        print("Download returned:", video_file)

        clipped_file = editor.clip_video(video_file)
        if clipped_file is None:
            print("Skipping because clip_video failed.")
            continue

        portrait_clipped_file = editor.convert_to_portrait(clipped_file)
        audio_file = editor.extract_audio(portrait_clipped_file)

        language, segments = subtitler.transcribe(audio_file)
        srt_file = subtitler.generate_srt(segments, language)
        ass_file = subtitler.convert_to_ass(srt_file)

        subbed_video = editor.burn_subtitles(portrait_clipped_file, ass_file, language)
        uploader.upload_to_youtube(subbed_video, title)

        utilizer.cleanup_files([
            video_file,
            clipped_file,
            portrait_clipped_file,
            subbed_video,
            audio_file,
            srt_file,
            ass_file
        ])
        return video_file
if __name__ == "__main__":
    app.run(debug=True) 