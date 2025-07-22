import matplotlib.pyplot as plt
import Alter
import Decomposition

def default_buy_logic(OHLC, i):
    return False  # Never buys

def default_sell_logic(OHLC, i):
    return False  # Never sells

class Trade:
    def __init__(self, df, cash=1500, max_position=3, trend_window=7, buy_logic=None, sell_logic=None, infinite_sell=False):
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
        self.infinite_sell = infinite_sell
        self.buy_logic = buy_logic if buy_logic else default_buy_logic
        self.sell_logic = sell_logic if sell_logic else default_sell_logic
        assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        self._preprocess()
        # dam its so uselessly making code long, why i need so many self.

        # DAM this is getting out of hand, kinda like callback, if the buy_logic function
        # needs some data from Trade class, it will get that using this attach call
        if hasattr(buy_logic, "attach"):
            self.buy_logic.attach(self) #from other side we are callin ourself?! waht?
        if hasattr(sell_logic, "attach"):
            self.sell_logic.attach(self)

    def _preprocess(self):
        self.df["Return"] = Alter.PercentChange(self.df)
        self.df["Trend"] = self.df["Return"].apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
        self.df["TrendSum"] = self.df["Trend"].rolling(self.trend_window).sum()
        self.df["20SMA"] = Alter.MovingAvg(self.df)
        self.df["50SMA"] = Alter.MovingAvg(self.df, 50)
        self.df["200SMA"] = Alter.MovingAvg(self.df, 200)

    def buy(self, price, date):
        if len(self.positions) < self.max_positions:
            amount_per_buy = self.cash / (self.max_positions - len(self.positions)) # Cuz we not buying 1 stock, but percent
            self.positions.append((price, amount_per_buy)) # (curr_trading_price, amount_invested)
            self.cash -= amount_per_buy
            assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
            self.buy_points.append(date)
            self.total_transactions += 1
        # else:
        #     print(f"potential buy missed at {date}")

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

        elif self.infinite_sell:
            self.sell_points.append(date)
            self.sell_time_cash.append(self.cash)
            self.total_transactions += 1
            # print(f"selling initialised, sell pint {len(self.sell_points)} and sell val {len(self.sell_time_cash)}")

    def run(self):
        for i in range(self.trend_window, len(self.df) - 1):
            next_open_price = self.df["Open"].iloc[i + 1]
            date = self.df.index[i + 1]

            if self.sell_logic(self.df, i):
                self.sell(next_open_price, date)

            if self.buy_logic(self.df, i): 
                self.buy(next_open_price, date)

        # Final liquidation at end
        last_price = self.df["Close"].iloc[-1]
        for entry_price, invested in self.positions:
            self.cash += invested * (last_price / entry_price)
        # *Record* that liquidation as a sell on the final bar:
        final_date = self.df.index[-1]
        self.sell_points.append(final_date)
        self.sell_time_cash.append(self.cash)
        self.total_transactions += 1

        # clear positions
        self.positions = []


        
    def report(self):
        assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        print(f"Final Cash: {self.cash:.2f}")
        print(f"Total Transactions: {self.total_transactions}")
        print(f"Profit/Loss %: {((self.cash - self.starting_cash)/self.starting_cash) * 100:.2f}%")
        # print(f"len of sell points {len(self.sell_points)} and sell values {len(self.sell_time_cash)}")
        
    def plot_trades(self, overlay = False):
        self.df['Close'].plot(figsize=(14, 6), title="Trend Trading Strategy")
        assert isinstance(self.cash, (int, float)), f"Cash is wrong type: {type(self.cash)}"
        plt.vlines(x=self.buy_points, ymin=self.df['Close'].min(), ymax=self.df.loc[self.buy_points, 'Close'],
                   colors="red", linestyles="--", linewidth=0.8, label="Buys")
        plt.vlines(x=self.sell_points, ymin=self.df['Close'].min(), ymax=self.df.loc[self.sell_points, 'Close'],
                   colors="green", linestyles="--", linewidth=0.8, label="Sells")
        
        for i, (x, y) in enumerate(zip(self.sell_points, self.df.loc[self.sell_points, 'Close'])):
            plt.text(x, y, f'{self.sell_time_cash[i]:.2f}', color='green', fontsize=10, ha='left', va='bottom')
        plt.legend()
        plt.grid(True)
        plt.show()
