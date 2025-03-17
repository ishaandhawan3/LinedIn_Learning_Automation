from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

def handle_video(driver):
    """Handles video playback by setting speed to 2x and waiting for completion."""
    try:
        time.sleep(2)  # Wait for page elements to load

        # Find the video player
        try:
            video_element = driver.find_element(By.CLASS_NAME, "vjs-tech")  # Video element
            driver.execute_script("arguments[0].playbackRate = 2;", video_element)  # Set speed to 2x
            print("🎥 Video playback speed set to 2x.")

        except NoSuchElementException:
            print("⚠️ Video player not found!")
            return  # Exit if no video found

        # Wait for video to finish playing
        while True:
            try:
                # Check if the video is still playing
                is_playing = driver.execute_script("return !arguments[0].paused && !arguments[0].ended;", video_element)
                if not is_playing:
                    print("✅ Video completed.")
                    break  # Exit loop if video has ended
            except:
                break  # Handle unexpected errors in script execution

            time.sleep(5)  # Check every 5 seconds

        print("🔄 Returning to content traversal...")
        # Import traverse_contents here to avoid circular imports
        from main import traverse_contents
        traverse_contents(driver)  # Call traversal function again after video completion

    except Exception as e:
        print(f"⚠️ Error in handle_video: {e}")
