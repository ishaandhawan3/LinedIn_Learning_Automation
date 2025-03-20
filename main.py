#importing libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from classify import content_Classifier

# Define traverse_contents first to avoid import issues
def traverse_contents(driver):
    """Recursively traverses the contents bar, checks status, and processes incomplete content."""
    try:
        time.sleep(2)  # Wait for page elements to load

        # Get all content items in the sidebar
        content_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")  
        if not content_items:
            print("⚠️ No contents found!")
            return

        all_completed = True  # Flag to check if entire course is complete

        for content in content_items:
            try:
                # Check if content is completed
                if content.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon"):
                    print("✔️ Content already completed. Skipping...")
                    continue

                # Check if content is in progress or not attempted
                elif content.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status--in-progress") or \
                     content.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status"):
                    print("⏳ Content in progress/not attempted. Classifying...")
                    all_completed = False

                    # Click and process content
                    content.click()
                    time.sleep(3)
                    content_Classifier(driver)
                    return  # Restart traversal after processing

            except NoSuchElementException:
                print("⚠️ Couldn't check content status")
                continue

        if all_completed:
            print("🎉🎉🎉 Course complete! 🎉🎉🎉")
            return

        print("🔄 Checking remaining contents...")
        traverse_contents(driver)

    except Exception as e:
        print(f"⚠️ Traversal error: {e}")

if __name__ == "__main__":
    # Single driver instance for entire session
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    try:
        # Login flow
        driver.get("https://www.linkedin.com/learning/")
        time.sleep(2)

        # Handle sign-in
        try:
            driver.find_element(By.LINK_TEXT, "Sign in").click()
            print("Clicked sign-in")
            time.sleep(1)
        except:
            print("Sign-in button not found")

        # Credential handling
        try:
            email_field = driver.find_element(By.ID, "auth-id-input")
            email_field.send_keys("23bcs12220@cuchd.in" + Keys.RETURN)
            time.sleep(1)

            password_field = driver.find_element(By.NAME, "session_password")
            password_field.send_keys("Bharat@0930" + Keys.RETURN)
            print("Login successful!")
            time.sleep(2)
        except:
            print("Login failed")
            driver.quit()
            exit()

        # Course navigation
        try:
            driver.find_element(By.LINK_TEXT, "My Library").click()
            print("Opened library")
            time.sleep(2)
            driver.find_element(By.PARTIAL_LINK_TEXT, "Saved").click()
            print("Opened saved courses")
            time.sleep(2)
        except:
            print("Navigation failed")
            driver.quit()
            exit()

        # Course selection
        desired_course = input("Enter course name: ").strip().lower()
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]"))
            )
            for course in driver.find_elements(By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]"):
                if desired_course in course.text.strip().lower():
                    course.click()
                    print(f"Opened: {course.text}")
                    break
        except:
            print(f"Course '{desired_course}' not found")
            driver.quit()
            exit()

        # Close AI bot
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "coach-panel__header-close"))
            )
            driver.execute_script("arguments[0].click();", close_btn)
            print("✅ Closed AI panel")
        except TimeoutException:
            print("❌ No AI panel found")

        # Start content processing
        traverse_contents(driver)

    finally:
        input("Press ENTER to exit...")
        driver.quit()
