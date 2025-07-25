import pandas
import matplotlib.pyplot as plt
import Alter
import Fetch
import Folio
import Trade
from types import MethodType

df = Fetch.ReadCSV('^NSEI')
df2 = Fetch.ReadCSV('NIFTYBEES.NS')
df3 = Fetch.ReadCSV('^NSEBANK')

my_portfolio = Folio.Portfolio(5000)
my_portfolio.Add('Nifty50', df)
my_portfolio.Add('NiftyETF', df2)
my_portfolio.Add('BankNifty', df3)

my_portfolio.QueryAll('2024-06-06')
my_portfolio.Credit(500000)

trade = Trade.MasterTrade()
trade.Add('mp1', my_portfolio)
trade.Emulate('2020-01-01', '2025-07-01')
trade.portfolio['mp1'].QueryAll('2024-06-06')
# trade.portfolio['mp1'].holdings['Nifty50'].Query(52000)
# trade.portfolio['mp1'].holdings['BankNifty'].Query(52000)
# trade.portfolio['mp1'].holdings['NiftyETF'].Query(52000)
