import requests
import pandas as pd
import time

# Step 1: Prepare session
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com",
    "Connection": "keep-alive"
}
session.headers.update(headers)

# Step 2: Visit homepage to get cookies
print("[*] Warming up session...")
response = session.get("https://www.nseindia.com", timeout=5)
time.sleep(2)

# Step 3: Access option chain
url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
print("[*] Fetching option chain...")
response = session.get(url, timeout=5)

# Debug if error
if response.status_code != 200:
    print(f"HTTP error: {response.status_code}")
    print(response.text[:300])
    exit()

try:
    data = response.json()
except Exception as e:
    print("JSON decode failed:", e)
    print("Response was:")
    print(response.text[:300])
    exit()

# Step 4: Parse and show
records = data['records']['data']
all_options = []
for entry in records:
    strike = entry.get('strikePrice')
    ce = entry.get('CE', {})
    pe = entry.get('PE', {})
    
    all_options.append({
        'strikePrice': strike,
        'CE_OI': ce.get('openInterest'),
        'CE_LTP': ce.get('lastPrice'),
        'PE_OI': pe.get('openInterest'),
        'PE_LTP': pe.get('lastPrice'),
        'expiryDate': ce.get('expiryDate') or pe.get('expiryDate')
    })

df = pd.DataFrame(all_options)
print(df.head())
df.to_csv('option.csb')
