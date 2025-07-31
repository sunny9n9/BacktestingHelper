import matplotlib.pyplot as plt
from Alter import *
from Decomposition import *
from Display import *
from Fetch import *
from Trade import MasterTrade
from Folio import *

def CustomPlot(df):
    plt.plot(df['Close'], label='Original')
    plt.plot(df['woResiduals'], label='Non Residuals')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    df = ReadCSV('^NSEI')
    df['MA12'] = MovingAvg(df, 12)
    df['EMA12'] = MovingAvg(df, 12)

    df['woResiduals'] = RemoveResiduals(df, show=False)
    
    # AutoCorr(df)
    # PlotChange3(df)
    Decompose(df, period=39)
    # CustomPlot(df)

if __name__ == '__main__':
    main()
