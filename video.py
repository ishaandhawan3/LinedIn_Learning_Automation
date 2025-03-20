from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

def handle_video(driver):
    """Handles video playback"""
    from main import traverse_contents  # Local import to break circular dependency
    
    try:
        video_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vjs-tech"))
        )
        
        driver.execute_script("""
            arguments[0].playbackRate = 2;
            arguments[0].dispatchEvent(new Event('ratechange'));
        """, video_element)
        print("⏩ 2x playback enabled")

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
