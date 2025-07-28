# The Holding class stores per asset data, and portfolio class
# is intended to be a group of holdings though functions' interactions are
# rather irritiaing, needs cleanup
import Alter
import pandas
import matplotlib.pyplot as plt

# TODO: Make Defaults Hidden Functions
__all__ = [
    'Holding', 'Portfolio'
]

class Holding:
    def __init__(self, name, underlying_asset, type='Equity', buy_signal=None, sell_signal=None):
        self.underlying_asset = underlying_asset # the OHLCV it follows
        self.name = name # name used for convinience to reffer to asset
        self.type = type
        self.dedicated_funds = 0
        self.quantity = 0
        self.total_invested = 0
        self.buy_points = pandas.Series(dtype=float) # for plotting only
        self.buy_price = [] # cost‐basis FIFO list(temp records)
        self.buy_quantity = []    
        self.sell_points = pandas.Series(dtype=float)
        self.sell_quantity = []
        self.balances = pandas.Series(dtype=float)
        self.net_profit_loss = 0

        self.buy_signal = buy_signal if buy_signal is not None else self.Default_Buy
        self.sell_signal = sell_signal if sell_signal is not None else self.Default_Sell

        self.default_param1 = Alter.MovingAvg(underlying_asset, 14)
        self.default_param2 = Alter.MovingAvg(underlying_asset, 45)
        self.last_action = None

    def DefaultBuyQuantity(self, i, price, portfolio_cash, allow_fractions):
        '''How much quantity to buy (default == all)'''
        pot = self.dedicated_funds if self.dedicated_funds > 0 else portfolio_cash
        raw_qty = pot / price
        if not allow_fractions:
            raw_qty = int(raw_qty)
        return raw_qty

    def DefaultSellQuantity(self, i):
        '''Decide how many shares to sell (default = all)'''
        qty = self.quantity  # default = sell everything
        total_cost = 0
        remaining  = qty

        while remaining and self.buy_quantity:
            lot   = self.buy_quantity.pop(0)
            p_lot = self.buy_price.pop(0)
            if lot <= remaining:
                total_cost += lot * p_lot
                remaining  -= lot
            else:
                total_cost += remaining * p_lot
                # put back the unused portion
                self.buy_quantity.insert(0, lot - remaining)
                self.buy_price.insert(0, p_lot)
                remaining = 0

        return qty, total_cost

    def Buy(self, i, price, portfolio_cash, allow_fractions=False):
        '''Buy is more of a Logging function. To change how much it buys
        override the DefaultBuyQuantity function and to change when it buys
        override the Default_Buy method'''
        qty = self.DefaultBuyQuantity(i, price, portfolio_cash, allow_fractions)
        if qty <= 0:
            return portfolio_cash  # no funds, no trade

        # portfolio_cash = portfolio_cash
        cost = qty * price
        # debit the real cash pots:
        if self.dedicated_funds > 0:
            self.dedicated_funds -= cost
        else:
            portfolio_cash = 0        # mutates portfolio.cash
        # now record the trade:
        self.total_invested   += cost
        self.quantity          += qty
        self.buy_price.append(price)
        self.buy_quantity.append(qty)
        self.buy_points.loc[self.underlying_asset.index[i]] = price
        self.last_action = "buy"

        return portfolio_cash


    def Sell(self, i, price, portfolio_cash, allow_fractions):
        '''Sell is more of a Logging function. To change how much it sells
        override the DefaultSellQuantity function and to change when it sells
        override the Default_Sell method'''
        qty, total_cost = self.DefaultSellQuantity(i)
        if qty <= 0:
            return portfolio_cash

        self.sell_points.loc[self.underlying_asset.index[i]] = price

        proceeds = qty * price
        self.net_profit_loss += proceeds - total_cost
        self.quantity -= qty
        self.total_invested -= total_cost
        self.last_action = "sell"

        if self.dedicated_funds > 0:
            self.dedicated_funds += proceeds
        else:
            portfolio_cash += proceeds
        print(f'SELL for {price} @total of {total_cost}')
        return portfolio_cash

    def Default_Buy(self, i):
        '''HandleWithCare, half the problem is here'''
        if self.quantity == 0 and self.default_param1.iloc[i] > self.default_param2.iloc[i] and self.last_action != "buy":
            return True
        return False

    def Default_Sell(self, i):
        '''HandleWithCare, other half of problem is here'''
        if self.quantity > 0 and self.default_param1.iloc[i] < self.default_param2.iloc[i] and self.last_action != "sell":
            return True
        return False

    def Plot(self):
        '''Plots all buy and sell moments on chart along with the price'''
        self.underlying_asset['Close'].plot()
        plt.scatter(self.buy_points.index, self.buy_points.values, marker='^', color='green', label='Buy', s=100)
        plt.scatter(self.sell_points.index, self.sell_points.values, marker='v', color='red', label='Sell', s=100)
        for dt, price, bal in zip(self.sell_points.index, self.sell_points.values, self.balances):
            plt.text(dt, price, f"{bal:.2f}", fontsize=9, ha="left", va="bottom")
        plt.legend()
        plt.show()
        
    def Query(self, price):
        if self.quantity == 0:
            avg_price = 0
        else:
            total_qty_price = sum(p * q for p, q in zip(self.buy_price, self.buy_quantity))
            avg_price = total_qty_price / self.quantity

        print(f'Asset: {self.name}')
        print(f'Total invested amount: {self.total_invested:.2f}')
        print(f'Average buy price: {avg_price:.2f}')
        print(f'Current price: {price:.2f}')
        print(f'Current holding quantity: {self.quantity}')
        print(f'Current market value: {price * self.quantity:.2f}')
        print(f'Unrealized P/L: {price * self.quantity - self.total_invested:.2f}')
        print(f'Net realized P/L: {self.net_profit_loss:.2f}')
        # print(f'% P/L: {(self.net_profit_loss)/ self.dedicated_funds}')

