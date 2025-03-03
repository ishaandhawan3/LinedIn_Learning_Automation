from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to LinkedIn Learning
driver.get("https://www.linkedin.com/learning/")
time.sleep(2)

# Click "Sign In" if present
try:
    sign_in_button = driver.find_element(By.LINK_TEXT, "Sign in")
    sign_in_button.click()
    print("Clicked 'Sign in'.")
    time.sleep(1)
except:
    print("Sign in button not found, proceeding...")

# Log in
try:
    email_field = driver.find_element(By.ID, "auth-id-input")
    email_field.send_keys("23bcs12220@cuchd.in")  # Replace with actual email
    email_field.send_keys(Keys.RETURN)
    time.sleep(1)

    password_field = driver.find_element(By.NAME, "session_password")
    password_field.send_keys("Bharat@0930")  # Replace with actual password
    password_field.send_keys(Keys.RETURN)
    print("Login successful!")
    time.sleep(2)
except:
    print("Login failed.")
    driver.quit()
    exit()

# Navigate to "My Library"
try:
    library_button = driver.find_element(By.LINK_TEXT, "My Library")
    library_button.click()
    print("Navigated to My Library.")
    time.sleep(2)
except:
    print("Could not find 'My Library' button.")

try:
    saved_button = driver.find_element(By.PARTIAL_LINK_TEXT, "Saved")
    saved_button.click()
    print("Navigated to Saved courses.")
    time.sleep(2)
except:
    print("Could not find 'Saved' section.")

# Ask for the course name
desired_course = input("Enter the course name you want to open: ").strip().lower()

# Wait for courses to load and select the desired course
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]"))
    )
    course_elements = driver.find_elements(By.XPATH, "//h3 | //span[contains(@class, 'base-card__title')]")

    for course in course_elements:
        if desired_course in course.text.strip().lower():
            course.click()
            print(f"Opened course: {course.text}")
            break
except:
    print(f"Course '{desired_course}' not found.")

# Wait for video player to load
try:
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.CLASS_NAME, "vjs-tech"))
    )
    print("Video player loaded.")
except TimeoutException:
    print("Video player did not load in time.")
    driver.quit()
    exit()

# Set playback speed to 2x at the beginning only
try:
    # Wait for and click the playback speed button
    playback_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "vjs-playback-rate"))
    )
    playback_button.click()
    time.sleep(1)  # Give time for the menu to open

    # Use JavaScript to ensure menu is open
    driver.execute_script("document.querySelector('.vjs-playback-rate .vjs-menu').style.display = 'block';")
    
    # Find all speed options
    speed_options = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='vjs-menu-content']//li"))
    )

    # Click on the 2x speed option
    for item in speed_options:
        if "2x" in item.text:
            driver.execute_script("arguments[0].click();", item)  # Use JS click to avoid interception
            print("✅ Playback speed set to 2x.")
            break
except TimeoutException:
    print("❌ Could not find playback speed options.")
except Exception as e:
    print("⚠️ Error setting playback speed:", e)

# Click the cross button for the ai bot
try:
    # Wait for the button to appear
    close_button = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.CLASS_NAME, "coach-panel__header-close")
        )
    )
    
    # Click the button using JavaScript to avoid click interception issues
    driver.execute_script("arguments[0].click();", close_button)
    
    print("✅ Cross button detected and clicked.")
    
except TimeoutException:
    print("❌ Cross button not found.")

#Detecting chapter quiz
def is_chapter_quiz_page(driver):
    try:
        # Wait for the quiz header to appear
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "chapter-quiz-question__header"))
        )
        print("🎯 Chapter Quiz detected!")
        return True
    except TimeoutException:
        print("❌ No Chapter Quiz detected.")
        return False

# Usage:
if is_chapter_quiz_page(driver):
    print("📖 This is a Chapter Quiz Page!")
else:
    print("🎥 Not a quiz page, continue watching videos.")


#Cancelling countdown for next video
def cancel_autoplay_countdown(driver):
    try:
        # Wait for the cross button to appear (used to cancel countdown)
        countdown_cancel_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "_icon_ps32ck"))
        )
        countdown_cancel_button.click()
        print("⏹️ Autoplay countdown canceled.")
        return True
    except TimeoutException:
        print("⚠️ No autoplay countdown detected.")
        return False

# Example usage:
cancel_autoplay_countdown(driver)

input("Press ENTER to exit the page...")

# Close the browser
driver.quit()
