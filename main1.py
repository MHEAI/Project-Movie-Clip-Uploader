from Classes.youtube_downloader import YoutubeDownloader
from Classes.title_cleaner import TitleCleaner
from Classes.video_editor import VideoEditor
from Classes.subtitle_handler import SubtitleHandler
from Classes.uploader import Uploader
from Classes.utils import Utilities


def main():
    playlist = "https://www.youtube.com/watch?v=2S4CF9cBYZ8&list=PL86SiVwkw_ofayKHT1CLKEmH-Yq9Eh310"
    
    downloader = YoutubeDownloader()
    title_cleaner = TitleCleaner()
    editor = VideoEditor()
    subtitler = SubtitleHandler()
    uploader = Uploader()
    utilizer = Utilities()
    
    
    info = downloader.extract_playlist(playlist)
    
    for video in info['entries']:
        
        if not video:
            continue

        try:
            video = downloader.extract_video_info(video["webpage_url"])
        except Exception as e:
            print(f"Skipped video because it could not be fetched: {e}")
            continue


        if (
            video.get("availability") == "private"
            or video.get("is_private")
            or video.get("availability") == "unavailable"
        ):
            print(f"Skipped {video.get('id')} because it is private or unavailable")
            continue
                
        # Clean And Summarize Title
        title = title_cleaner.clean_and_summarize_title(video.get("title"))
        
        # Download The Video File
        video_file = downloader.download_video(video["webpage_url"])
        print("Download returned:", video_file)
        # Clip Video
        clipped_file = editor.clip_video(video_file)
        if clipped_file is None:
            print("Skipping because clip_video failed.")
            continue
        # Crop To Portrait
        portrait_clipped_file = editor.convert_to_portrait(clipped_file)
        
        # Extract Audio
        audio_file = editor.extract_audio(portrait_clipped_file)
        
        # Transcribe
        language,segments = subtitler.transcribe(audio_file)
        
        # Generate SRT file
        srt_file = subtitler.generate_srt(segments,language)
        
        # Generate ASS file
        ass_file = subtitler.convert_to_ass(srt_file)
        
        # Burn Subtitles into Video
        subbed_video = editor.burn_subtitles(portrait_clipped_file,ass_file,language)
        
        # Upload Video
        uploader.upload_to_youtube(subbed_video,title)

        # Cleanup Files
        utilizer.cleanup_files([
            video_file,
            clipped_file,
            portrait_clipped_file,
            subbed_video,
            audio_file,
            srt_file,
            ass_file
            
        ])
        
        
        
    

if __name__ == "__main__":
    main()
    