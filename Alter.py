import pandas

def PercentChange(OHLCV : pandas.DataFrame):
    TradingHour = ((OHLCV['Close'] - OHLCV['Open']) / OHLCV['Open']) * 100
    SinceLastClose = OHLCV["Close"].pct_change() * 100

    return TradingHour    

def MovingAvg(OHLCV, duration = 20, field = 'Close'):
    avgg = OHLCV[field].rolling(window=duration).mean()
    return avgg

def ExpMovingAvg(OHLCV, duration = 20, weight = 0.9, field = 'Close'):
    avgg = OHLCV[field].ewm(span=20, adjust=False).mean()
    return avgg
