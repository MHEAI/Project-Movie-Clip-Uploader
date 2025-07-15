
from faster_whisper import WhisperModel
import math
import random
from yt_dlp.utils import sanitize_filename
import srt
def transcribe(audio):
        print("Transcribing")
        model = WhisperModel("tiny")
        try:
            segments,info = model.transcribe(audio)
        except Exception as e:
            print(f"Error while transcribing {e}")
            
        language = info.language
        if isinstance(language, list):
            language = language[0]  
        print("Transcription Language",language)
        segments = list(segments)
        for segment in segments:
            print("[%.2fs -> %.2fs] %s"
                % (segment.start, segment.end, segment.text))
        return language[0], segments
def generate_srt(segments,language):
        def format_time(seconds):

            hours = math.floor(seconds / 3600)
            seconds %= 3600
            minutes = math.floor(seconds / 60)
            seconds %= 60
            milliseconds = round((seconds - math.floor(seconds)) * 1000)
            seconds = math.floor(seconds)
            formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

            return formatted_time
        print("Generating SRT File")
        print("DEBUG: language type:", type(language), "value:", language)
        if isinstance(language, list):
            language = language[0]
        subtitle_file =  f"{sanitize_filename(language)}_{random.randint(1000,9999)}.srt"
        text = ""
        for index, segment in enumerate(segments):
            segment_start = format_time(segment.start)
            segment_end = format_time(segment.end)
            text += f"{str(index+1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment.text} \n"
            text += "\n"
            
        with open(subtitle_file,"w", encoding="utf-8") as f:
            f.write(text)

        return subtitle_file
if __name__ == "__main__":
    lang,segments  =  transcribe("Interstellar.opus")
    generate_srt(segments,lang)