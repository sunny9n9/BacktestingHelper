import pandas
import pandas as pd
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
        'Volume': 'sum' if 'Volume' in OHLCV.columns else 'first' # YOU BETTER HOPE ALL DATA HAS VOLUME
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

# INTRADAY CHANGE
def PlotChange(OHLCV):
    trading_hour = ((OHLCV['Close'] - OHLCV['Open']) / OHLCV['Open']) * 100
    # print(f"{OHLCV['Close']}  {OHLCV['Open']}  {trading_hour}") # WHY NO NEGATIVES??!!
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
    day_to_day = OHLCV['Close'].pct_change().fillna(0) * 100
    # print(day_to_day.min(), day_to_day.max())
    plt.figure(figsize=(14, 5))
    for date, val in zip(OHLCV.index, day_to_day):
        plt.vlines(x=date, ymin=min(0, val), ymax=max(0, val), color='green' if val >= 0 else 'red', linewidth=1)

    plt.title("% Change (Close to Close)")
    plt.ylabel("% Change")
    plt.xlabel("Date")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
def PlotChange3(OHLCV: pd.DataFrame):
    if 'Close' not in OHLCV.columns:
        raise ValueError("OHLCV DataFrame must contain a 'Close' column.")
    if OHLCV.empty:
        print("Empty DataFrame provided. Nothing to plot.")
        return
    # Yeah, why not 
    
    close = OHLCV['Close']
    close_values = close.values # Use numpy array for faster indexing [note to self WTF]
    n = len(close_values)

    current_peak_idx = 0 
    current_trough_idx = 0
    in_drawdown = False
    drawdown_segments_for_plotting = []

    for i in range(1, n):
        price = close_values[i]

        if in_drawdown:
            if price < close_values[current_trough_idx]:
                current_trough_idx = i
        else:
            current_trough_idx = current_peak_idx

        drawdown_from_peak = (price - close_values[current_peak_idx]) / close_values[current_peak_idx]
        if drawdown_from_peak <= -0.05:
            if not in_drawdown:
                in_drawdown = True
                current_trough_idx = i
            else:
                if price < close_values[current_trough_idx]:
                    current_trough_idx = i

        if in_drawdown:
            recovery_from_trough = (price - close_values[current_trough_idx]) / close_values[current_trough_idx]

            if recovery_from_trough >= 0.03:
                drawdown_segments_for_plotting.append((current_peak_idx, current_trough_idx))

                current_peak_idx = i
                in_drawdown = False
                current_trough_idx = i
        else:
            if price > close_values[current_peak_idx]:
                current_peak_idx = i
                current_trough_idx = i

    if in_drawdown:
        drawdown_segments_for_plotting.append((current_peak_idx, current_trough_idx))

    plt.figure(figsize=(14, 6))
    plt.plot(range(n), close_values, label='Close Price', color='blue', alpha=0.8)

    for start_idx, end_idx in drawdown_segments_for_plotting:
        actual_start = min(start_idx, n - 1)
        actual_end = min(end_idx, n - 1)
        if actual_start > actual_end:
            actual_start, actual_end = actual_end, actual_start

        plt.plot(range(actual_start, actual_end + 1), close_values[actual_start:actual_end + 1],
                 color='red', linewidth=2, label='_HiddenLabel_') # Use hidden label to avoid repeated legends

    if drawdown_segments_for_plotting:
        plt.plot([], [], color='red', linewidth=2, label='Drawdown (>5% from Peak, until 3% Recovery)')


    plt.title("Drawdowns (>=5% from Peak, Until >=3% Recovery from Trough)")
    plt.xlabel("Days (from start of data)")
    plt.ylabel("Close Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# def PlotChange3(OHLCV):
#     # Step 1: Calculate cumulative percentage change
#     day_to_day = OHLCV['Close'].pct_change().fillna(0)
#     day_pct = [1]
#     for pct in day_to_day:
#         day_pct.append(day_pct[-1] * (1 + pct))
#     cumulative_pct = [x - 1 for x in day_pct]

#     """
#     I believe in myself, i WILL forget what am i doing here so heres the logic :
#     say changes are +3%, +8%, -4% we can't add percenetage directly, proper method is
#     Day 1: 1 + 0.03 = 1.03  Day 2: 1 + 0.08 = 1.08  Day 3: 1 - 0.04 = 0.96
#     day_pct = [1]  
#         1 * 1.03 = 1.03  
#         1.03 * 1.08 = 1.1124  
#         1.1124 * 0.96 = 1.0679
#     This gives +6.79% cumulative gain (1 - 1.0679)
#     """

def CompareAgainstIndex(OHLCV, INDEX, datefrom, dateto):
    index_domain = INDEX['Close'][datefrom : dateto]
    symbol_domain = OHLCV['Close'][datefrom : dateto]
    # since both are going to be having different prices, let us compare percent chagne rather 
    index_domain = index_domain.pct_change().fillna(0) * 100 # i dont like decimals
    symbol_domain = symbol_domain.pct_change().fillna(0) * 100 

    plt.plot(index_domain, label = 'Index Change %', color = 'green')
    plt.plot(symbol_domain, label = 'Symbol Chanfe %', color = 'blue')
    plt.legend()
    plt.grid(True)
    plt.title('Index vs Symbol')
    plt.show()
