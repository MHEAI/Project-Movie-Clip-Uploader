from Classes.movie_handler import MovieHandler
from Classes.subtitle_handler import SubtitleHandler
from Classes.title_cleaner import TitleCleaner
from Classes.uploader import Uploader
from Classes.utils import Utilities
from Classes.video_editor import VideoEditor
from Classes.youtube_downloader import YoutubeDownloader
from Classes.movie_handler import MovieHandler

import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio
class Workflows:
    def __init__(self):
        self.downloader = YoutubeDownloader()
        self.title_cleaner = TitleCleaner()
        self.utilizer = Utilities()
        self.editor = VideoEditor()
        self.subtitler = SubtitleHandler()
        self.uploader = Uploader()
        self.utilizer = Utilities()
        self.moviehandler = MovieHandler()
    def edit_movie(self,movie,max_vids):
        audio_file = self.editor.extract_audio(movie)
        language, segments = self.subtitler.transcribe(audio_file)
        srt_file = self.subtitler.generate_srt(segments, language)

        time_stamps = asyncio.run(self.moviehandler.find_most_interesting_scene_async(srt_file))
        self.utilizer.cleanup_files([audio_file, srt_file])

        paths = self.moviehandler.clip_video(movie, time_stamps, max_vids)
        
        return paths
    def edit_and_upload(self,file_path, title=None):
        editor = VideoEditor()
        subtitler = SubtitleHandler()
        uploader = Uploader()
        utilizer = Utilities()

        with ThreadPoolExecutor() as executor:
            future_clipped_file = executor.submit(editor.convert_to_portrait, file_path)
            future_audio_file = executor.submit(editor.extract_audio, file_path)

            portrait_clipped_file = future_clipped_file.result()
            audio_file = future_audio_file.result()

        language, segments = subtitler.transcribe(audio_file)
        srt_file = subtitler.generate_srt(segments, language)
        ass_file = subtitler.convert_to_ass(srt_file)

        subbed_video = editor.burn_subtitles(portrait_clipped_file, ass_file, language)

        if title is None:
            title = r"#ShortFilm #MovieClip #EpicMoment #FilmLovers #Cinematic #DramaScene #MustWatch #Shorts #Viral"

        with ThreadPoolExecutor() as executor:
            future_youtube = executor.submit(uploader.upload_to_youtube, subbed_video, title)
            future_tiktok = executor.submit(uploader.upload_to_tiktok, subbed_video)
            video_id = future_youtube.result()
            future_tiktok.result()
        utilizer.cleanup_files([file_path,
                                            portrait_clipped_file,
                                            audio_file,
                                            srt_file,
                                            ass_file,
                                            subbed_video])
        if video_id:
            return video_id
    def process(self,video):
        try: 
            video_info = self.downloader.extract_video_info(video["webpage_url"])
        except Exception as e:
            logging.warning(f"Skipped video because it could not be fetched: {e}")
            return None
        if video_info.get("availability") in ("private", "unavailable") or video_info.get("is_private"):
            logging.info(f"Skipped {video_info.get('id')} because it is private or unavailable")
            return None

        title = self.title_cleaner.clean_and_summarize_title(video_info.get("title"))
        video_file = self.downloader.download_video(video_info["webpage_url"])
        logging.info(f"Downloaded: {video_file}")

        clipped_file = VideoEditor().clip_video(video_file, video_info["duration"])
        if clipped_file is None:
            logging.warning("Skipping because clip_video failed.")
            return None

        video_id = self.edit_and_upload(clipped_file, title)
        self.utilizer.cleanup_files([video_file])
        return video_id