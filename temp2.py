import requests
import time
import random
import json
from datetime import datetime
import os

# ========= CONFIGURATION =========
BASE_URL = "https://www.nseindia.com"
OPTION_CHAIN_API = "https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry=21-Aug-2025"
SAVE_FOLDER = "nse_option_chain_data"
FETCH_INTERVAL = (180, 300)  # range in seconds (3 to 5 min)
# =================================

# Ensure save directory exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Standard browser-like headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}

# Create a session to store cookies
session = requests.Session()


def refresh_cookies():
    """
    Refresh cookies by visiting NSE homepage.
    This is necessary to avoid getting blocked.
    """
    try:
        print("[INFO] Refreshing cookies from NSE homepage...")
        session.get(BASE_URL, headers=HEADERS, timeout=10)
        print("[INFO] Cookies refreshed successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to refresh cookies: {e}")


def fetch_option_chain():
    """
    Fetch option chain JSON from NSE and return it.
    If blocked or invalid response, return None.
    """
    try:
        r = session.get(OPTION_CHAIN_API, headers=HEADERS, timeout=15)

        # If response is JSON, parse it
        if r.headers.get("Content-Type", "").startswith("application/json"):
            return r.json()
        else:
            print(f"[WARN] Non-JSON response. Status {r.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return None


def save_data(data):
    """
    Save fetched JSON data to a timestamped file.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SAVE_FOLDER, f"nifty_options_{ts}.json")
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[SAVE] Data saved: {filepath}")


def main():
    """
    Main loop to run indefinitely, fetching and saving option chain data.
    """
    refresh_cookies()  # Initial cookie fetch

    while True:
        data = fetch_option_chain()

        if data:
            save_data(data)
        else:
            print("[INFO] Data fetch failed. Attempting to refresh cookies...")
            refresh_cookies()

        # Random sleep between requests to avoid detection
        wait_time = random.randint(*FETCH_INTERVAL)
        print(f"[SLEEP] Waiting {wait_time} seconds before next request...")
        time.sleep(wait_time)



if __name__ == "__main__":
    main()
