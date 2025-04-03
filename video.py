from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time

def handle_video(driver):
    """Video handler with reliable completion detection"""
    from classify import find_and_click_next_incomplete_item
    
    try:
        video_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".vjs-tech, video"))
        )
        
        # Check if already completed
        progress = driver.execute_script("""
            return Math.round(
                (arguments[0].currentTime / arguments[0].duration) * 100
            ) || 0;
        """, video_element)
        
        if progress > 95:
            print(f"⏩ Skipping already watched video ({progress}%)")
            find_and_click_next_incomplete_item(driver)
            return

        # Set playback
        driver.execute_script("arguments[0].playbackRate = 2;", video_element)
        print("⏩ 2x playback enabled")

        # Monitor playback
        WebDriverWait(driver, 600).until(
            lambda d: d.execute_script("return arguments[0].ended", video_element)
        )
        print("✅ Video completed")
        
        # Auto-continue to next
        find_and_click_next_incomplete_item(driver)

    except Exception as e:
        print(f"📹 Playback error: {str(e)[:100]}...")
        find_and_click_next_incomplete_item(driver)


def get_video_progress(driver, video_element):
    """Get video completion percentage"""
    try:
        progress = driver.execute_script("""
            return Math.round(
                (arguments[0].currentTime / arguments[0].duration) * 100
            ) || 0;
        """, video_element)
        return min(progress, 100)
    except:
        return 0

def monitor_video_playback(driver, video_element):
    """Monitor video playback with completion checks"""
    start_time = time.time()
    while time.time() - start_time < 600:  # 10 minute timeout
        try:
            if not video_element.is_displayed():
                break
                
            current_time = driver.execute_script(
                "return arguments[0].currentTime", 
                video_element
            )
            duration = driver.execute_script(
                "return arguments[0].duration", 
                video_element
            )
            
            if duration and current_time >= duration - 5:  # Last 5 seconds
                print("🎬 Video ending detected")
                break
                
            time.sleep(5)
            
        except StaleElementReferenceException:
            print("🔄 Video element stale, refreshing...")
            video_element = driver.find_element(By.CLASS_NAME, "vjs-tech")
            
        except Exception as e:
            print(f"⚠️ Playback monitoring error: {str(e)[:50]}...")
            break
