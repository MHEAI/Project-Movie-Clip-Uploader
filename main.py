from faster_whisper import WhisperModel
import time
import math
import ffmpeg
import yt_dlp
from yt_dlp.utils import DownloadError
from yt_dlp import YoutubeDL
import os
from yt_dlp.utils import sanitize_filename
from subprocess import run as r
from pathlib import Path
import srt

from moviepy.video.io.VideoFileClip import VideoFileClip

import re
import random
import requests
import json

def talk_to_bot(prompt_id, title):
    prompts = {
        1: f"""You are a title cleanup tool. Given this movie clip title:

{title}

Perform these steps:

- Remove junk words like "4K", "HD", "Trailer", "Movieclips", etc.
- Remove special characters such as brackets, pipes, colons, and dashes.
- Remove year indicators like "2006" or "2020".
- Normalize whitespace.
- Add a random catchy adjective like "Epic" or "Legendary" plus the word "Scene".
- remove the original thing and Then summarize what this entire process does in a cool, catchy tagline that includes the movie name and the clip's main premise dont over do it.
- Append hashtags: #Shorts #MovieClips   #FilmLovers. to the very end



dont add asterisks



dont make it more than 100 characters

Return only one plain string combining the cleaned title with hashtags and the tagline. No extra explanation or multiple options.

double check the length and make sure it isnt more than 100 characters
"""
    }

    if prompt_id not in prompts:
        raise ValueError(f"Prompt ID {prompt_id} not found in prompt list.")

    prompt = prompts[prompt_id]

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "mistralai/mistral-small-3.2-24b-instruct:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )

    data = response.json()
    if "choices" not in data:
        print("API error:", data)
        return None

    return data["choices"][0]["message"]["content"]

def summarize_title(text, prompt_id=1):
    return talk_to_bot(prompt_id, text)


def upload_to_youtube(file,title):
    description = (r"""🔥 Watch more amazing movie moments every day! 🔥
Catch the coolest scenes, epic fights, and unforgettable moments from your favorite films.

🎬 Don’t forget to Subscribe for daily Shorts!
👇 Check out more clips here: MovieBytes

#Shorts #MovieClips #EpicScenes #MustWatch #FilmLovers""")
    keywords = [
    "movie clips",
    "movie scenes",
    "epic scenes",
    "funny movie clips",
    "action scenes",
    "classic movie moments",
    "must watch",
    "viral",
    "trending",
    "best of",
    "top moments",
    "unbelievable",
    "new release",
    "behind the scenes",
    "exclusive clip"
    ]
    keyword_string = ",".join(keywords)

    command = ["python","upload_video.py","--file",file,"--title",title,"--description",description,"--keywords",keyword_string,"--category","24"]
    r(command)
    
def convert_to_portrait(input_path):
    p = Path(input_path)
    output_path = str(p.with_name(p.stem + "_portrait" + p.suffix))
    command = [
    "ffmpeg",
    "-i", input_path,
    "-vf", "crop=ih*9/16:ih,scale=1080:1920",
    "-c:a", "copy",
    output_path
    ]
    r(command)
    return output_path

def srt_to_ass_time(srt_time):
    # srt_time is a datetime.timedelta object from the srt library
    total_seconds = srt_time.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int(round((total_seconds - int(total_seconds)) * 1000))
    centiseconds = int(round(milliseconds / 10))
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

def convert_to_ass(srt_file, ass_file):
    print("Converting to Ass")
    with open(srt_file, 'r', encoding="utf-8") as f:
        subtitles = list(srt.parse(f.read()))
    with open(ass_file, "w", encoding="utf-8") as f:
        f.write("[Script Info]\n")
        f.write("PlayResX: 1080\n")
        f.write("PlayResY: 1920\n\n")
        
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        f.write("Style: Default,Arial,50,&H00FFFFFF,&H00000000,1,1,0,5,50,50,100,3\n\n")
        
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")

        for sub in subtitles:
            start = srt_to_ass_time(sub.start)
            end = srt_to_ass_time(sub.end)
            text = sub.content.replace('\n', '\\N')
            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

    return ass_file

        
        
        
        
