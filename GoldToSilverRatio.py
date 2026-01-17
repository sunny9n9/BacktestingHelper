import pandas
from Includes import *
import matplotlib.pyplot as plt
import seaborn as sns

gold = 'GC=F'
silver = 'SI=F'
usd_inr = 'USDINR=X'
# why tf are you returning Oz, WHY
OZ_TO_G = 31.1034768

def get_data():
    Fetch(gold, period='max')
    Fetch(silver, period='max')
    Fetch(usd_inr, period='max')

def make_df():
    df_gold = ReadCSV(gold)
    df_silver = ReadCSV(silver)
    df_conversion = ReadCSV(usd_inr)
    # need to align by date
    merged = df_gold.join(df_silver, lsuffix='_gold', rsuffix='_silver')
    merged = merged.join(df_conversion, rsuffix='_excRate')

    print(merged.head())
    cleaned = pandas.DataFrame({'Close_gold' : merged['Close_gold'], 'Close_silver' : merged['Close_silver'], 'Close' : merged['Close']}, index=merged.index)
    cleaned['Gold_INR_SPOT'] = cleaned['Close_gold'] * cleaned['Close'] / OZ_TO_G
    cleaned['Silver_INR_SPOT'] = cleaned['Close_silver'] * cleaned['Close'] / OZ_TO_G

    cleaned['Gold_INR_SPOT_pct'] = PercentChange(cleaned, 'Gold_INR_SPOT')
    cleaned['Silver_INR_SPOT_pct'] = PercentChange(cleaned, 'Silver_INR_SPOT')

    cleaned = cleaned.dropna()
    cleaned["Gold_INR_SPOT_norm"] = cleaned["Gold_INR_SPOT"] / cleaned["Gold_INR_SPOT"].iloc[0] * 100
    cleaned["Silver_INR_SPOT_norm"] = cleaned["Silver_INR_SPOT"] / cleaned["Silver_INR_SPOT"].iloc[0] * 100
    
    print(cleaned['Silver_INR_SPOT'].head())
    return cleaned

def plot(df):
    fig, axes = plt.subplots(3, 1, height_ratios=[3, 3, 2])
    
    axes[0].plot(df['Gold_INR_SPOT'], label='gold', color='yellow')
    axes[1].plot(df['Silver_INR_SPOT'], label='silver', color='grey')
    axes[2].plot(df['Gold_INR_SPOT']/df['Silver_INR_SPOT'], label='ratio', color='red')
    
    axes[0].grid(True)
    axes[1].grid(True)
    axes[2].grid(True)

    axes[0].legend(loc='upper left')
    axes[1].legend(loc='upper left')
    axes[2].legend(loc='upper left')
    plt.show()

def random_stats(df):
    sns.heatmap(df.corr(), cmap='coolwarm')
    plt.show()
    CompareAgainstIndex(df, ReadCSV('^NSEI'), pandas.to_datetime('01-01-2010'), pandas.to_datetime('17-12-2025'), 'Gold_INR_SPOT')
if __name__ == '__main__':
    #plot(make_df()) 
    get_data()
    plot(make_df())