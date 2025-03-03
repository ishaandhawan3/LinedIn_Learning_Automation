import main

def classify_content(driver):
    """
    Function to detect if the current content is a video or a quiz.
    If it's a video, it redirects to the 'video_function'.
    If it's a quiz, it redirects to the 'quiz' function.
    """
    try:
        # Wait for the content page to load
        time.sleep(2)

        # Check if the content is a video by detecting the video player
        video_player = driver.find_elements(By.CLASS_NAME, "vjs-tech")
        if video_player:
            print("🎥 Detected Video: Redirecting to video_function...")
            video_function(driver)
            return

        # Check if the content is a quiz by detecting the quiz heading
        quiz_header = driver.find_elements(By.CLASS_NAME, "chapter-quiz-question__header")
        if quiz_header:
            print("📝 Detected Quiz: Redirecting to quiz function...")
            quiz(driver)
            return

        print("❌ Could not classify content. Skipping to next item.")
    
    except Exception as e:
        print(f"⚠️ Error in classification: {e}")
