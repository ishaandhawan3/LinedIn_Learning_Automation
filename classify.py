from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

def content_Classifier(driver):
    """Classifies content type"""
    from video import handle_video  # Local import to break circular dependency
    
    try:
        time.sleep(2)
        
        # Video check
        try:
            video_player = driver.find_element(By.CLASS_NAME, "vjs-tech")
            if video_player.is_displayed():
                print("🎥 Video detected")
                handle_video(driver)
                return
        except NoSuchElementException:
            pass

        # Quiz check
        try:
            quiz_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                ".quiz-submit-button, .chapter-quiz-header, .quiz-question"
            )
            if any(element.is_displayed() for element in quiz_elements):
                print("📝 Quiz detected")
                # handle_quiz(driver)  # Uncomment when implemented
                return
        except NoSuchElementException:
            pass

        print("⚠️ Unknown content type")

    except Exception as e:
        print(f"🔍 Classification error: {str(e)[:100]}...")
