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
import sys
from classify import content_Classifier

def traverse_contents(driver):
    """Recursively traverses the contents bar, checks status, and processes incomplete content."""
    try:
        time.sleep(2)

        content_items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "classroom-toc-item"))
        )

        all_completed = True

        for content in content_items:
            try:
                if content.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon"):
                    print("✔️ Content already completed.")
                    continue

                elif content.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status--in-progress") or \
                     content.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status"):
                    print("⏳ Content in progress/not attempted.")
                    all_completed = False

                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(content)).click()
                    time.sleep(3)
                    content_Classifier(driver)
                    return

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
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        # Login flow
        driver.get("https://www.linkedin.com/learning/")
        
        # Handle sign-in
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Sign in"))
            ).click()
            print("Clicked sign-in")
        except:
            print("Sign-in button not found")

        # Credential handling
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "auth-id-input"))
            ).send_keys("23bcs12220@cuchd.in" + Keys.RETURN)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "session_password"))
            ).send_keys("Bharat@0930" + Keys.RETURN)
            
            print("Login successful!")
        except Exception as e:
            print(f"Login failed: {e}")
            sys.exit(1)

        # Course navigation
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "My Library"))
            ).click()
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Saved"))
            ).click()
            
            print("Opened saved courses")
        except Exception as e:
            print(f"Navigation failed: {e}")
            sys.exit(1)

        # Course selection
        desired_course = input("Enter course name: ").strip().lower()
        try:
            course_locator = (By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]")
            courses = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(course_locator)
            )
            
            for course in courses:
                try:
                    if desired_course in course.text.strip().lower():
                        WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(course)
                        ).click()
                        print(f"Opened: {course.text}")
                        break
                except:
                    continue
            else:
                raise Exception("Course not found")
                
        except Exception as e:
            print(f"Course error: {e}")
            sys.exit(1)

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

    except Exception as e:
        print(f"⚠️ Critical error: {e}")
    finally:
        if driver:
            input("Press ENTER to exit...")
            driver.quit()
