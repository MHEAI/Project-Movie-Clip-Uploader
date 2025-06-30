
from requests import post
from json import dumps

class TitleCleaner:
    def __init__(self):
        pass
    
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
- Append hashtags: #Shorts #MovieClips   #FilmLovers. to the very end



dont add asterisks



dont make it more than 100 characters

Return only one plain string combining the cleaned title with hashtags and the tagline. No extra explanation or multiple options.

double check the length and make sure it isnt more than 100 characters
"""
        
        
        
        response = post(
            url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": "Bearer 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",
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
        return data["choices"][0]["message"]["content"]
    
        