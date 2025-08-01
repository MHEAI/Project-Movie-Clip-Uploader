from pathlib import Path
from subprocess import run
import logging
import random

import ffmpeg
from moviepy.video.io.VideoFileClip import VideoFileClip


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VideoEditor:
    def __init__(self):
        pass

    def clip_video(self, video,length):
        try:
            with VideoFileClip(video) as clip:
                start = random.randint(0,length)
                subclip = clip.subclipped(start, start+60)  # fixed typo: subclipped -> subclip
                p = Path(video)
                output_path = str(p.with_name(p.stem + "_clipped" + p.suffix))
                if Path(output_path).exists():
                    Path(output_path).unlink()
                subclip.write_videofile(
                    output_path, 
                    codec="libx264", 
                    audio_codec="aac",
                    ffmpeg_params=["-nostdin"]
                )
            return output_path
        except Exception as e:
            logging.error(f"Error while clipping video: {e}")
            return None

    def extract_audio(self, video_path):
        p = Path(video_path)
        audio_file = str(p.with_name(p.stem + ".opus"))
        ffmpeg.input(video_path).output(
            audio_file,
            acodec="libopus"
        ).run(overwrite_output=True)
        return audio_file

    def convert_to_portrait(self, video_file):
        p = Path(video_file)
        output_path = str(p.with_name(p.stem + "_portrait" + p.suffix))
        command = [
            "ffmpeg",
            "-i", video_file,
            "-vf", "crop=ih*9/16:ih,scale=1080:1920",
            "-c:a", "copy",
            output_path
        ]
        run(command)
        return output_path

    def burn_subtitles(self, video, subtitle_file, language):
        logging.info("Burning subtitle into video")
        video_input_stream = ffmpeg.input(video)
        video_name = video.replace(".mp4", "")
        output_video = f"{video_name}_subbed.mp4"
        subtitle_track_title = subtitle_file.replace(".srt", "")
        try:
            stream = ffmpeg.output(
                video_input_stream,
                output_video,
                vf=f"subtitles='{subtitle_file}'"
            )
            ffmpeg.run(stream, overwrite_output=True)
        except ffmpeg.Error as e:
            logging.error(f"Error while burning in subtitles: {e}")

        return output_video
