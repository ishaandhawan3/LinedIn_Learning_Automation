
def set_playback_speed(driver, speed="2x"):
    try:
        # Wait for and click the playback speed button
        playback_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "vjs-playback-rate"))
        )
        playback_button.click()
        time.sleep(1)  # Give time for the menu to open

        # Ensure the menu is open using JavaScript
        driver.execute_script("document.querySelector('.vjs-playback-rate .vjs-menu').style.display = 'block';")

        # Find all speed options
        speed_options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='vjs-menu-content']//li"))
        )

        # Click on the desired speed option
        for item in speed_options:
            if speed in item.text:
                driver.execute_script("arguments[0].click();", item)  # Use JS click to avoid interception
                print(f"✅ Playback speed set to {speed}.")
                return True
        print(f"⚠️ Playback speed '{speed}' not found.")
        return False

    except TimeoutException:
        print("❌ Could not find playback speed options.")
        return False
    except Exception as e:
        print("⚠️ Error setting playback speed:", e)
        return False
