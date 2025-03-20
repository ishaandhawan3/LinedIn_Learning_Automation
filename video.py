from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time

def handle_video(driver):
    """Handles video playback"""
    from main import traverse_contents  # Local import to break circular dependency
    
    try:
        # Wait for video element with refresh handling
        video_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vjs-tech"))
        )
        
        # Set playback speed and ensure it's applied
        driver.execute_script("""
            arguments[0].playbackRate = 2;
            arguments[0].dispatchEvent(new Event('ratechange'));
        """, video_element)
        print("⏩ 2x playback enabled")

        # Monitor playback with stale element handling
        max_wait_time = 600  # 10 minutes max for video to complete
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                is_playing = driver.execute_script(
                    "return !arguments[0].paused && !arguments[0].ended;", 
                    video_element
                )
                remaining = driver.execute_script(
                    "return Math.floor((arguments[0].duration - arguments[0].currentTime) / 60);",
                    video_element
                )
                print(f"⏱️ Approximately {remaining} minutes remaining...")
                
                if not is_playing:
                    print("✅ Video completed")
                    # Wait for any post-video processing
                    time.sleep(2)
                    break
            except (StaleElementReferenceException, Exception) as e:
                print(f"🔄 Refreshing video reference... ({str(e)[:50]})")
                try:
                    video_element = driver.find_element(By.CLASS_NAME, "vjs-tech")
                except:
                    print("❌ Video element no longer available, continuing...")
                    break
            
            time.sleep(5)

        # Ensure we're back at the course page before continuing
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "classroom-toc-item"))
            )
        except:
            # If we can't find the course page elements, try to go back
            try:
                driver.execute_script("window.history.back();")
                time.sleep(2)
            except:
                pass

        print("🔄 Restarting traversal...")
        traverse_contents(driver)

    except Exception as e:
        print(f"📹 Video error: {str(e)[:100]}...")
        # Try to continue with traversal anyway
        from main import traverse_contents
        traverse_contents(driver)
