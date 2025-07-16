import pandas
import matplotlib.pyplot as plt
import mplfinance as mpf
import plotly.graph_objects as go

# PLOT A NORMAL LINE CHART TO SEE MOVEMENT
def Overview(OHLCV, PlotBy, Title="Yeh...plot"):
    if PlotBy not in OHLCV.columns:
        raise ValueError(f"'{PlotBy}' not found in DataFrame")

    OHLCV[PlotBy].plot(title=Title, figsize=(12,5))
    plt.xlabel("Date")
    plt.ylabel(f"{PlotBy}")
    plt.grid(True)
    plt.show()
    return 1

# PLOT CANDLES IN DIFFERENT TIEM FRAMES
def Candle(OHLCV : pandas.DataFrame, Interval, Title="IDK MATE"):
    OHLCV_resampled = OHLCV.resample(Interval).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum' if 'Volume' in OHLCV.columns else 'first'
    })
        # These are how to resample (aruments)
    # Check if volume is all NaN
    show_volume = "Volume" in OHLCV.columns and not OHLCV["Volume"].isna().all()
    mpf.plot(OHLCV_resampled, type='candle', style='charles', title=Title, volume=show_volume, ylabel="Price", ylabel_lower="Volume" if show_volume else None)

# FUKING DISAPPOINTMENT
def PlotlyCandle(OHLCV, title="Something"):
    fig = go.Figure(data=[go.Candlestick(
        x=OHLCV.index,
        open=OHLCV['Open'],
        high=OHLCV['High'],
        low=OHLCV['Low'],
        close=OHLCV['Close'],
        name="Price"
    )]) # interesting format

    fig.update_layout(
        title=title, xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False, template="plotly_white", height=600
    )
    fig.show()

# FOR PERCENT_CHANGE WWWWTTTTTTTTTTTFFFFFFFFFFFFF
def PlotChange(OHLCV):
    trading_hour = ((OHLCV['Close'] - OHLCV['Open']) / OHLCV['Open']) * 100
    print(trading_hour.min(), trading_hour.max()) # WHY NO NEGATIVES??!!
    plt.figure(figsize=(14, 5))
    for date, val in zip(OHLCV.index, trading_hour):
        plt.vlines(x=date, ymin=min(0, val), ymax=max(0, val), color='green' if val >= 0 else 'red', linewidth=1)

    plt.title("% Change (Close vs Open)")
    plt.ylabel("% Change")
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def PlotChange2(OHLCV):
    day_to_day = OHLCV['Close'].pct_change() * 100
    print(day_to_day.min(), day_to_day.max())
    plt.figure(figsize=(14, 5))
    for date, val in zip(OHLCV.index, day_to_day):
        plt.vlines(x=date, ymin=min(0, val), ymax=max(0, val), color='green' if val >= 0 else 'red', linewidth=1)

    plt.title("% Change (Close to Close)")
    plt.ylabel("% Change")
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
