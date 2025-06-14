from faster_whisper import WhisperModel
import time
import math
import ffmpeg
import yt_dlp
from yt_dlp import YoutubeDL
import os
from yt_dlp.utils import sanitize_filename
from faster_whisper import WhisperModel

import srt
def convert_to_ass(srt_file, ass_file):
    with open(srt_file, 'r') as f:
        subtitles = list(srt.parse(f.read()))
    with open(ass_file,"w") as f:
        f.write("[Script Info]\n\n[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        f.write("Style: Default,Arial,40,&H0000FF&, &H000000&,1,1,0,2,10,10,10,1\n\n")

        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

        for sub in subtitles:
            start = str(sub.start).replace(',', '.')[:-3]
            end = str(sub.end).replace(',', '.')[:-3]
            text = "{\\c&H0000FF&}" + sub.content.replace('\n', '\\N')
            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
        return ass_file
        
        
        
        
def download_and_upload(playlist):
    
    folder_name = "Movie Clips"
    os.makedirs(folder_name, exist_ok=True)
    output_path = os.path.join(folder_name, '%(title)s.%(ext)s')
    
    def download_audio_and_video(link):
        
        """Downloads Youtube Video as Opus file for audio and Mp4 for video"""
        with yt_dlp.YoutubeDL({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': output_path
        }) as ydl:
            info = ydl.extract_info(link, download=True)
            base_title = sanitize_filename(info['title'])
            video_file = os.path.join(folder_name,f"{base_title}.mp4")

        audio_file = os.path.join(folder_name,f"{base_title}.opus")
        ffmpeg.input(video_file).output(audio_file, acodec='copy').run(overwrite_output=True)

        return video_file, audio_file
    
    def get_time(info):
        
        """Returns whether the duration is viable for downloading"""
        
        duration = info.get('duration')
        if duration is None:
            return "no duration info"
        if duration >= 180:
            return "duration too long"
        return None
    
    

    

    def format_time(seconds):

        hours = math.floor(seconds / 3600)
        seconds %= 3600
        minutes = math.floor(seconds / 60)
        seconds %= 60
        milliseconds = round((seconds - math.floor(seconds)) * 1000)
        seconds = math.floor(seconds)
        formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

        return formatted_time
    def generate_subtitle_file(language, segments):

        subtitle_file = f"sub--pythonargs.{language}.srt"
        text = ""
        for index, segment in enumerate(segments):
            segment_start = format_time(segment.start)
            segment_end = format_time(segment.end)
            text += f"{str(index+1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment.text} \n"
            text += "\n"
            
        f = open(subtitle_file, "w")
        f.write(text)
        f.close()

        return subtitle_file
    def transcribe(audio):
        model = WhisperModel("tiny")
        segments,info = model.transcribe(audio)
        language = info.language
        print("Transcription Language", info.language)
        segments = list(segments)
        for segment in segments:
            # print(segment)
            print("[%.2fs -> %.2fs] %s"
                % (segment.start, segment.end, segment.text))
        return language, segments


    def add_subtitle_to_video(soft_subtitle, subtitle_file, subtitle_language, video):
        video_input_stream = ffmpeg.input(video)
        vid_name = video.replace(".mp4","")
        output_video = f"{vid_name}_subbed.mp4"
        subtitle_file = convert_to_ass(subtitle_file, ("STYLED" + subtitle_file ))
        subtitle_track_title = subtitle_file.replace(".srt", "")
        try:
            if soft_subtitle:
                stream = (
                    ffmpeg
                    .output(
                        video_input_stream,
                        output_video,
                        vf=f"subtitles='{subtitle_file}'",  
                        **{"c:a": "copy"},
                        **{f"metadata:s:s:0": f"language={subtitle_language}", f"metadata:s:s:0": f"title={subtitle_track_title}"}
                    )
                )
            else:
                stream = ffmpeg.output(
                    video_input_stream,
                    output_video,
                    vf=f"subtitles='{subtitle_file}'"
                )
            ffmpeg.run(stream, overwrite_output=True)
        except ffmpeg.Error as e:
            print("dumbass you did big error")
    def run():
        ydl_opts = {
            'match_filter': get_time,
            'outtmpl':output_path,
            'quiet' : True,
            'playlistend' : 3
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url = playlist,download=False)
            for video in info['entries']:
                id = sanitize_filename(video.get("id"))
                duration = video.get('duration')
                if duration < 180:
                    print("Getting that one")
                    video_path, audio_path = download_audio_and_video(id)
                    language, segments = transcribe(audio=audio_path)
                    subtitle_file = generate_subtitle_file(
                        language=language,
                        segments=segments
                    )
                    add_subtitle_to_video(
                    soft_subtitle=True,
                    subtitle_file=subtitle_file,
                    subtitle_language=language,
                    video = video_path
                    )
                    #Yotube_upload(edited_footage)
                    os.remove(video_path)
                    os.remove(audio_path)
                    os.remove(subtitle_file)
                    
                else:
                    print("Skipped" , video.get('title'))
        
    run()


download_and_upload("https://www.youtube.com/playlist?list=PL86SiVwkw_oeDQoAZwcuyoyG43eKWtbJM")

