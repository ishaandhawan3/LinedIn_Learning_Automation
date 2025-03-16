#importing libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import classify


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

# Function to detect and handle the sidebar
def open_contents_panel(driver):
    """Ensure the contents sidebar is open."""
    try:
        sidebar = driver.find_element(By.CLASS_NAME, "classroom-layout__sidebar")
        if "slide-out-panel--open" not in sidebar.get_attribute("class"):
            menu_button = driver.find_element(By.CLASS_NAME, "classroom-toc__toggle")
            menu_button.click()
            print("📂 Contents panel opened.")
            time.sleep(2)
    except NoSuchElementException:
        print("⚠️ Could not find contents panel button.")

# Function to classify content (Video or Quiz)
def content_Classifier(driver):
    """Classifies content as a video or a quiz."""
    try:
        # Check for video element
        video_element = driver.find_element(By.TAG_NAME, "video")
        if video_element.is_displayed():
            print("🎬 Content is a Video. Playing now...")
            time.sleep(5)  # Simulating video play time
            return "video"

        # Check for quiz elements
        quiz_element = driver.find_element(By.CLASS_NAME, "quiz-container")  # Adjust class name if needed
        if quiz_element.is_displayed():
            print("📝 Content is a Quiz. Attempting now...")
            return "quiz"

    except NoSuchElementException:
        print("⚠️ Unable to classify content.")
        return "unknown"

# Function to traverse contents
def traverse_contents(driver):
    """Traverse the course content list, skipping completed items and processing the rest."""
    try:
        # Ensure sidebar is open
        open_contents_panel(driver)

        # Wait for content list to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "classroom-toc-item"))
        )

        # Fetch all content items
        content_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")
        completed_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon")

        print(f"📜 Total Contents: {len(content_items)}")

        for index, item in enumerate(content_items):
            try:
                # Check if the item is completed
                if item in completed_items:
                    print(f"✅ Content {index + 1} is already completed. Skipping...")
                    continue

                # Scroll into view to ensure visibility
                driver.execute_script("arguments[0].scrollIntoView();", item)
                time.sleep(1)

                # Click on the item
                item.click()
                print(f"▶️ Starting Content {index + 1}...")

                # Classify and process content
                classification = content_Classifier(driver)

                # Add logic based on classification (e.g., handle quizzes)
                if classification == "quiz":
                    print("📝 Handling Quiz... (Add quiz-handling logic here)")
                elif classification == "video":
                    print("🎬 Watching video...")

                time.sleep(2)  # Simulate processing delay

            except Exception as e:
                print(f"⚠️ Error processing content {index + 1}: {e}")

        print("✅ Finished processing all contents.")

    except Exception as e:
        print("⚠️ Error in traversing contents:", e)

# Run the traversal function
traverse_contents(driver)

input("Press ENTER to exit the page...")

# Close the browser
driver.quit()