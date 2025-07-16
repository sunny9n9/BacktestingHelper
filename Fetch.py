import yfinance as yf
import pandas

# Macros for what to fetch
SYMBOL = "^NSEI"
START = "2019-01-01"
END = None
INTERVAL = "1d"

# temp 
STATUS_SUCCESS = 1
STATUS_FAILURE = -1

# DOWNLOAD SYMBOL AND MAKE(SAVE) CSV
def Fetch(symbol=SYMBOL, start=START,end = END, interval = INTERVAL):
    try:
        ticket = yf.download(SYMBOL, start=START,end=END, interval=INTERVAL)
        if(ticket.empty): # dam they have empty
            return STATUS_FAILURE
        # Save
        ticket.to_csv(f"{SYMBOL}.csv")
        print(f"Saved to {SYMBOL}.csv")
        return ticket
    except Exception as ex:
        print(f"While trying to download symbol : {ex}")
        return STATUS_FAILURE


# USE THAT CSV AND SORT TO OHLCV ORDER
def ReadCSV(symbol=SYMBOL):
    df = pandas.read_csv(f"{SYMBOL}.csv", skiprows=3)
    df.columns = ["Date", "Open", "Close", "High", "Low", "Volume"]
    df["Date"] = pandas.to_datetime(df["Date"])
    df.set_index(df["Date"], inplace=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]]  # ensure column order

    return df