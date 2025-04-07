from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import time
from main import traverse_contents

def content_Classifier(driver, current_index):
    """Classifies content and skips to next if completed"""
    from video import handle_video
    
    try:
        # Immediate check for completed content
        if is_content_completed(driver):
            print("⏩ Content already completed, skipping...")
            traverse_contents(driver, current_index + 1)
            return

        # Video detection and handling
        try:
            video_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".vjs-tech, video"))
            )
            if video_element.is_displayed():
                print("🎥 Video detected")
                handle_video(driver, current_index)
                return
        except (NoSuchElementException, TimeoutException):
            pass

        # Quiz detection
        if detect_quiz(driver):
            print("📝 Quiz detected")
            # handle_quiz(driver, current_index)
            return

        print("⚠️ Unknown content type, proceeding to next")
        traverse_contents(driver, current_index + 1)

    except Exception as e:
        print(f"🔍 Classification error: {str(e)[:100]}...")
        traverse_contents(driver, current_index + 1)

def is_content_completed(driver):
    """Check if current content is marked as completed"""
    try:
        completed_indicators = [
            (By.CSS_SELECTOR, ".content-completed-badge"),
            (By.XPATH, "//*[contains(text(), 'Completed')]"),
            (By.CSS_SELECTOR, ".classroom-toc-item__completed-icon"),
            (By.CSS_SELECTOR, ".classroom-toc-item--completed")
        ]
        
        for indicator in completed_indicators:
            elements = driver.find_elements(*indicator)
            if elements and any(elem.is_displayed() for elem in elements):
                return True
                
        # Also check video completion if it's a video
        try:
            video = driver.find_element(By.CSS_SELECTOR, ".vjs-tech")
            if video.is_displayed():
                progress = driver.execute_script(
                    "return arguments[0].currentTime / arguments[0].duration * 100", 
                    video
                )
                if progress > 95:  # 95% watched
                    return True
        except:
            pass
            
        return False
    except:
        return False

def find_and_click_next_incomplete_item(driver):
    """Improved next item detection with active state tracking"""
    print("🔍 Looking for next incomplete item...")
    try:
        expand_sidebar_if_collapsed(driver)
        
        # Get fresh TOC reference
        toc_items = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "classroom-toc-item"))
        )
        
        # Find current active index
        active_index = next((i for i, item in enumerate(toc_items) 
                           if "classroom-toc-item--is-active" in item.get_attribute("class")), -1)
        
        # Search remaining items
        for i in range(active_index + 1, len(toc_items)):
            try:
                item = toc_items[i]
                if not item.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon"):
                    print(f"⏭️ Found incomplete item at position {i+1}")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", item)
                    driver.execute_script("arguments[0].click();", item)
                    
                    # Verify activation
                    WebDriverWait(driver, 10).until(
                        lambda d: "classroom-toc-item--is-active" in item.get_attribute("class")
                    )
                    return True
            except StaleElementReferenceException:
                print("🔄 TOC updated, retrying...")
                return find_and_click_next_incomplete_item(driver)
        
        print("✅ No more incomplete items found")
        return False
        
    except Exception as e:
        print(f"⚠️ Navigation error: {str(e)[:100]}...")
        return False

def expand_sidebar_if_collapsed(driver):
    """Make sure the sidebar/TOC is expanded"""
    try:
        # Check if there's a toggle button for the TOC
        toggle_buttons = driver.find_elements(By.CSS_SELECTOR, 
            ".classroom-toc-toggle, .classroom-layout__sidebar-toggle, [aria-label*='Show Table of Contents']")
        
        for button in toggle_buttons:
            try:
                if button.is_displayed():
                    aria_expanded = button.get_attribute("aria-expanded")
                    if aria_expanded == "false":
                        button.click()
                        time.sleep(1)
                    break
            except:
                continue
                
        # Verify sidebar is visible
        sidebar = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 
                ".classroom-toc-container, .classroom-layout__sidebar"))
        )
    except:
        print("⚠️ Could not expand sidebar, proceeding anyway")
        
def navigate_back_to_course(driver):
    """Last resort: Navigate back to the specific course outline"""
    try:
        # Only use URL navigation as a last resort (triggers AI bot)
        current_url = driver.current_url
        
        if "/learning/" in current_url:
            base_parts = current_url.split("/learning/")[0]
            course_parts = current_url.split("/learning/")[1].split("/")
            if len(course_parts) > 0:
                course_name = course_parts[0]
                # Navigate directly to the course homepage
                course_url = f"{base_parts}/learning/{course_name}"
                driver.get(course_url)
                time.sleep(2)
                return
    except Exception as e:
        print(f"Error returning to course: {str(e)[:100]}")
    
    # Fallback to UI navigation
    try:
        # Look for course title or breadcrumb navigation
        course_nav = driver.find_element(By.CSS_SELECTOR, ".course-title, .classroom-nav-link")
        driver.execute_script("arguments[0].click();", course_nav)
        time.sleep(2)
    except:
        # Only use browser back as last resort
        driver.execute_script("window.history.back();")
        time.sleep(2)

def detect_quiz(driver):
    """Check for quiz elements"""
    try:
        quiz_selectors = [
            ".quiz-submit-button", 
            ".chapter-quiz-header", 
            ".quiz-question",
            "button[type='submit']"
        ]
        for selector in quiz_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements and any(elem.is_displayed() for elem in elements):
                return True
        return False
    except:
        return False

def is_content_completed(driver):
    """Checks multiple completion indicators"""
    try:
        completion_indicators = [
            ".content-completed-badge",
            ".classroom-toc-item__completed-icon",
            ".progress-bar-completed"
        ]
        return any(driver.find_elements(By.CSS_SELECTOR, selector) for selector in completion_indicators)
    except:
        return False