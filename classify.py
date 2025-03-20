from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

def content_Classifier(driver):
    """Classifies content type"""
    from video import handle_video  # Local import to break circular dependency
    
    try:
        # Wait for page to stabilize
        time.sleep(2)
        
        # Video check with more reliable detection
        try:
            video_player = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".vjs-tech, video"))
            )
            if video_player.is_displayed():
                print("🎥 Video detected")
                handle_video(driver)
                return
        except (NoSuchElementException, TimeoutException):
            print("🔍 No video found, checking for quiz...")

        # Quiz check with improved selectors
        try:
            quiz_selectors = [
                ".quiz-submit-button", 
                ".chapter-quiz-header", 
                ".quiz-question",
                "button[type='submit']",
                "form[class*='quiz']"
            ]
            
            for selector in quiz_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if any(element.is_displayed() for element in elements):
                    print("📝 Quiz detected")
                    # handle_quiz(driver)  # Uncomment when implemented
                    return
        except NoSuchElementException:
            pass

        print("⚠️ Unknown content type, checking if we should return to course page")
        
        # If content type is unknown, try to find course navigation
        try:
            course_nav = driver.find_element(By.CSS_SELECTOR, ".course-navigation, .classroom-nav")
            if course_nav.is_displayed():
                print("🏠 Returning to course page")
                from main import traverse_contents
                traverse_contents(driver)
                return
        except:
            pass

        print("❓ Could not classify content, will retry traversal")
        from main import traverse_contents
        traverse_contents(driver)

    except Exception as e:
        print(f"🔍 Classification error: {str(e)[:100]}...")
        # Try to continue with traversal
        from main import traverse_contents
        traverse_contents(driver)
