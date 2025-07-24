import pandas as pd
import matplotlib.pyplot as plt
import Folio
# df = pd.read_csv("D:\downloads\GOLD_1900-2025.csv", skiprows=2)

# pd.set_option('display.max_columns', None)
# df.columns = ['year', 'usd', 's/g', 'idk']
# df.set_index('year', inplace=True, drop=True)
# df['usd'] = df['usd'].str.replace(',', '').astype(float) # fukin commas
# df['usd'].plot()
# plt.grid(True)
# plt.show()

# print(df.head(5))

my_portfolio = Folio.Portfolio()
my_portfolio.Add('Nifty', 5, 5000)
my_portfolio.Add('Gold', 5, 5000)
my_portfolio.Sell('Gold', 'All', 5500)

my_portfolio.Query('All', 5400)

