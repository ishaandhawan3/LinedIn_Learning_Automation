from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

from video import handle_video  # Import video handling function
from quiz import handle_quiz  # Import quiz handling function

def content_Classifier(driver):
    """Classifies the content as either a video or a quiz and calls the respective function."""
    try:
        time.sleep(2)  # Allow content to load properly
        
        # Check if a video player is present
        try:
            video_player = driver.find_element(By.CLASS_NAME, "vjs-tech")  # Video player class
            if video_player.is_displayed():
                print("🎥 Video detected. Calling handle_video()...")
                handle_video(driver)
                return  # Exit after handling video
        except NoSuchElementException:
            pass  # No video player found, continue checking for quiz

        # Check if a quiz is present
        try:
            quiz_elements = [
                driver.find_element(By.CLASS_NAME, "quiz-submit-button"),  # Submit button
                driver.find_element(By.CLASS_NAME, "chapter-quiz-header"),  # Quiz header
                driver.find_element(By.CLASS_NAME, "quiz-question")  # Question element
            ]
            
            if any(element.is_displayed() for element in quiz_elements):
                print("📝 Quiz detected. Calling handle_quiz()...")
                handle_quiz(driver)
                return  # Exit after handling quiz
        except NoSuchElementException:
            pass  # No quiz elements found

        print("⚠️ Unknown content type. Skipping...")

    except Exception as e:
        print(f"⚠️ Error in content classification: {e}")
