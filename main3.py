import pandas
import matplotlib.pyplot as plt
from Fetch import *
from Folio import *
from Trade import *
from Decomposition import *
from types import MethodType
# from pycallgraph2 import PyCallGraph
# from pycallgraph2.output import GraphvizOutput

def CustomBuy(self, i):
    df = self.underlying_asset
    if i < 45:
        return False

    if not hasattr(self, 'custom_param1'):
        ts  = df.index[i]
        ago = ts - pandas.DateOffset(days=45)
        pos_ago = df.index.get_indexer([ago], method='pad')[0]
        if pos_ago < 0:
            return False

        lookback = i - pos_ago
        self.custom_param1 = (self.default_param1 - self.default_param1.shift(lookback)).pct_change().fillna(0)
    print(f'for the value of {self.custom_param1.iloc[i]}')
    return self.custom_param1.iloc[i] <= -0.08

def CustomSell(self, i):
    if not 0 <= i + 45 < len(self.underlying_asset.index):
        return False
    if not hasattr(self, 'custom_param2'):
        self.custom_param2 = self.custom_param1.copy()
        self.custom_param3 = RemoveResiduals(self.underlying_asset, show=False)
    return self.custom_param1.iloc[i+45] >= 0.1 

def main():
    
    df = ReadCSV('^NSEI')
    df2 = ReadCSV('NIFTYBEES.NS')
    df3 = ReadCSV('^NSEBANK')

    my_portfolio = Portfolio(0)
    my_portfolio.Add('Nifty50', df)
    my_portfolio.Add('NiftyETF', df2)
    my_portfolio.Add('BankNifty', df3)

    # my_portfolio.QueryAll('2024-06-06')
    # my_portfolio.Credit(0)
    # my_portfolio.holdings['Nifty50'].dedicated_funds = 25000
    my_portfolio.holdings['NiftyETF'].dedicated_funds = 1000
    # my_portfolio.holdings['BankNifty'].dedicated_funds = 150000

    nifty = my_portfolio.holdings['Nifty50']
    # nifty.buy_signal = MethodType(CustomBuy, nifty)
    # nifty.sell_signal = MethodType(CustomSell, nifty)

    trade = MasterTrade()
    trade.Add('mp1', my_portfolio)
    trade.Emulate('2019-01-01', '2025-01-07', True)
    trade.portfolio['mp1'].QueryAll('2024-06-06')

if __name__ == '__main__':
    main()