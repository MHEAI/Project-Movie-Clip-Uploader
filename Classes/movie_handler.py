

import datetime
import json
import os
import random
import datetime  
import re
from pathlib import Path

import requests  
from dotenv import load_dotenv
import json
from moviepy import VideoFileClip
import srt


load_dotenv()

class MovieHandler:
    def __init__(self):
        pass
    @staticmethod
    def load_chunks_from_srt(path):
    
        with open(path, "r", encoding="utf-8") as f:
            subtitles = list(srt.parse(f.read()))

        blocks = []
        start_time = subtitles[0].start
        end_time = subtitles[-1].end

        current = start_time
        while current + datetime.timedelta(seconds=60) <= end_time:
            chunk_text = ""
            chunk_end = current + datetime.timedelta(seconds=60)

            for sub in subtitles:
                if current <= sub.start < chunk_end:
                    chunk_text += sub.content.strip() + " "

            if chunk_text.strip():
                blocks.append({
                    "start": str(current),
                    "end": str(chunk_end),
                    "text": chunk_text.strip()
                })

            current += datetime.timedelta(seconds=30)

        return blocks

    @staticmethod
    def score_scene_llm(block):
        
        prompt = f"""
    You are a movie critic.

    Here is a scene (from subtitles only):

    \"\"\"{block["text"]}\"\"\"

    Rate how interesting or dramatic this scene is on a scale of 1 to 10.
    Respond ONLY with a number. dont give a reason
    """

        headers = {
            "Authorization": os.getenv("OPENROUTER_API_KEY"),
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        try:

            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            res.raise_for_status()

            extract =lambda text: float(re.search(r"(10(\.0+)?|[1-9](\.\d+)?)", text).group(0)) if re.search(r"(10(\.0+)?|[1-9](\.\d+)?)", text) else None
            score = res.json()["choices"][0]["message"]["content"].strip()
            return extract(score)

        except Exception as e:
            print("LLM Error:", e)
            return 0  



    def find_most_interesting_scene(self,srt_path):
        """
        Full pipeline: loads SRT → chunks → scores → finds top-rated scene.
        Prints the best scene and returns it.
        """

        chunks = MovieHandler.load_chunks_from_srt(srt_path)
        print(f"🧠 Loaded {len(chunks)} chunks.")

        results = []


        for i, block in enumerate(chunks):
            score = MovieHandler.score_scene_llm(block)
            print(f"[{i+1}/{len(chunks)}] {block['start']}–{block['end']} → Score: {score}")
            results.append((score, block))

        best = sorted(results, key=lambda x: -x[0])[0]


        print("\n🎬 Most Interesting Scene:")
        print(f"{best[1]['start']} → {best[1]['end']}")
        print(best[1]["text"])
        with open("stamps.json","w") as f:
            json.dump(sorted(results, key=lambda x: -x[0]),f)
        return "stamps.json"
    
    def clip_video(self,video,times,max_videos):
        with open(times) as f:
            data = json.load(f)
        times = [(item[1]["start"], item[1]["end"]) for item in data]
        times = times[:max_videos]
        paths = []
        with VideoFileClip(video) as clip:
            for start,end in times:
                subclip = clip.subclipped(start, end)
                p = Path(video)
                output_path = str(p.with_name(p.stem + f"_{random.randint(1,1000)}" + p.suffix))
                if Path(output_path).exists():
                    Path(output_path).unlink()
                subclip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                paths.append(output_path)
        return paths
