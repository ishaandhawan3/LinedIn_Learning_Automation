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


# Import here to avoid circular imports
from classify import content_Classifier

# Function to detect and handle the sidebar
def traverse_contents(driver):
    """Recursively traverses the contents bar, checks status, and processes incomplete content."""
    try:
        time.sleep(2)  # Wait for page elements to load

        # Get all content items in the sidebar
        content_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item")  
        if not content_items:
            print("⚠️ No contents found!")
            return

        all_completed = True  # Flag to check if the entire course is complete

        for content in content_items:
            try:
                # Check if content is completed
                if content.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon"):
                    print("✔️ Content is already completed. Skipping...")
                    continue  # Skip to the next content

                # Check if content is in progress or not attempted
                elif content.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status--in-progress") or \
                     content.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status"):
                    print("⏳ Content is in progress or not attempted. Classifying content...")
                    all_completed = False  # Set flag to False since at least one content is incomplete

                    # Click on the content to open it
                    content.click()
                    time.sleep(3)  # Allow page to load

                    # Call the classification function
                    content_Classifier(driver)
                    return  # Stop loop execution as function will restart traverse_contents after processing

            except NoSuchElementException:
                print("⚠️ Could not check status for a content item.")
                continue

        # If all contents are completed
        if all_completed:
            print("🎉🎉🎉 Congratulationsssss! Your course is now complete. 🎉🎉🎉")
            return

        # Recursively call traverse_contents to keep checking
        print("🔄 Checking for remaining contents...")
        traverse_contents(driver)

    except Exception as e:
        print(f"⚠️ Error in traverse_contents: {e}")

# Run the traversal function
traverse_contents(driver)

input("Press ENTER to exit the page...")

# Close the browser
driver.quit()
