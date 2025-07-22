import pandas

def PercentChange(OHLCV : pandas.DataFrame):
    SinceLastClose : pandas.Series = OHLCV["Close"].pct_change().fillna(0) * 100
    SinceLastClose.index = OHLCV.index
    return SinceLastClose

def IntradayPercentChange(OHLCV : pandas.DataFrame):
    TradingHour : pandas.Series = ((OHLCV['Close'] - OHLCV['Open']) / OHLCV['Open']) * 100
    TradingHour.index = OHLCV.index
    return TradingHour

def IntradayPeaktoPeak(OHLCV):
    change = ((OHLCV['High'] - OHLCV['Low']) / OHLCV['Low']) * 100
    change.index = OHLCV.index
    return change

def AddDayData(OHLCV : pandas.Series | pandas.DataFrame):
    if isinstance(OHLCV, pandas.Series):
        OHLCV = OHLCV.to_frame(name='Values')
    OHLCV['Day'] = OHLCV.index.day_name()
    return OHLCV

def MovingAvg(OHLCV, duration = 20, field = 'Close'):
    avgg = OHLCV[field].rolling(window=duration).mean()
    avgg.index = OHLCV.index
    return avgg

def ExpMovingAvg(OHLCV, duration = 20, weight = 0.9, field = 'Close'):
    avgg = OHLCV[field].ewm(span=duration, adjust=False).mean() #fukin wxponential weighted moving function
    avgg.index = OHLCV.index
    return avgg

def TrueRange(OHLCV, period = 14):
    prev_close = OHLCV['Close'].shift(1)
    intraday_p2p = (OHLCV['High'] - OHLCV['Low']).abs()
    high_prev_close = (OHLCV['High'] - prev_close).abs()
    low_prev_close = (OHLCV['Low'] - prev_close).abs()
    true_range = pandas.DataFrame({"intraday_p2p" : intraday_p2p, 
                                   "high_prev_close" : high_prev_close,
                                   "low_prev_close" : low_prev_close}).max(axis=1) # we want row wise not wholw max
    return true_range

def AvgTrueRange(OHLCV, period = 14):
    true_range = TrueRange(OHLCV)
    avg_true_range = true_range.rolling(period).mean()
    atr = true_range.ewm(alpha=1/period, adjust=False).mean()

    return atr
    

def RelativeStrengthIndex(OHLCV, period = 14):
    close_prices = OHLCV['Close']
    change_since_close = close_prices.diff()
    gain = change_since_close.clip(lower=0)
    loss = -change_since_close.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
import pandas as pd

# INTENED USE : TO COMPLIMENT RSI WHEN DECIDING TO BUY/SELL
# ADX > 25 FOR CONFIRMATIONN
def AverageDirIdx(OHLCV, period=14):
    alpha = 1/period
    
    df = OHLCV.copy()
    # 1. Calculate True Range
    df['tr']  = TrueRange(OHLCV)
    df['atr'] = df['tr'].ewm(alpha=alpha, adjust=False).mean()

    # 2. Directional Movements
    df['up_move'] = df['High'] - df['High'].shift(1)
    df['down_move'] = df['Low'].shift(1) - df['Low']
    df['dm_plus']  = df['up_move'].where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), 0.0) # basically clip all so that we hav only gains
    df['dm_minus'] = df['down_move'].where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), 0.0) # same for loss
    
    # 3. Wilder’s smoothing (RMA) on TR, DM+ and DM−
    df['atr'] = df['tr'].ewm(alpha=alpha, adjust=False).mean()
    df['dm_plus_sm']  = df['dm_plus'].ewm(alpha=alpha, adjust=False).mean()
    df['dm_minus_sm'] = df['dm_minus'].ewm(alpha=alpha, adjust=False).mean()

    # 4. +DI and −DI
    df['pdi'] = 100 * df['dm_plus_sm']  / df['atr']
    df['mdi'] = 100 * df['dm_minus_sm'] / df['atr']

    # 5. DX and ADX
    df['dx']  = 100 * (df['pdi'] - df['mdi']).abs() / (df['pdi'] + df['mdi'])
    df['adx'] = df['dx'].ewm(alpha=alpha, adjust=False).mean()

    return df['adx']

