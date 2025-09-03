import random
import logging
from faster_whisper import WhisperModel
from yt_dlp.utils import sanitize_filename
import ffmpeg
from pathlib import Path
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SubtitleHandler:
    def __init__(self):
        self.model = WhisperModel("tiny")

    def transcribe(self, audio):
        logging.info(f"Transcribing {audio}")
        try:
            segments, info = self.model.transcribe(audio, word_timestamps=True)
        except Exception as e:
            logging.error(f"Error while transcribing {e}")
            return None, None

        language = info.language
        if isinstance(language, list):
            language = language[0]
        logging.info(f"Transcription Language : {language}")

        segments = list(segments)
        for seg in segments:
            logging.debug(f"[{seg.start:.2f}s -> {seg.end:.2f}s] {seg.text}")
        return language, segments

    def generate_ass(self, segments, language):
        def format_ass_time(seconds):
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            seconds = seconds % 60
            return f"{hours}:{minutes:02d}:{seconds:05.2f}"

        if isinstance(language, list):
            language = language[0]

        ass_file = f"{sanitize_filename(language)}_{random.randint(1000,9999)}.ass"
        with open(ass_file, "w", encoding="utf-8") as f:
            # Header
            f.write("[Script Info]\n")
            f.write("PlayResX: 1080\n")
            f.write("PlayResY: 1920\n\n")

            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                    "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
  
            f.write("Style: Default,Arial,70,&H00FFFFFF,&H00FFFF00&,&H00000000,1,2,0,5,50,50,100,1\n\n")

            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

            # Subtitles
            for seg in segments:
                start = format_ass_time(seg.start)
                end = format_ass_time(seg.end)

                if seg.words:  # karaoke effect
                    karaoke_line = ""
                    for w in seg.words:
                        dur_cs = int((w.end - w.start) * 100)  # centiseconds
                        karaoke_line += f"{{\\k{dur_cs}}}{w.word.strip()} "
                else:
                    karaoke_line = seg.text

                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{karaoke_line.strip()}\n")

        logging.info(f"ASS saved: {ass_file}")
        return ass_file


def burn_subtitles(video, subtitle_file, language):
    logging.info("Burning subtitles into video")
    video_input_stream = ffmpeg.input(video)
    video_name = Path(video).stem
    output_video = f"{video_name}_subbed.mp4"
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


# Example usage
# s = SubtitleHandler()
# language, segments = s.transcribe("video.opus")
# if segments:
#     ass_file = s.generate_ass(segments, language)
#     burn_subtitles("video.mp4", ass_file, language)
