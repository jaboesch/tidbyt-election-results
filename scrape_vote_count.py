import os
import time
import threading
import atexit
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

# Load env variables
load_dotenv()
URL = os.getenv("ELECTION_RESULTS_URL")
GOP_ELEMENT_SELECTOR = os.getenv("GOP_ELEMENT_SELECTOR")
DEM_ELEMENT_SELECTOR = os.getenv("DEM_ELEMENT_SELECTOR")
POLL_INTERVAL = 60

# Initialize Flask app and Selenium driver
app = Flask(__name__)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)

# Cache data since selenium is slow and we don't want excessive fetches
cached_data = {
    "timestamp": None,
    "dem": 0,
    "gop": 0
}

def fetch_election_data():
    global cached_data
    while True:
        payload = {
            "timestamp": time.time(),
            "dem": 0,
            "gop": 0,
        }

        try:
            # Load and parse the page
            driver.get(URL)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Select the GOP and DEM vote elements
            gop_element = soup.select_one(GOP_ELEMENT_SELECTOR)
            dem_element = soup.select_one(DEM_ELEMENT_SELECTOR)
            
            # Extract the text content from the elements (if selected correctly, this should only be the vote count)
            gop_text = ''.join([str(content) for content in gop_element.contents if isinstance(content, str)]).strip()
            dem_text = ''.join([str(content) for content in dem_element.contents if isinstance(content, str)]).strip()

            # Update the cache with the latest data
            payload['gop'] = int(gop_text)
            payload['dem'] = int(dem_text)
            cached_data = payload
            
            print(f"Data updated at {time.ctime(cached_data['timestamp'])}: {cached_data}")
        except Exception as e:
            print(f"Error fetching election data: {e}")

        # Wait before the next fetch
        time.sleep(POLL_INTERVAL)

@app.route("/api/election", methods=["GET"])
def election_api():
    print(f"API request at {time.ctime()} returning: {cached_data}")
    return jsonify(cached_data)

# Start background thread for polling
threading.Thread(target=fetch_election_data, daemon=True).start()

# Clean up the driver when the server stops
atexit.register(driver.quit)

if __name__ == "__main__":
    app.run(port=5000)
