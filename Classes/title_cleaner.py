
import os

from json import dumps
from requests import post
from dotenv import load_dotenv


load_dotenv()


class TitleCleaner:
    def __init__(self):
        print("Loaded API_KEY:", os.getenv("API_KEY"))
    
    def clean_and_summarize_title(self,title):
        prompt = f"""You are a title cleanup tool. Given this movie clip title:

{title}

Perform these steps:

- Remove junk words like "4K", "HD", "Trailer", "Movieclips", etc.
- Remove special characters such as brackets, pipes, colons, and dashes.
- Remove year indicators like "2006" or "2020".
- Normalize whitespace.
- Add a random catchy adjective like "Epic" or "Legendary" plus the word "Scene".
- remove the original thing and Then summarize what this entire process does in a cool, catchy tagline that includes the movie name and the clip's main premise dont over do it.
- After creating the cleaned title and the short catchy tagline, append the hashtags exactly like this with no extra space or punctuation before them: " #Shorts #MovieClips #FilmLovers".




dont add asterisks



dont make it more than 100 characters

Return only one plain string combining the cleaned title with hashtags and the tagline. No extra explanation or multiple options.

double check the length and make sure it isnt more than 100 characters
"""
        
        
        
        response = post(
            url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": os.getenv("API_KEY"),
            "Content-Type": "application/json",
        },
        data=dumps({
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
        raw_title = data["choices"][0]["message"]["content"]
        
        if not raw_title:
            raise ValueError("TitleCleaner returned an empty title.")

        if len(raw_title) > 100:
            raw_title = raw_title[:97] + "..."

        print("Cleaned title:", repr(raw_title))
        return raw_title
    
        