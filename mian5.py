import Display
import Fetch
import Alter
import pandas

df = Fetch.ReadCSV('118663_Nippon_India_Gold_Savings_Fund_-_Direct_Plan_Growth_Plan_-_Growth_Option')
df2 = Fetch.ReadCSV('^NSEI')

Display.CompareAgainstIndex(df, df2, pandas.to_datetime('2014-01-02'), pandas.to_datetime('2025-01-02'))
