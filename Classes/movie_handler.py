import asyncio
import datetime
import json
import logging
import os
import random
import re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from moviepy.video.io.VideoFileClip import VideoFileClip
import srt
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class MovieHandler:
    def __init__(self):
        pass

    @staticmethod
    def load_chunks_from_srt(path):
        logging.info(f"Loading SRT file from {path}")
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
    async def score_scene_llm_async(block):
        import httpx

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
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                res.raise_for_status()
                content = res.json()["choices"][0]["message"]["content"]
                match = re.search(r"(10(\.0+)?|[1-9](\.\d+)?)", content)
                return float(match.group(0)) if match else 0
        except Exception as e:
            logging.error(f"LLM Error: {e}")
            return 0

    async def find_most_interesting_scene_async(self, srt_path):
        chunks = MovieHandler.load_chunks_from_srt(srt_path)
        logging.info(f"🧠 Loaded {len(chunks)} chunks.")

        tasks = [MovieHandler.score_scene_llm_async(block) for block in chunks]
        scores = await asyncio.gather(*tasks)

        results = list(zip(scores, chunks))
        best = sorted(results, key=lambda x: -x[0])[0]

        print("\n🎬 Most Interesting Scene:")
        print(f"{best[1]['start']} → {best[1]['end']}")
        print(best[1]["text"])

        with open("stamps.json", "w") as f:
            json.dump(sorted(results, key=lambda x: -x[0]), f)

        return "stamps.json"

    @staticmethod
    def _cut_clip(video, start, end):
        
        p = Path(video)
        output_path = str(p.with_name(p.stem + f"_{random.randint(1,1000)}" + p.suffix))
        if Path(output_path).exists():
            Path(output_path).unlink()
        with VideoFileClip(video) as clip:
            subclip = clip.subclipped(start, end)
            subclip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)
        return output_path

    def clip_video(self, video, times_json_path, max_videos):
        logging.info(f"Clipping video {video} with max {max_videos} scenes.")
        with open(times_json_path) as f:
            data = json.load(f)

        times = [(item[1]["start"], item[1]["end"]) for item in data][:max_videos]

        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(MovieHandler._cut_clip, video, start, end) for start, end in times]
            paths = [f.result() for f in futures]

        return paths
