from statsmodels.tsa.seasonal import STL
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

def Decompose(OHLCV, field, period = 30, show=True):
    stl = STL(OHLCV[field], period=period, robust=True)
    results = stl.fit()

    seasonal = results.seasonal
    trend = results.trend
    residuals = results.resid
    
    if show:
        results.plot()
        plt.show()
    return seasonal, trend, residuals



def IsWhiteNoise(OHLCV, field = "Close"):
    seasonal, trend, residuals = Decompose(OHLCV, field, show=False)
    lb_result = acorr_ljungbox(residuals.dropna(), lags=[10], return_df=True)
    print(lb_result)

def IsStationary(OHLCV, field = "Close"):
    sesonal, trend, residuals = Decompose(OHLCV, field, show=False)

    adf_result = adfuller(residuals.dropna())
    
    print(f"ADF Statistic: {adf_result[0]}")
    print(f"p-value: {adf_result[1]} \n\n p-val < 0.05 == stationary(likeyly)")

def AutoCorr(OHLCV, field = "Close", lag = 21):
    series = OHLCV[field]
    fig, axes = plt.subplots(2, 1)
    plot_acf(series, lags=lag, ax=axes[0])
    plot_pacf(series, lags=lag, ax=axes[1])
    axes[0].set_title("Autocorrelation")
    axes[1].set_title("Partial Autocorrelation")

    plt.tight_layout()
    plt.show()

def RemoveResiduals(OHLCV, field = "Close", period = 30, show = True):
    seasonal, trend, residuals = Decompose(OHLCV, field, show=False)

    new_series = pd.Series(seasonal + trend, index=OHLCV.index)
    new_series.index = OHLCV.index
    if show:
        new_series.plot()   
        plt.show()
    return new_series