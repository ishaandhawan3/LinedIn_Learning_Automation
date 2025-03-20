def handle_video(driver):
    """Handles video playback by setting speed to 2x and waiting for completion."""
    try:
        time.sleep(2)  # Wait for page elements to load

        # Find the video player
        try:
            video_element = driver.find_element(By.CLASS_NAME, "vjs-tech")
            driver.execute_script("arguments[0].playbackRate = 2;", video_element)
            print("🎥 Video playback speed set to 2x.")
        except NoSuchElementException:
            print("⚠️ Video player not found!")
            return

        # Wait for video completion
        while True:
            try:
                is_playing = driver.execute_script(
                    "return !arguments[0].paused && !arguments[0].ended;", 
                    video_element
                )
                if not is_playing:
                    print("✅ Video completed.")
                    break
            except:
                break
            time.sleep(5)

        print("🔄 Returning to content traversal...")
        # Directly call traverse_contents without reimporting
        traverse_contents(driver)

    except Exception as e:
        print(f"⚠️ Error in handle_video: {e}")
