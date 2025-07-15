# Movie Clip Uploader

A flask web app to process youtube playlists or upload movie for video clip uploading

---

## Features

- Analyze a youtube playlist and clip it
- Upload your own movie files for automated AI clipping
- Extract, transcribe and burn subtitles onto video clips
- Convert clips to portrait mode
- Upload processed clips directly to Youtube using data api with auto generated titles or hashtags

---

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/MHEAI/Project-Movie-Clip-Uploader
   ```
2. Create and activate a virtual enviroment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

   Install dependencies:

   ```bash
    pip install uv
    uv install
   ```

3. Run the flask app:

   ```bash
       python main.py
   ```

## Usage

Youtube Playlist:
Paste a Youtube playlist URL. Select amount of vidoes. Click Process Playlist

Upload Movie File:
Upload a movie file, specify the number of clips to generate, and click process movie

## Configuration

Max upload size is set to 5 gb (adjustable in line 18) in main .py

Logging can be changed for each module
