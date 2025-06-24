import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# --- Default YouTube URL ---
# A short, calming Creative Commons video of ocean waves.
DEFAULT_YOUTUBE_URL = "https://www.youtube.com/watch?app=desktop&v=zqpv2bySbr4"

def play_youtube_video(youtube_url):
    """
    Plays a single YouTube video in a Chromium browser and closes the browser when finished.
    This version attempts to disable YouTube's autoplay feature.
    """
    driver = None  # Initialize driver to None
    try:
        # Setup chrome options
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        options.add_argument("--no-first-run")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--mute-audio")

        # Installs and manages the driver for Chromium
        print("Setting up Chromium driver...")
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"Opening URL: {youtube_url}")
        driver.get(youtube_url)

        # Wait for the video player to be present
        wait = WebDriverWait(driver, 15)
        video_player = wait.until(
            EC.presence_of_element_located((By.ID, 'movie_player'))
        )

        # --- New: Logic to disable YouTube's "Up Next" Autoplay ---
        try:
            # Wait for the autoplay toggle button to be clickable
            autoplay_toggle = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-autonav-toggle-button"))
            )
            # Check if autoplay is currently enabled (the aria-checked attribute will be 'true')
            if autoplay_toggle.get_attribute("aria-checked") == "true":
                print("Autoplay feature is ON. Clicking to disable it...")
                autoplay_toggle.click()
            else:
                print("Autoplay feature is already OFF.")
        except TimeoutException:
            print("Could not find the autoplay toggle button. It might be off by default or the UI may have changed.")
        except Exception as e:
            print(f"An error occurred while trying to disable autoplay: {e}")

        # Click the play button to start the video
        try:
            video_player.click()
            print("Video playback initiated.")
        except Exception as e:
            print(f"Could not click play button, video might autoplay. Error: {e}")

        # --- Logic to wait for the current video to end ---
        video_finished = False
        while not video_finished:
            # We execute JavaScript to get the player's state. State 0 means the video has ended.
            try:
                player_status = driver.execute_script("return document.getElementById('movie_player').getPlayerState()")
                
                if player_status == 0:
                    print("Video has finished playing.")
                    video_finished = True
                elif player_status == -1:
                    print("Video player unstarted, waiting...")
                elif player_status is None:
                    print("Could not get player state. Waiting...")
            except WebDriverException:
                print("Browser is no longer available. Exiting video check.")
                break

            time.sleep(2)

    except TimeoutException:
        print("The video player did not load in time. Please check the URL and your connection.")
    except WebDriverException as e:
        print(f"A browser error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if driver:
            print("Closing the browser.")
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"No YouTube URL provided. Using default: {DEFAULT_YOUTUBE_URL}")
        video_url = DEFAULT_YOUTUBE_URL
    else:
        video_url = sys.argv[1]
        if "youtube.com/watch?v=" not in video_url and "youtu.be/" not in video_url:
            print("Invalid YouTube URL provided. Please provide a valid link.")
            sys.exit(1)

    while True:
        play_youtube_video(video_url)
        print("Playback complete. Restarting in 5 seconds...")
        time.sleep(5)