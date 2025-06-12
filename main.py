from playwright.sync_api import Playwright, sync_playwright, expect
from yt_dlp import YoutubeDL
from rich import print
def run(playwright: Playwright) -> None:
    
    """Return the link of the playlist of movie clips"""
    
    # Initialize new chromium page
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    
    # Navigate To MovieClips Channel Clips Playlist
    page.goto("https://www.youtube.com/")
    page.get_by_role("combobox", name="Search").click()
    page.get_by_role("combobox", name="Search").fill("movieclips")
    page.get_by_role("combobox", name="Search").press("Enter")
    page.get_by_role("link", name="Movieclips tooltip Verified @").click()
    page.get_by_role("link", name="Clips in 4K/UHD").click()
    
    # Navigates to the share button and gets the link
    page.get_by_role("button", name="Share").click()
    page.wait_for_selector("""xpath=//*[@id="share-url"]""")
    share_link = page.locator("""xpath=//*[@id="share-url"]""").input_value()
    context.close()
    browser.close()
    
    #Splits the link to get ID
    share_link = share_link.split("list=")[1]
    
    return share_link
def download(link):
    def get_time(info):
        
        """Returns whether the duration is viable for downloading"""
        
        duration = info.get('duration')
        if duration is None:
            return "no duration info"
        if duration >= 180:
            return "duration too long"
        return None

    # Defines options dictionary to tell ydl which filters to apply
    ydl_opts = {
        'match_filter': get_time,
        'outtmpl':r"C:\Users\dell\Desktop\Coding\TOP SECRET PROJECTS\Project Movie Clip Uploader\Test\%(title)s.%(ext)s"

    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
        
def main():
    
    with sync_playwright() as playwright:
        link = run(playwright)
    download(link)
    

    print(link)
if __name__ == "__main__":
    main()
