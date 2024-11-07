import os
import time
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DEVICE_ID = os.getenv("TIDBYT_DEVICE_ID")
PUSH_INTERVAL = 10

def start_server():
    try:
        subprocess.Popen(["python", "scrape_vote_count.py"])
        print("Flask server started successfully.")
    except Exception as e:
        print(f"Failed to start Flask server: {e}")

def run_pixlet_commands():
    while True:
        try:
            # Render the script to a webp image
            subprocess.run(["pixlet", "render", "vote_display.star"], check=True)
            # Push the rendered image to the Tidbyt device
            subprocess.run(["pixlet", "push", DEVICE_ID, "vote_display.webp"], check=True)
            print("Pixlet commands executed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred: {e}")
        time.sleep(PUSH_INTERVAL)

if __name__ == "__main__":
    start_server()
    time.sleep(PUSH_INTERVAL)
    run_pixlet_commands()
