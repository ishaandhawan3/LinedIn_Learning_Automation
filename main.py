from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, 
                                       NoSuchElementException,
                                       StaleElementReferenceException)
import time
import sys

def traverse_contents(driver):
    """Recursively processes course content with stale element handling"""
    from classify import content_Classifier  # Local import to break circular dependency
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "classroom-toc-item"))
        )
        
        content_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")
        if not content_items:
            print("⚠️ No contents found!")
            return

        all_completed = True
        
        for index in range(len(content_items)):
            try:
                # Re-fetch elements each iteration
                item = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")[index]
                
                if item.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon"):
                    print("✔️ Content already completed.")
                    continue

                status_elements = item.find_elements(
                    By.CSS_SELECTOR, 
                    ".classroom-toc-item__viewing-status--in-progress, .classroom-toc-item__viewing-status"
                )
                
                if status_elements:
                    print("⏳ Content in progress/not attempted.")
                    all_completed = False
                    
                    driver.execute_script("arguments[0].click();", item)
                    time.sleep(2)
                    
                    WebDriverWait(driver, 15).until(
                        EC.staleness_of(item)
                    )
                    
                    content_Classifier(driver)
                    return

            except (NoSuchElementException, StaleElementReferenceException) as e:
                print(f"⚠️ Element issue: {str(e)[:100]}...")
                continue

        if all_completed:
            print("🎉🎉🎉 Course complete! 🎉🎉🎉")
            return

        print("🔄 Checking remaining contents...")
        traverse_contents(driver)

    except Exception as e:
        print(f"⚠️ Traversal error: {str(e)[:100]}...")

if __name__ == "__main__":
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.implicitly_wait(5)
        
        # Login flow
        driver.get("https://www.linkedin.com/learning/")
        
        # Sign-in
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Sign in"))
            ).click()
            print("Clicked sign-in")
        except:
            print("Sign-in button not found")

        # Credentials
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "auth-id-input"))
            ).send_keys("23bcs12220@cuchd.in" + Keys.RETURN)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "session_password"))
            ).send_keys("Bharat@0930" + Keys.RETURN)
            print("🔑 Login successful!")
        except Exception as e:
            print(f"🔒 Login failed: {str(e)[:100]}...")
            sys.exit(1)

        # Navigation
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "My Library"))
            ).click()
            
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Saved"))
            ).click()
            print("📚 Opened saved courses")
        except Exception as e:
            print(f"🧭 Navigation failed: {str(e)[:100]}...")
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
                        driver.execute_script("arguments[0].click();", course)
                        print(f"📖 Opened: {course.text}")
                        break
                except StaleElementReferenceException:
                    print("🔄 Refreshing course list...")
                    courses = driver.find_elements(*course_locator)
            else:
                raise Exception("❌ Course not found")
                
        except Exception as e:
            print(f"📚 Course error: {str(e)[:100]}...")
            sys.exit(1)

        # AI panel
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "coach-panel__header-close"))
            )
            driver.execute_script("arguments[0].click();", close_btn)
            print("🤖 Closed AI panel")
        except TimeoutException:
            print("⚠️ No AI panel found")

        # Start processing
        traverse_contents(driver)

    except Exception as e:
        print(f"🔥 Critical error: {str(e)[:100]}...")
    finally:
        if driver:
            input("⏯️ Press ENTER to exit...")
            driver.quit()
