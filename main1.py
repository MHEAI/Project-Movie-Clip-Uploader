from Classes.youtube_downloader import YoutubeDownloader
from Classes.title_cleaner import TitleCleaner
from Classes.video_editor import VideoEditor
from Classes.subtitle_handler import SubtitleHandler
from Classes.youtube_uploader import YoutubeUploader
from Classes.utils import Utilities


def main():
    playlist = "https://www.youtube.com/watch?v=pYy0f4N2sVE&list=PL86SiVwkw_oeDQoAZwcuyoyG43eKWtbJM"
    
    downloader = YoutubeDownloader()
    title_cleaner = TitleCleaner()
    editor = VideoEditor()
    subtitler = SubtitleHandler()
    uploader = YoutubeUploader()
    utilizer = Utilities()
    
    
    info = downloader.extract_playlist(playlist)
    for video in info['entries']:
        
        if not downloader.is_duration_valid(video):
            continue
        
        # Clean And Summarize Title
        title = title_cleaner.clean_and_summarize_title(video["title"])
        
        # Download The Video File
        video_file = downloader.download_video(video["webpage_url"])
        
        # Clip Video
        clipped_file = editor.clip_video(video_file)
        
        # Crop To Portrait
        portrait_clipped_file = editor.convert_to_portrait(clipped_file)
        
        # Extract Audio
        audio_file = editor.extract_audio(portrait_clipped_file)
        
        # Transcribe
        language,segments = subtitler.transcribe(audio_file)
        
        # Generate SRT file
        srt_file = subtitler.generate_srt(language,segments)
        
        # Generate ASS file
        ass_file = subtitler.convert_to_ass(srt_file)
        
        # Burn Subtitles into Video
        subbed_video = editor.add_subtitles(portrait_clipped_file, ass_file,language)
        
        # Upload Video
        uploader.upload(subbed_video,title)

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
    