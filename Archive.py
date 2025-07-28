# I keep forgetting this exists and i delete stuff ::CRY::
# Old Trade Classs' Buy and Sell logic
class BuyLogic:
    def __init__(self):
        self.has_been_30 = False
        self.trade = None

    def attach(self, trade): # Callback ??
        self.trade = trade

    def __call__(self, OHLC, i):
        if not self.has_been_30 and OHLC['RSI'].iloc[i] <= 30:
            self.has_been_30 = True
        if self.has_been_30 and OHLC['RSI'].iloc[i] >= 30:
            self.has_been_30 = False
            return True
        return False

class SellLogic:
    def __init__(self):
        self.has_been_70 = False
        self.trade = None
        
    def attach(self, trade): # Yeah we smart now. We use callbacks
        self.trade = trade

    def __call__(self, OHLC, i):
        # if not self.has_been_70 and OHLC['RSI'].iloc[i] >= 70:
        #     self.has_been_70 = True
        # return self.has_been_70 and OHLC['RSI'].iloc[i] <= 70
    # and self.trade.positions[amount_per_buy] < OHLC['Close'].iloc[i-1] * len(positions)
                                                                        # look at this smart ppl stuff
        return OHLC['EMA17'].iloc[i] < OHLC['EMA45'].iloc[i]

    def DefaultBuyQuantity(self, i, price, portfolio_cash, allow_fractions):
        '''this function manages the following concepts:
        1. Which fund to use to buy 
        2. How much to buy'''
        
        # 1. Where to get money from
        remaining = portfolio_cash
        if self.dedicated_funds > 0:
            pot = self.dedicated_funds
            will_deduct_from_dedicated = True
        else:
            pot = portfolio_cash
            will_deduct_from_dedicated = False

        if will_deduct_from_dedicated :
            self.dedicated_funds = 0
            # THIS WILL BE responsible for updating portfolio cash amount 
        else:
            remaining = 0

        # 2. How much money to use
        buy_qty = pot / price
        if not allow_fractions:
            buy_qty = int(buy_qty)
        
        return buy_qty, remaining # this is how much i need to buy
    
    def Buy(self, i, price, portfolio_cash, allow_fractions):
        quantity, portfolio_cash = self.DefaultBuyQuantity(i, price, portfolio_cash, allow_fractions)
        if quantity <= 0:
            return portfolio_cash
        cost = quantity * price
        if self.dedicated_funds > 0:
            self.dedicated_funds -= cost
        else:
            portfolio_cash -= cost

        self.total_invested += (quantity * price)
        self.quantity += quantity
        self.buy_price.append(price)
        self.buy_quantity.append(quantity)
        self.buy_points.loc[self.underlying_asset.index[i]] = price
        self.last_action = "buy"
        print(f'BUY for {price} @ {self.total_invested} ###{portfolio_cash}')
        return portfolio_cash

    # intended only for execution of buy/sell, check conditions with default/custom version
    def Buy(self, i, quantity, price):
        # print(f'Buy Triggered for {self.name}')
        self.total_invested += quantity * price
        self.quantity += quantity
        self.buy_price.append(price)
        self.buy_points.loc[self.underlying_asset.index[i]] = price
        self.buy_quantity.append(quantity)
        # self.dedicated_funds = 
        # self.balances[self.underlying_asset.index[i]] = self.buy_price[-1]*self.buy_quantity[-1] # RECORD
        self.last_action = "buy"

    def Sell(self, i, qty, price):
        if isinstance(qty, str) and qty.lower() == 'all':
            qty = self.quantity
        if qty > self.quantity:
            raise ValueError("Not enough to sell")
        # print(f'Sell Triggered for {self.name}')
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
        self.sell_points[self.underlying_asset.index[i]] = price
        # self.balances[self.underlying_asset.index[i]] = self.buy_price[-1]*self.buy_quantity[-1] # RECORD
        proceeds = qty * price
        self.net_profit_loss += proceeds - total_cost
        self.quantity -= qty
        self.total_invested -= total_cost
        self.last_action = "sell"

