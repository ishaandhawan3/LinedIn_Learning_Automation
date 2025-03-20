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
from classify import content_Classifier

def safe_click(driver, locator, timeout=10):
    """Handles stale elements by retrying clicks with fresh element references"""
    attempts = 0
    while attempts < 3:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            element.click()
            return True
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
    return False

def traverse_contents(driver):
    """Recursively processes course content with stale element handling"""
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
                # Re-fetch elements each iteration to avoid staleness
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
                    
                    # Use JavaScript click to avoid element detachment issues
                    driver.execute_script("arguments[0].click();", item)
                    time.sleep(2)
                    
                    # Refresh element reference after click
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
        
        # Login flow with stale element handling
        driver.get("https://www.linkedin.com/learning/")
        
        # Sign-in process
        if not safe_click(driver, (By.LINK_TEXT, "Sign in")):
            print("⚠️ Sign-in button not found or clickable")
        
        # Credential handling
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

        # Navigation with stale element protection
        if not safe_click(driver, (By.LINK_TEXT, "My Library")):
            print("📚 Could not access library")
            sys.exit(1)
            
        if not safe_click(driver, (By.PARTIAL_LINK_TEXT, "Saved")):
            print("💾 Could not access saved courses")
            sys.exit(1)

        # Course selection with refreshed elements
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

        # AI panel handling
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "coach-panel__header-close"))
            )
            driver.execute_script("arguments[0].click();", close_btn)
            print("🤖 Closed AI panel")
        except TimeoutException:
            print("⚠️ No AI panel found")

        # Start content processing
        traverse_contents(driver)

    except Exception as e:
        print(f"🔥 Critical error: {str(e)[:100]}...")
    finally:
        if driver:
            input("⏯️ Press ENTER to exit...")
            driver.quit()
