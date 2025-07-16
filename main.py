import matplotlib.pyplot
import pandas
import Fetch
import Display
import Decomposition
import matplotlib
import Alter
# ticket = Fetch.Fetch()
df = Fetch.ReadCSV("^NSEI")
# Display.Overview(df, "Close")
# Display.PlotChange2(df.tail(100))
# Decomposition.Decompose(df, "Close")
# Decomposition.AutoCorr(df)
# Decomposition.IsStationary(df)
# Decomposition.IsWhiteNoise(df)
df = df.tail(100)
sma = Alter.MovingAvg(df)
ema = Alter.ExpMovingAvg(df)
df_noresidual = Decomposition.RemoveResiduals(df, show=False)
# df_noresidual.index = df.index
matplotlib.pyplot.plot(df['Close'], color='red', label='Original')
matplotlib.pyplot.plot(df_noresidual, color='blue', linestyle="--", label='NoOutliers')
matplotlib.pyplot.plot(sma, color='orange', linestyle=':', label='sma')
matplotlib.pyplot.plot(ema, color='green', linestyle=':', label='ema')
matplotlib.pyplot.legend()
matplotlib.pyplot.show()

# Lets buy if 3 bULL days and sell if 3 bear, can buy 3 holding of 500, say
# nifty cant take 500 so i need percentage

cash = 1500
positions = []
max_positions = 3

df["Return"] = df["Close"].pct_change()
df["Trend"] = df["Return"].apply(lambda x: 1 if x > 0 else -1)
df["TrendSum"] = df["Trend"].rolling(3).sum()


for i in range(3, len(df) - 1):
    signal = df["TrendSum"].iloc[i]
    price = df["Open"].iloc[i + 1]  # Next day open

    # Buy signal
    if signal == 3 and len(positions) < max_positions:
        amount_per_buy = cash / (max_positions - len(positions))
        positions.append((price, amount_per_buy))
        cash -= amount_per_buy

    # Sell signal
    elif signal == -3 and positions:
        new_positions = []
        for entry_price, invested in positions:
            sell_value = invested * (price / entry_price)
            cash += sell_value
        positions = []  # all sold
for entry_price, invested in positions:
    last_price = df["Close"].iloc[-1]
    cash += invested * (last_price / entry_price)
print(cash, "llllllllllllllllllllllllllll")

