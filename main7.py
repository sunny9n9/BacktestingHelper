from Includes import *
import pandas
import yfinance

def get_data():
    nifty_50 = yfinance.download("^NSEI", period='max', )
    pandas.set_option('display.max_columns', None)
    print(nifty_50)

if __name__ == '__main__':
    get_data()
# And hence he gave up and accepted the power of Database(s)
