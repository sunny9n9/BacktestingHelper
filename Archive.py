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


