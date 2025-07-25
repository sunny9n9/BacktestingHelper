import pandas as pd
import matplotlib.pyplot as plt
import Folio
import Fetch
import Trade
import Alter
# df = pd.read_csv("D:\downloads\GOLD_1900-2025.csv", skiprows=2)

pd.set_option('display.max_columns', None)
# df.columns = ['year', 'usd', 's/g', 'idk']
# df.set_index('year', inplace=True, drop=True)
# df['usd'] = df['usd'].str.replace(',', '').astype(float) # fukin commas
# df['usd'].plot()
# plt.grid(True)
# plt.show()

# print(df.head(5))

# my_portfolio = Folio.Portfolio()
# my_portfolio.Add('Nifty', 5, 5000)
# my_portfolio.Add('Gold', 5, 5000)
# my_portfolio.Sell('Gold', 'All', 5500)

# my_portfolio.Query('All', 5400)

# banknifty = Fetch.Fetch('^NSEBANK')
# niftyNXT50 = Fetch.Fetch(146381, True)
# print(banknifty.head(5))
# print(niftyNXT50.head(5))

# df = Fetch.ReadCSV('118663_Nippon_India_Gold_Savings_Fund_-_Direct_Plan_Growth_Plan_-_Growth_Option')
# print(df.head())
df = Fetch.ReadCSV('NIFTYBEES.NS')
print(df.head(5))
df['SMA14'] = Alter.MovingAvg(df, 14)
df['SMA45'] = Alter.MovingAvg(df, 45)

plt.plot(df['Close'])
plt.plot(df['SMA14'])
plt.plot(df['SMA45'])
plt.grid(True)
plt.show()

def buy_logic(df, i):
    return df['SMA14'].iloc[i] > df['SMA45'].iloc[i]

def sell_logic(df, i):
    return df['SMA14'].iloc[i] < df['SMA45'].iloc[i]

trade = Trade.Trade(df, 5000, 5, buy_logic=buy_logic, sell_logic=sell_logic)
trade.run()
trade.plot_trades()
trade.report()