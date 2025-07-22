import yfinance as yf
import pandas
import requests

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

# DOWNLOAD SYMBOL AND MAKE(SAVE) CSV
def Fetch(symbol=SYMBOL,interval = INTERVAL, **kwargs):
    try:
        ticket = yf.download(tickers=symbol, interval=INTERVAL, **kwargs)
        if(ticket.empty): # dam they have empty
            return STATUS_FAILURE
        # Save
        ticket.to_csv(f"{symbol}.csv")
        print(f"Saved to {symbol}.csv \n Written {ticket.shape}")
        return ticket
    except Exception as ex:
        print(f"While trying to download {symbol} : {ex}")
        return STATUS_FAILURE


# USE THAT CSV AND SORT TO OHLCV ORDER
def ReadCSV(symbol=SYMBOL):
    df = pandas.read_csv(f"{SYMBOL}.csv", skiprows=3)
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
    _save_history(scheme)
