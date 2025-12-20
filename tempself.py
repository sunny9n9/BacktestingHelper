import numpy
import pandas
import matplotlib
import regex
import requests
import json
import os
import time
import random

URL_TABLE = 'https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry={expiry}'
URL_CHART = 'https://www.nseindia.com/api/chart-databyindex?index=OPTIDXNIFTY{expiry}{CEPE}{strike}.00'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
}

connection = requests.Session()

def EstablishConnection(url, connection : requests.Session):
    try:
        connection.get("https://www.nseindia.com", headers=HEADERS) # fake home page wlse get blocked
        time.sleep(1)
        response = connection.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        if 'filtered' in data:
            return data['filtered'] # we return only option chain data itslef
    except requests.exceptions.RequestException as e:
        raise NotImplementedError(f'fuk this :: {e}')
    
def GetRangeOfChain(data):
    start_strike = data['data'][0]['strikePrice']
    end_strike = data['data'][-1]['strikePrice']

    # for safety, i will consider +- 2000 strike price
    start_strike = int(start_strike) + 2000
    end_strike = int(end_strike) - 2000

    print(f'start strike + 2000 :: {start_strike}')
    print(f'end strike - 2000 :: {end_strike}')
    return start_strike, end_strike

def ScrapeAllChartData(url, expiry, cepe, strike, connection : requests.Session):
    try:
        chart_data = connection.get(url.format(expiry = expiry, CEPE = cepe, strike = strike), headers=HEADERS, timeout=10)
        chart_data.raise_for_status()
        chart_data = chart_data.json()
        if 'grapthData' in chart_data:
            return{
                f'{strike}{cepe}' : chart_data['grapthData'] # fuking wrong spelling
            }
        else:
            raise NotImplementedError('idk other types of error but return was bad')
    except requests.exceptions.RequestException as e:
        # raise NotImplementedError(f'fuk this site :: {e}')
        print(f'thankyou NSEI {e}')
        return None

def main():
    EXPIRY1 = '14-Aug-2025'
    EXPIRY2 = '14-08-2025'

    data = EstablishConnection(URL_TABLE.format(expiry = EXPIRY1), connection)
    strike_range = GetRangeOfChain(data)
    all_data = { }
    for things in range(strike_range[0], strike_range[1], 50):
        for current in ['CE', 'PE']:
            returned_data = ScrapeAllChartData(URL_CHART, EXPIRY2, current, things, connection)
            if returned_data is None:
                for retries in range(5):
                    returned_data = ScrapeAllChartData(URL_CHART, EXPIRY2, current, things, connection)
                    time.sleep(random.uniform(0.5, 2))
                    print(f'retrying {retries} for {things}{current}')
                    if returned_data:
                        break
            if returned_data is None :
                # its still null m8
                continue
            all_data.update(returned_data)
            time.sleep(random.uniform(0.1, 1.0))
    print(f'current is :: {len(all_data)}')

    with open(f"optiondata_{EXPIRY1}.json", "w") as f:
        json.dump(all_data, f, indent=2)


if __name__ == '__main__':
    main()

# fuking unauthorised for everything