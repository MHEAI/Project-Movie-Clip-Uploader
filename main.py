from flask import Flask, render_template, request

from Classes.youtube_downloader import YoutubeDownloader 
from Classes.title_cleaner import TitleCleaner
from Classes.video_editor import VideoEditor
from Classes.subtitle_handler import SubtitleHandler
from Classes.uploader import Uploader
from Classes.utils import Utilities

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    playlist = None
    if request.method == 'POST':
        playlist = request.form['playlist_name']
        main(playlist)
    return render_template('index.html', playlist_name=playlist)

def main(playlist):

    downloader = YoutubeDownloader()
    title_cleaner = TitleCleaner()
    editor = VideoEditor()
    subtitler = SubtitleHandler()
    uploader = Uploader()
    utilizer = Utilities()

    info = downloader.extract_playlist(playlist)

    for video in info['entries']:
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

if __name__ == "__main__":
    app.run(debug=True)
