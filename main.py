from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException
)
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

def traverse_contents(driver, start_index=0):
    """Handles course content traversal, skipping completed items"""
    from classify import content_Classifier
    
    try:
        # Ensure TOC is expanded and visible
        # expand_sidebar_if_collapsed(driver)
        
        # Get fresh TOC items reference
        toc_container = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".classroom-toc-container"))
        )
        content_items = toc_container.find_elements(By.CLASS_NAME, "classroom-toc-item")
        
        # Track progress through items
        for index in range(start_index, len(content_items)):
            try:
                # Get fresh reference to avoid staleness
                item = toc_container.find_elements(By.CLASS_NAME, "classroom-toc-item")[index]
                item_classes = item.get_attribute("class")
                
                # Skip completed items
                if "classroom-toc-item--completed" in item_classes:
                    print(f"⏭️ Skipping completed item {index+1}")
                    continue
                    
                print(f"🔍 Processing item {index+1}/{len(content_items)}")
                
                # Scroll and click using JavaScript
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", item)
                driver.execute_script("arguments[0].click();", item)
                
                # Wait for content load
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".classroom-layout__content"))
                )
                
                # Process content
                content_Classifier(driver, index)
                return  # Exit after processing one item

            except StaleElementReferenceException:
                print("🔄 TOC updated, restarting traversal")
                return traverse_contents(driver, index)  # Retry current index
                
        print("🎉 All content items processed!")

    except Exception as e:
        print(f"⚠️ Traversal error: {str(e)[:100]}")


if __name__ == "__main__":
    driver = None
    try:
        # Add Chrome options to handle GPU errors
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    except:
        pass
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.implicitly_wait(1)

        driver.get("https://www.linkedin.com/learning/")
        wait_for_page_load(driver)

        safe_click(driver, (By.LINK_TEXT, "Sign in"))

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "auth-id-input"))
            ).send_keys("23bcs12220@cuchd.in" + Keys.RETURN)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "session_password"))
            ).send_keys("Bharat@0930" + Keys.RETURN)
            print("🔑 Login successful!")

            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "nav.global-nav"))
            )
            wait_for_page_load(driver)
        except Exception as e:
            print(f"🔒 Login failed: {str(e)[:100]}")
            driver.save_screenshot("login_error.png")
            sys.exit(1)

        safe_click(driver, (By.LINK_TEXT, "My Library"))
        wait_for_page_load(driver)
        safe_click(driver, (By.PARTIAL_LINK_TEXT, "Saved"))
        wait_for_page_load(driver)
        print("📚 Navigation successful")

        traverse_contents(driver)
    
    except TimeoutException as te:
        print(f"⏰ Timeout occurred: {str(te)}")
        if driver:
            driver.save_screenshot("timeout_main.png")
    
    except NoSuchElementException as ne:
        print(f"🔎 Element missing: {str(ne)}")
        if driver:
            driver.save_screenshot("missing_element_main.png")
    
    except WebDriverException as wde:
        print(f"🚨 WebDriver error: {str(wde)}")
        if driver:
            driver.save_screenshot("webdriver_error.png")
    
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        if driver:
            driver.save_screenshot("unexpected_error.png")
    
    finally:
        if driver:
            input("⏯️ Press ENTER to exit...")
            driver.quit()

