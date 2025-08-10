import os
import random
import time
import argparse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secrets.json"
TOKEN_FILE = "token.json"

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (HttpError, IOError)
MAX_RETRIES = 10
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def initialize_upload(youtube, options):
    tags = options.keywords.split(",") if options.keywords else None
    body = {
        "snippet": {
            "title": options.title,
            "description": options.description,
            "tags": tags,
            "categoryId": options.category,
        },
        "status": {
            "privacyStatus": options.privacyStatus,
            "selfDeclaredMadeForKids": False
        },
    }
    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True),
    )
    resumable_upload(insert_request)

def resumable_upload(request):
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            status, response = request.next_chunk()
            if response:
                if "id" in response:
                    print(response["id"])  # Only print the raw video ID
                else:
                    print(f"ERROR: No video ID in response: {response}")
                    exit(1)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = f"Retriable HTTP error {e.resp.status}: {e.content}"
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = f"Retriable error: {e}"

        if error:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("Exceeded max retries.")
            sleep = random.uniform(1, 2 ** retry)
            print(f"Sleeping {sleep:.2f} seconds before retry...")
            time.sleep(sleep)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Video file to upload")
    parser.add_argument("--title", default="Test Title", help="Video title")
    parser.add_argument("--description", default="Test Description", help="Video description")
    parser.add_argument("--category", default="22", help="Numeric video category ID")
    parser.add_argument("--keywords", default="", help="Comma-separated video keywords")
    parser.add_argument("--privacyStatus", default="public", choices=VALID_PRIVACY_STATUSES, help="Video privacy status")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        exit("File does not exist.")

    youtube = get_authenticated_service()
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        print(f"HTTP error {e.resp.status}:\n{e.content}")
        exit(1)
