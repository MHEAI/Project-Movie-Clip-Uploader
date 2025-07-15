import json
from moviepy.video.io.VideoFileClip import VideoFileClip
from pathlib import Path
import random
with open(r'test.json') as f:
    data = json.load(f)

times = [(item[1]["start"], item[1]["end"]) for item in data]
times = times[:10]

def clip_video(video):
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
clip_video("Interstellar.mp4")