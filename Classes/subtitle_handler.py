from faster_whisper import WhisperModel
import math
import random
from yt_dlp.utils import sanitize_filename
import srt
from pydub import AudioSegment
import os
from io import BytesIO
class SubtitleHandler:
    def __init__(self):
        self.model = WhisperModel("tiny")
    def transcribe(self,audio):
        print("Transcribing")
        try:
            segments,info = self.model.transcribe(audio)
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

    def generate_srt(self,segments,language):
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
    
    def convert_to_ass(self, srt_file):
        
        def srt_to_ass_time(srt_time):
            # srt_time is a datetime.timedelta object from the srt library
            total_seconds = srt_time.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = int(total_seconds % 60)
            milliseconds = int(round((total_seconds - int(total_seconds)) * 1000))
            centiseconds = int(round(milliseconds / 10))
            return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
        
        print("Converting SRT File To ass")
        ass_file = "STYLED" + srt_file
        with open(srt_file,"r", encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))
        with open(ass_file, "w", encoding="utf-8") as f:
            f.write("[Script Info]\n")
            f.write("PlayResX: 1080\n")
            f.write("PlayResY: 1920\n\n")
            
            f.write("[V4+ Styles]\n")
            f.write("Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
            f.write("Style: Default,Arial,70,&H00FFFFFF,&H00000000,1,1,0,5,50,50,100,3\n\n")
            
            f.write("[Events]\n")
            f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

            for sub in subtitles:
                start = srt_to_ass_time(sub.start)
                end = srt_to_ass_time(sub.end)
                text = sub.content.replace('\n', '\\N')
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

        return ass_file