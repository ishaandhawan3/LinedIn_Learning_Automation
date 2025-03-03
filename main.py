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



##function to detect the status
def traverse_contents(driver):
    try:
        # Ensure the contents bar is open
        sidebar_class = "slide-out-panel slide-out-panel--right slide-out-panel--open classroom-layout__sidebar hue-web-color-scheme--dark"
        sidebar = driver.find_element(By.CLASS_NAME, "classroom-layout__sidebar")

        if sidebar.get_attribute("class") != sidebar_class:
            print("📌 Sidebar is closed. Opening contents panel...")
            open_contents_panel(driver)  #  Function to open the panel

        # Wait for contents to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "classroom-toc-item__viewing-status"))
        )

        # Get all content items
        content_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status")
        completed_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item__completed-icon")
        in_progress_items = driver.find_elements(By.CLASS_NAME, "classroom-toc-item__viewing-status--in-progress")

        total_items = len(content_items) + len(completed_items) + len(in_progress_items)
        print(f"📜 Total Contents: {total_items}")

        for index, item in enumerate(content_items + in_progress_items):
            try:
                # Scroll into view to ensure visibility
                driver.execute_script("arguments[0].scrollIntoView();", item)
                time.sleep(1)  # Small delay to allow UI to adjust

                # Click on the item
                item.click()
                print(f"▶️ Starting Content {index + 1}...")

                # Call the detection function
                detection(driver)

                # Recursively call traverse_contents() after finishing
                traverse_contents(driver)
                return  # Exit current recursion and continue

            except Exception as e:
                print(f"⚠️ Error processing content {index + 1}: {e}")

        # If all items are completed, exit recursion
        print("✅ All contents are completed!")

    except Exception as e:
        print("⚠️ Error in traversing contents:", e)

def open_contents_panel(driver):
    try:
        # Locate and click the button to open the panel (adjust selector if needed)
        menu_button = driver.find_element(By.CLASS_NAME, "classroom-toc__toggle")
        menu_button.click()
        print("📂 Contents panel opened.")
        time.sleep(2)  # Wait for the panel to open
    except Exception as e:
        print("⚠️ Could not open contents panel:", e)

# Example function for detection (To be implemented as per requirement)
def detection(driver):
    print("🔍 Running detection function...")
    time.sleep(3)  # Simulating detection process
    print("✔️ Detection completed.")


traverse_contents(driver)

input("Press ENTER to exit the page...")

# Close the browser
driver.quit()