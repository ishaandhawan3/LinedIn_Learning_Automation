from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from main import traverse_contents

def handle_video(driver):
    try:
        # Wait for video element with refresh handling
        video_element = WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.CLASS_NAME, "vjs-tech")
        )
        
        # Set playback speed
        driver.execute_script("""
            arguments[0].playbackRate = 2;
            arguments[0].dispatchEvent(new Event('ratechange'));
        """, video_element)
        print("⏩ 2x playback enabled")

        # Monitor playback with stale element handling
        while True:
            try:
                is_playing = driver.execute_script(
                    "return !arguments[0].paused && !arguments[0].ended;", 
                    video_element
                )
                if not is_playing:
                    print("✅ Video completed")
                    break
            except StaleElementReferenceException:
                print("🔄 Refreshing video reference...")
                video_element = driver.find_element(By.CLASS_NAME, "vjs-tech")
                
            time.sleep(5)

        print("🔄 Restarting traversal...")
        traverse_contents(driver)

    except Exception as e:
        print(f"📹 Video error: {str(e)[:100]}...")
