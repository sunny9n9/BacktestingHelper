import requests
import json
import time
import random

# -----------------------------
# CONFIG
# -----------------------------
URL_TABLE = "https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry={expiry}"
URL_CHART = "https://www.nseindia.com/api/chart-databyindex?index=OPTIDXNIFTY{expiry}{CEPE}{strike}.00"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}

BASE_URL = "https://www.nseindia.com"

session = requests.Session()

# -----------------------------
# COOKIE REFRESH
# -----------------------------
def refresh_cookies():
    """Refresh cookies once, so session is authorized."""
    print("[INFO] Refreshing cookies from NSE homepage...")
    r = session.get(BASE_URL, headers=HEADERS, timeout=10)
    r.raise_for_status()
    print("[INFO] Cookies refreshed.")

# -----------------------------
# OPTION CHAIN
# -----------------------------
def get_option_chain(expiry):
    """Fetch option chain for given expiry."""
    url = URL_TABLE.format(expiry=expiry)
    r = session.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data["filtered"]

def get_strike_range(chain_data):
    """Extract a safe strike range from option chain."""
    start = chain_data["data"][0]["strikePrice"]
    end = chain_data["data"][-1]["strikePrice"]
    return int(start) + 2000, int(end) - 2000

# -----------------------------
# CHART DATA
# -----------------------------
def get_chart(expiry, cepe, strike):
    """Fetch chart data for one strike+CE/PE."""
    url = URL_CHART.format(expiry=expiry, CEPE=cepe, strike=strike)
    try:
        r = session.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "grapthData" in data:  # NSE spelling
            return {f"{strike}{cepe}": data["grapthData"]}
    except requests.RequestException as e:
        print(f"[WARN] Failed for {strike}{cepe}: {e}")
    return None

# -----------------------------
# MAIN
# -----------------------------
def main():
    EXPIRY_CHAIN = "14-Aug-2025"  # format for option chain
    EXPIRY_CHART = "14-08-2025"    # format for chart

    refresh_cookies()

    chain_data = get_option_chain(EXPIRY_CHAIN)
    strike_min, strike_max = get_strike_range(chain_data)

    all_data = {}
    for strike in range(strike_min, strike_max, 50):
        for cepe in ["CE", "PE"]:
            chart = get_chart(EXPIRY_CHART, cepe, strike)

            # Retry if failed
            retries = 0
            while chart is None and retries < 3:
                time.sleep(random.uniform(0.5, 2))
                chart = get_chart(EXPIRY_CHART, cepe, strike)
                retries += 1
                print(f"[INFO] Retry {retries} for {strike}{cepe}")

            if chart:
                all_data.update(chart)

            # Be polite to server
            time.sleep(random.uniform(0.3, 1.0))

    print(f"[DONE] Collected {len(all_data)} strike legs.")

    with open(f"optiondata_{EXPIRY_CHAIN}.json", "w") as f:
        json.dump(all_data, f, indent=2)


if __name__ == "__main__":
    main()
