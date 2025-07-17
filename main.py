import matplotlib.pyplot as plt
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
df = df.tail(300)
sma = Alter.MovingAvg(df)
ema = Alter.ExpMovingAvg(df)
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

# cash = 1500
# starting = cash
# positions = []
# max_positions = 3
# total_transactions = 0

# df["Return"] = df["Close"].pct_change()
# df["Trend"] = df["Return"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
# df["TrendSum"] = df["Trend"].rolling(3).sum() # dam sliding window simple

# buy_points = []
# sell_points = []
# sell_time_cash = []
# for i in range(3, len(df) - 1):
#     signal = df["TrendSum"].iloc[i]
#     price = df["Open"].iloc[i + 1]  # Next day open

#     # Buy signal
#     if signal == 3 and len(positions) < max_positions:
#         amount_per_buy = cash / (max_positions - len(positions))
#         positions.append((price, amount_per_buy))
#         buy_points.append(df.index[i])
#         cash -= amount_per_buy
#         total_transactions += 1
#     # Sell signal
#     elif signal == -3 and positions:
#         new_positions = []
#         for entry_price, invested in positions:
#             sell_value = invested * (price / entry_price)
#             cash += sell_value # We not working with 1 share, so we need percent calculation 
#         sell_points.append(df.index[i])
#         positions = []  # all sold
#         sell_time_cash.append(cash)
#         total_transactions += 1
# for entry_price, invested in positions:
#     last_price = df["Close"].iloc[-1]
#     cash += invested * (last_price / entry_price)
# print(f"Final Cash : {cash} and total transactions : {total_transactions}")
# print(f"percentage profit/loss : {((cash - starting)/starting) * 100}")

# df['Close'].plot()
# plt.vlines(x=buy_points, ymin=df['Close'].min(), ymax=df.loc[buy_points, 'Close'], colors="red", linestyles="--", linewidth=0.8, label="Buys")
# plt.vlines(x=sell_points, ymin=df['Close'].min(), ymax=df.loc[sell_points, 'Close'], colors="green", linestyles="--", linewidth=0.8, label="Sells")
# for i, (x, y) in enumerate(zip(sell_points, df.loc[sell_points, 'Close'])):
#     plt.text(x, y, f'{sell_time_cash[i]:.2f}', color='green', fontsize=8, ha='left', va='bottom')

# plt.legend()
# plt.show()

# sigTwo = (df["TrendSum"] == -2)
# print(sigTwo.sum())

class Trade:
    def __init__(self, df, cash=1500, max_position=3, trend_window=7):
        self.df = df.copy()
        self.cash = cash
        self.starting_cash = cash
        self.max_positions = max_position
        self.positions = []
        self.trend_window = trend_window
        self.total_transactions = 0
        self.buy_points = []
        self.sell_points = []
        self.sell_time_cash = []
        assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        self._preprocess()
        # dam its so uselessly making code long, why i need so many self.

    def _preprocess(self):
        self.df["Return"] = Alter.PercentChange(self.df)
        self.df["Trend"] = self.df["Return"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        self.df["TrendSum"] = self.df["Trend"].rolling(self.trend_window).sum()
        self.df["20SMA"] = Alter.MovingAvg(df)
        self.df["50SMA"] = Alter.MovingAvg(df, 50)
        self.df["200SMA"] = Alter.MovingAvg(df, 200)

    def buy(self, price, date):
        if len(self.positions) < self.max_positions:
            amount_per_buy = self.cash / (self.max_positions - len(self.positions)) # Cuz we not buying 1 stock, but percent
            self.positions.append((price, amount_per_buy))
            self.cash -= amount_per_buy
            assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
            self.buy_points.append(date)
            self.total_transactions += 1

    def sell(self, price, date):
        if self.positions:
            for entry_price, invested in self.positions:
                sell_value = invested * (price / entry_price)
                self.cash += sell_value
                assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
            self.positions = []
            self.sell_points.append(date)
            self.sell_time_cash.append(self.cash)
            self.total_transactions += 1
            # print(f"selling initialised, sell pint {len(self.sell_points)} and sell val {len(self.sell_time_cash)}")

    def run(self):
        for i in range(self.trend_window, len(self.df) - 1):
            signal = self.df["TrendSum"].iloc[i]
            price = self.df["Open"].iloc[i + 1]
            date = self.df.index[i]

            if signal == 3:
                self.buy(price, date)
            elif signal == -5:
                self.sell(price, date)

        # Final liquidation
        last_price = self.df["Close"].iloc[-1]
        for entry_price, invested in self.positions:
            self.cash += invested * (last_price / entry_price)
            assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        self.positions = []
        
    def report(self):
        assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        print(f"Final Cash: {self.cash:.2f}")
        print(f"Total Transactions: {self.total_transactions}")
        print(f"Profit/Loss %: {((self.cash - self.starting_cash)/self.starting_cash) * 100:.2f}%")
        # print(f"len of sell points {len(self.sell_points)} and sell values {len(self.sell_time_cash)}")
        
    def plot_trades(self):
        self.df['Close'].plot(figsize=(14, 6), title="Trend Trading Strategy")
        assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        plt.vlines(x=self.buy_points, ymin=self.df['Close'].min(), ymax=self.df.loc[self.buy_points, 'Close'],
                   colors="red", linestyles="--", linewidth=0.8, label="Buys")
        plt.vlines(x=self.sell_points, ymin=self.df['Close'].min(), ymax=self.df.loc[self.sell_points, 'Close'],
                   colors="green", linestyles="--", linewidth=0.8, label="Sells")
        
        for i, (x, y) in enumerate(zip(self.sell_points, self.df.loc[self.sell_points, 'Close'])):
            plt.text(x, y, f'{self.sell_time_cash[i]:.2f}', color='green', fontsize=8, ha='left', va='bottom')
        
        plt.legend()
        plt.grid(True)
        plt.show()

# Suppose df is your DataFrame with 'Open' and 'Close' columns and DateTimeIndex
trader = Trade(df.tail(100))
trader.run()
trader.report()
trader.plot_trades()

        