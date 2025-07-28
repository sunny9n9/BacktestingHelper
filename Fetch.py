# For downloading and loading data to dataframes
# Need crypto support and better Discretion between Stock and MFs
import yfinance as yf
import pandas
import requests
import re

# Macros for what to fetch
SYMBOL = "^NSEI"
START = "2019-01-01"
END = None
INTERVAL = "1d"

# temp 
STATUS_SUCCESS = 1
STATUS_FAILURE = -1

# MF DATA
URL = "https://api.mfapi.in/mf"
URL_ALT = "https://www.amfiindia.com/spages/NAVAll.txt"

__all__ = [
    'Fetch', 'FetchStock', 'FetchMF', 'ReadCSV'
]

# Master fetch to fetch all kinds of assets
def Fetch(name, MF=False, interval=INTERVAL, **kwargs):
    """
    name can be name of index/MF 
    for index, can further use arguments like interval, start, etc as supported by yfinance
    """
    try:
        if MF:
            raise TypeError(f'Its a MF')
        return FetchStock(symbol=name, interval=interval, **kwargs)
    except Exception as e:
        try:
            return FetchMF(name)
        except Exception as e2:
            print(f"[Fetch] Failed to fetch '{name}':\nStock error: {e}\nMF error: {e2}")
            return None

# DOWNLOAD SYMBOL AND MAKE(SAVE) CSV
def FetchStock(symbol=SYMBOL, interval = INTERVAL, save_csv = True, **kwargs):
    try:
        df = yf.download(tickers=symbol, interval=interval, **kwargs)

        if df.empty:
            print(f"[FetchStock] No data returned for '{symbol}' "f"(interval={interval}, {kwargs})")
            return None

        if save_csv:
            filename = f"{symbol}.csv"
            df.to_csv(filename, index=True)
            print(f"[FetchStock] Saved to {filename} "f"({df.shape[0]} rows x {df.shape[1]} cols)")
        return df

    except Exception as e:
        print(f"[FetchStock] Error downloading '{symbol}': {e}")
        return None

# USE THAT CSV AND SORT TO OHLCV ORDER
def ReadCSV(name=SYMBOL):
    df = pandas.DataFrame()
    if re.match(r'^\d', name): # it means its a mutual fund    
        # print('MutualFundConfirmed')
        df = pandas.read_csv(f'{name}.csv', skiprows=1)
        # df = df.sort_index(ascending=True)
        df.columns = ['Date', 'Close']
        df['Date'] = pandas.to_datetime(df['Date'])
        df.set_index("Date", inplace=True, drop=True)
        df = df.iloc[::-1]

    else: # i will assume its a standard stock
        df = pandas.read_csv(f"{name}.csv", skiprows=3)
        df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
        df["Date"] = pandas.to_datetime(df["Date"])
        df.set_index(df["Date"], inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]]  # ensure column order

    return df

# HELPER TO FETCHMF
def _save_history(scheme):
    code       = scheme["schemeCode"]
    clean_name = scheme["schemeName"].replace(" ", "_").replace("/", "_")
    out_file   = f"{code}_{clean_name}.csv"

    hist = requests.get(f"https://api.mfapi.in/mf/{code}", timeout=5).json()
    data = hist.get("data", [])
    df   = pandas.DataFrame(data).rename(columns={
        "date": "Date",
        "nav": "NAV",
        "repurchase_price": "Repurchase_Price",
        "sale_price": "Sale_Price"
    })

    df.to_csv(out_file, index=False)
    print(f"Saved {len(df)} NAV records to {out_file}")
    return df

def FetchMF(name):
    try:
        raw = requests.get(URL, timeout=5).json()
        schemes = [
            {"schemeCode": str(s["schemeCode"]), "schemeName": s["schemeName"]}
            for s in raw
        ]
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch from mfapi.in ({e}). Falling back to AMFI NAVAll.txt")
        df_navall = pandas.read_csv(
            URL_ALT,
            sep=";",
            skiprows=1,
            names=[
                "schemeCode","schemeName",
                "isinDivPayout","isinGrowth",
                "nav","date"
            ],
            engine="python",
            dtype={"schemeCode": str}
        )
        schemes = df_navall[["schemeCode","schemeName"]].to_dict(orient="records")

    if isinstance(name, str):
        tokens  = name.lower().split()
        matches = [
            s for s in schemes
            if all(tok in s["schemeName"].lower() for tok in tokens)
        ]
    else:
        code_str = str(name)
        matches  = [s for s in schemes if s["schemeCode"] == code_str]

    if not matches:
        print(f"No schemes found for “{name}”.")
        return
    if len(matches) > 1:
        print(f"Found {len(matches)} matches for “{name}”:\n")
        for s in matches:
            print(f"  • {s['schemeName']}   (Code: {s['schemeCode']})")
        return

    scheme = matches[0]
    print(f"Found 1 match: {scheme['schemeName']} (Code: {scheme['schemeCode']})\n")
    return _save_history(scheme)
    
