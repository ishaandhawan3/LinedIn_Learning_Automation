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

def safe_click(driver, locator, timeout=10):
    """Handles stale elements with retries and fresh element references"""
    attempts = 0
    while attempts < 3:
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable(locator)
            ).click()
            return True
        except StaleElementReferenceException:
            attempts += 1
            time.sleep(1)
    return False

def wait_for_page_load(driver, timeout=10):
    """Wait for page to fully load after navigation"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(1)  # Short additional wait for any JavaScript to finish
        return True
    except:
        return False

def find_course_with_scrolling(driver, course_name):
    """Scroll through the page to find a course by name"""
    print("🔍 Searching for course with scrolling...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    attempts = 0
    max_attempts = 5
    
    while attempts < max_attempts:
        # Multiple selector strategies for course cards
        selectors = [
            f"//h3[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]",
            f"//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]",
            f"//*[contains(@class, 'base-card__title') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]",
            f"//*[contains(@class, 'card-title') and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{course_name.lower()}')]"
        ]
        
        for selector in selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for element in elements:
                try:
                    if course_name.lower() in element.text.strip().lower():
                        print(f"✅ Found course: {element.text}")
                        return element
                except:
                    continue
        
        # Scroll down
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(1)
        
        # Check if we've reached the bottom
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            attempts += 1
        else:
            attempts = 0  # Reset attempts if page height changes
            
        last_height = new_height
    
    return None

def traverse_contents(driver):
    """Handles content traversal with stale element protection"""
    from classify import content_Classifier
    
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "classroom-toc-item"))
        )
        
        # Refresh element list each iteration
        content_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")
        if not content_items:
            print("⚠️ No contents found!")
            return

        all_completed = True
        
        for index in range(len(content_items)):
            try:
                # Get fresh reference each time
                item = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")[index]
                
                # Check completion status
                if item.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon"):
                    print("✔️ Content completed")
                    continue

                # Check content status
                status_selectors = [
                    ".classroom-toc-item__viewing-status--in-progress",
                    ".classroom-toc-item__viewing-status"
                ]
                status_elements = item.find_elements(By.CSS_SELECTOR, ", ".join(status_selectors))
                
                if status_elements:
                    print("⏳ Processing incomplete content")
                    all_completed = False
                    
                    # Use JS click to avoid element detachment
                    driver.execute_script("arguments[0].click();", item)
                    time.sleep(2)
                    
                    # Wait for DOM update
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.staleness_of(item)
                        )
                    except:
                        pass  # Continue even if element doesn't become stale
                    
                    content_Classifier(driver)
                    return

            except (NoSuchElementException, StaleElementReferenceException):
                continue

        if all_completed:
            print("🎉 Course complete!")
            return

        print("🔄 Checking remaining content...")
        traverse_contents(driver)

    except Exception as e:
        print(f"⚠️ Traversal error: {str(e)[:100]}")

if __name__ == "__main__":
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.implicitly_wait(1)  # Reduced to prevent race conditions

        # Login flow
        driver.get("https://www.linkedin.com/learning/")
        wait_for_page_load(driver)

        # Sign-in with stale protection
        safe_click(driver, (By.LINK_TEXT, "Sign in"))

        # Credential handling
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "auth-id-input"))
            ).send_keys("23bcs12220@cuchd.in" + Keys.RETURN)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "session_password"))
            ).send_keys("Bharat@0930" + Keys.RETURN)
            print("🔑 Login successful!")

            # Wait for login completion
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav.global-nav"))
            )
            wait_for_page_load(driver)
        except Exception as e:
            print(f"🔒 Login failed: {str(e)[:100]}")
            driver.save_screenshot("login_error.png")
            sys.exit(1)

        # Navigation with stale protection
        safe_click(driver, (By.LINK_TEXT, "My Library"))
        wait_for_page_load(driver)
        safe_click(driver, (By.PARTIAL_LINK_TEXT, "Saved"))
        wait_for_page_load(driver)
        print("📚 Navigation successful")

        # Course selection with improved approach
        desired_course = input("Enter course name: ").strip().lower()
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]")
                )
            )

            course_elements = driver.find_elements(
                By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]"
            )

            for course in course_elements:
                if desired_course in course.text.strip().lower():
                    course.click()
                    print(f"Opened course: {course.text}")
                    break

        except:
            print(f"Course '{desired_course}' not found.")

        # Handle AI panel
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
        print(f"🔥 Critical error: {str(e)[:100]}")
        if driver:
            driver.save_screenshot(f"error_{time.strftime('%Y%m%d-%H%M%S')}.png")
    finally:
        if driver:
            input("⏯️ Press ENTER to exit...")
            driver.quit()