class Portfolio:
    def __init__(self, cash):
        self.holdings : dict[str, Holding] = {}
        self.cash = cash # will need to be maintained manually, i won't push it ever by default
    
    def Credit(self, amount):
        '''Add amount to portfolio holding, which is kind of non invested 
        use anywhere / opportunity fund(s)'''
        self.cash += amount
    
    def Debit(self, amount):
        '''Take money from portfolio (opportunity fund) to invest somewhere'''
        if amount > self.cash:
            print(f'nothing, i just like the fact there is a not implimented error, selling all')
        self.cash -= amount

    def Add(self, name, underlying_asset):
        '''Add new asset/holding to portfolio'''
        if name not in self.holdings:
            self.holdings[name] = Holding(name, underlying_asset)
        else:
            print(f'Already Present {name}')
        # self.holdings[name].Buy(quantity, price)
    
    def Remove(self, name):
        '''Delete a Holding from portfolio
        I should see how to delete class instance or python does that ?'''
        if name not in self.holdings:
            raise ValueError(f'Could not find {name}')
        else:
            # self.holdings[name].Sell(quantity, price)
            self.holdings.pop(name)
        
    def Allocate(self, allocations: dict[str, float]):
        '''To allocate funds to different holding(s) {dedicated funds}'''
        for name, holding in self.holdings.items():
            if name in allocations:
                holding.dedicated_funds = float(allocations[name])
            else:
                # default to zero or leave existing
                holding.dedicated_funds = 0.0

    def QueryAll(self, date):
        dt = pandas.to_datetime(date)
        for name, holding in self.holdings.items():
            df = holding.underlying_asset
            if dt in df.index:
                price = df.loc[dt, 'Close']
                print(f"{name}:")
                holding.Query(price)
                holding.Plot()
                print()
            else:
                print(f"{name}: No data on {date}")

    def Record(self):
        raise NotImplementedError(f'Not yet implimented, maybe future')