def download_and_upload(playlist):
    
    
    print("Starting Upload")
    folder_name = "Movie Clips"
    os.makedirs(folder_name, exist_ok=True)
    output_path = os.path.join(folder_name, '%(title)s.%(ext)s')
    
    def download_audio_and_video(link):
        print("Downloading")
        """Downloads Youtube Video as Opus file for audio and Mp4 for video"""
        try : 
            with yt_dlp.YoutubeDL({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'outtmpl': output_path
            }) as ydl:
                info = ydl.extract_info(link, download=True)
        except DownloadError as e :
            print(f"Download error {e}" )
            raise e
        except Exception as e:
            print(f"Other error {e}")
            raise e
        base_title = sanitize_filename(info['title'], restricted=True)
        video_file = ydl.prepare_filename(info)

        if not os.path.exists(video_file):
            print(f"Video file does not exist {video_file}")
            raise FileNotFoundError(f"{video_file} not found")
        audio_file = os.path.join(folder_name,f"{base_title}.opus")
        ffmpeg.input(video_file).output(audio_file, acodec='copy').run(overwrite_output=True)
        video_file = convert_to_portrait(video_file)
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
        print("Generating Subtitle File")
        subtitle_file = f"{sanitize_filename(language)}_{random.randint(1000,9999)}.srt"
        text = ""
        for index, segment in enumerate(segments):
            segment_start = format_time(segment.start)
            segment_end = format_time(segment.end)
            text += f"{str(index+1)} \n"
            text += f"{segment_start} --> {segment_end} \n"
            text += f"{segment.text} \n"
            text += "\n"
            
        f = open(subtitle_file, "w", encoding= "utf-8")
        f.write(text)
        f.close()

        return subtitle_file
    def transcribe(audio):
        print("Transcribing")
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
        print("Adding Subtitle to Video")
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
                        **{"c:v": "libx264", "c:a": "aac"},
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
            print("dummy you did big error")
            
        return output_video
    def run():
        print("Starting Running")
        nonlocal output_path
        ydl_opts = {
            'match_filter': get_time,
            'outtmpl':output_path,
            'quiet' : True,
            'playliststart' : 1,
            'ignoreerrors' :True
            # ,'playlistend' : 3
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            print("Starting extraction")
            info = ydl.extract_info(url = playlist,download=False)
            for video in info['entries']:
                print("Starting loop")
                
                if video is None:
                    print("Skipped cus prob not available tbh")
                    continue
                if video.get("availability") == "private" or video.get("is_private") or video.get("availability") == "unavailable":
                    print(f"Skipped {video.get('id')} because it is private or unavailable")
                    continue
                title = summarize_title(video.get("title"), 1)
                id = sanitize_filename(video.get("id"))
            
                try:
                    video_path, audio_path = download_audio_and_video(id)
                except DownloadError as e:
                    print(f"Skipped {id} due to this error {e}")
                    continue
                except Exception as e:
                    print(f"Some other failure {e}")
                    continue
            
                
                
                
                language, segments = transcribe(audio=audio_path)
                subtitle_file = generate_subtitle_file(language=language, segments=segments)
                final_video = add_subtitle_to_video(False, subtitle_file, language, video_path)
                
                with VideoFileClip(final_video) as video:
                    subclip = video.subclipped(0,60)
                    p = Path(final_video)
                    output_path = str(p.with_name(p.stem + "_clipped" + p.suffix))
                    subclip.write_videofile(output_path, codec="libx264", audio_codec="aac")

                
                
                if len(title) > 100:
                    title = title[:100]
                print("Uploading with title:", title)
                upload_to_youtube(output_path, title)

                os.remove(video_path)
                os.remove(audio_path)
                os.remove(subtitle_file)

        
        
    run()

def main():
    print("Starting Upload")
    download_and_upload("https://www.youtube.com/watch?v=pYy0f4N2sVE&list=PL86SiVwkw_oeDQoAZwcuyoyG43eKWtbJM")



if __name__ == "__main__":
   print("Starting main loop")
   main()
