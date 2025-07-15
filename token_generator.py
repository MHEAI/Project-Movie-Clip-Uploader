from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json
import os

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_new_token():
    flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())
    
    print("✅ New token.json created.")

    # Optional: test YouTube API call
    youtube = build("youtube", "v3", credentials=creds)
    response = youtube.channels().list(part="snippet", mine=True).execute()
    print("🔗 Connected as:", response["items"][0]["snippet"]["title"])

if __name__ == "__main__":
    if not os.path.exists("client_secrets.json"):
        print("❌ client_secret.json not found!")
    else:
        get_new_token()
