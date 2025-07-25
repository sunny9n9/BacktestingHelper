import Alter
import pandas
# TODOS;
# change total invested amount to current invested amount and make a seperate total
# integrate folio with trade

class Holding:
    def __init__(self, name, underlying_asset, type='Equity', buy_signal=None, sell_signal=None):
        self.underlying_asset = underlying_asset # the OHLCV it follows
        self.name = name # name used for convinience to reffer to asset
        self.type = type
        self.quantity = 0
        self.total_invested = 0
        self.buy_price = []
        self.buy_quantity = []
        self.net_profit_loss = 0

        self.buy_signal = buy_signal if buy_signal is not None else self.Default_Buy
        self.sell_signal = sell_signal if sell_signal is not None else self.Default_Sell

        self.default_param1 = Alter.MovingAvg(underlying_asset, 14)
        self.default_param2 = Alter.MovingAvg(underlying_asset, 45)
        self.last_action = None 

    # intended only for execution of buy/sell, check conditions with default/custom version
    def Buy(self, i, quantity, price):
        print(f'Buy Triggered for {self.name}')
        self.total_invested += quantity * price
        self.quantity += quantity
        self.buy_price.append(price)
        self.buy_quantity.append(quantity)
        self.last_action = "buy"

    def Sell(self, i, qty, price):
        if isinstance(qty, str) and qty.lower() == 'all':
            qty = self.quantity
        if qty > self.quantity:
            raise ValueError("Not enough to sell")
        print(f'Sell Triggered for {self.name}')
        total_cost = 0
        remaining = qty

        while remaining and self.buy_quantity:
            lot = self.buy_quantity.pop(0)
            p_lot = self.buy_price.pop(0)
            if lot <= remaining:
                total_cost += lot * p_lot
                remaining -= lot
            else:
                total_cost += remaining * p_lot
                self.buy_quantity.insert(0, lot - remaining)
                self.buy_price.insert(0, p_lot)
                remaining = 0

        proceeds = qty * price
        self.net_profit_loss += proceeds - total_cost
        self.quantity       -= qty
        self.total_invested -= total_cost
        self.last_action = "sell"

    def Default_Buy(self, i):
        if self.quantity == 0 and self.default_param1.iloc[i] > self.default_param2.iloc[i] and self.last_action != "buy":
            return True
        return False

    def Default_Sell(self, i):
        if self.quantity > 0 and self.default_param1.iloc[i] < self.default_param2.iloc[i] and self.last_action != "sell":
            return True
        return False


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

class Portfolio:
    def __init__(self, cash):
        self.holdings : dict[str, Holding] = {}
        self.cash = cash
    
    def Credit(self, amount):
        self.cash += amount
    
    def Debit(self, amount):
        if amount > self.cash:
            raise NotImplementedError(f'nothing, i just like the fact there is a not implimented error')
        self.cash -= amount

    def Add(self, name, underlying_asset):
        if name not in self.holdings:
            self.holdings[name] = Holding(name, underlying_asset)
        else:
            print(f'Already Present {name}')
        # self.holdings[name].Buy(quantity, price)
    
    def Remove(self, name):
        if name not in self.holdings:
            raise ValueError(f'Could not find {name}')
        else:
            # self.holdings[name].Sell(quantity, price)
            self.holdings.pop(name)
        
    def QueryAll(self, date):
        dt = pandas.to_datetime(date)
        for name, holding in self.holdings.items():
            df = holding.underlying_asset
            if dt in df.index:
                price = df.loc[dt, 'Close']
                print(f"{name}: {holding.quantity} units for {price:.2f} is now {holding.quantity * price:.2f}")
            else:
                print(f"{name}: No data on {date}")

    def Record(self):
        raise NotImplementedError(f'Not yet implimented, maybe future')

