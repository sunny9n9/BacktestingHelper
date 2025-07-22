import matplotlib.pyplot as plt
import matplotlib.pyplot
import pandas
import Fetch
import Display
import Decomposition
import matplotlib
import Alter
import Infer
import Trade
import seaborn
# ticket = Fetch.Fetch("^NSEI", period='max')
# exit(3)
df = Fetch.ReadCSV("^NSEI")
df = df["2019-01-02" : ]
# Display.Overview(df, "Close")
# Display.PlotChange(df.tail(100))
# Decomposition.Decompose(df, "Close")
# Decomposition.AutoCorr(df)
# Decomposition.IsStationary(df)
# Decomposition.IsWhiteNoise(df)
# df = df.tail(100)
pandas.set_option("display.max_columns", None)
# sma = Alter.MovingAvg(df)
# ema = Alter.ExpMovingAvg(df)
# Display.PlotChange2(df)
# df_noresidual = Decomposition.RemoveResiduals(df, show=False)
# df_noresidual.index = df.index
# matplotlib.pyplot.plot(df['Close'], color='red', label='Original')
# matplotlib.pyplot.plot(df_noresidual, color='blue', linestyle="--", label='NoOutliers')
# matplotlib.pyplot.plot(sma, color='orange', linestyle=':', label='sma')
# matplotlib.pyplot.plot(ema, color='green', linestyle=':', label='ema')
# matplotlib.pyplot.legend()
# matplotlib.pyplot.show()

# Lets buy if 3 bULL days and sell if 3 bear, can buy 3 holding of 500, say
# nifty cant take 500 so i need percentage
# exit(0)


# Suppose df is your DataFrame with 'Open' and 'Close' columns and DateTimeIndex
# trader = Trade.Trade(df.tail(100))
# trader.run()
# trader.report()
# trader.plot_trades()
def RandomStats():
    close_to_close = Alter.PercentChange(df)
    intraday = Alter.IntradayPercentChange(df)

    temp = Alter.AddDayData(intraday)
    print(temp.head(5))
    print(temp.columns)

    desc = temp.groupby('Day').describe()
    desc.drop(columns='count', level=1, inplace=True) # this level thing seem useful
    seaborn.heatmap(desc, annot=True, cmap='coolwarm')
    plt.show()
    print(desc)

    # for i, (change, change2) in enumerate(zip(close_to_close, intraday)):
    #     plt.vlines(i, ymin=min(0, change), ymax=max(0, change), color="green" if change >= 0 else "red", linewidth=4)
    #     plt.vlines(i, ymin=min(0, change2), ymax=max(0, change2), color="#90ee90" if change2 >= 0 else "#ff9999", linewidth=4, alpha=0.6)

    # plt.show()

# let us see how much market deviates from non resudual graph
plt.plot(df['Close'], color="#215724", label="Market At")
plt.plot(Decomposition.RemoveResiduals(df, show=False), color='#4f89a9', label='Market WO RES')
# plt.plot(Alter.MovingAvg(df, 20), color="#F390BE", label='20SMA', linewidth=0.7)
# plt.plot(Alter.MovingAvg(df, 50), color="#EC579C", label='50SMA', linewidth=0.7)
# plt.plot(Alter.MovingAvg(df, 200), color="#F1167C", label='200SMA', linewidth=0.7)
# plt.plot(Alter.ExpMovingAvg(df, 50), color="#D4F658", label='50EMA', linewidth=0.7)
# plt.plot(Alter.AvgTrueRange(df), color="#EC4D4D", label='ExpMovement')
# plt.plot(Alter.AverageDirIdx(df), color="#EC4D4D", label='ADX')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

df['NonResidual'] = Decomposition.RemoveResiduals(df)

# Basic/Best Indicators
df['SMA20'] = Alter.MovingAvg(df, 20)
df['SMA50'] = Alter.MovingAvg(df, 50)
df['SMA200'] = Alter.MovingAvg(df, 200)
df['EMA17'] = Alter.ExpMovingAvg(df, 17)
df['EMA45'] = Alter.ExpMovingAvg(df, 45)

# Volatility
df['ATR'] = Alter.AvgTrueRange(df, 12)

# Signal
df['RSI'] = Alter.RelativeStrengthIndex(df, 12)
df['ADX'] = Alter.AverageDirIdx(df, 12)

class SimplerBuyLogic:
    def __call__(self, OHLC, i):
        return (94/100)*(OHLC['NonResidual'].iloc[i]) > OHLC['Close'].iloc[i]

class SimplerSellLogic:
    def __call__(self, OHLC, i):
        return OHLC['Close'].iloc[i] > (94/100)*(OHLC['NonResidual'].iloc[i])
        

buy_logic = SimplerBuyLogic()
sell_logic = SimplerSellLogic()
trial = Trade.Trade(df, 1000, 4, buy_logic=buy_logic, sell_logic=sell_logic, infinite_sell=False)
trial.run()
trial.report()
trial.plot_trades(overlay=False)

# plt.plot(df['Close'])
# plt.plot(df['EMA17'], color='green', linewidth='0.7', label='EMA17')
# plt.plot(df['EMA45'], color='yellow', linewidth='0.7', label='EMA45')
# print((df['EMA17'] < df['EMA45']).sum())
# plt.show()

# Display.PlotChange3(df)
