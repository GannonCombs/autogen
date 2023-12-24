# filename: crypto_ytd_gains.py

import yfinance as yf
import pandas as pd
from datetime import datetime

# list of the top ten Layer 1 cryptos
symbols = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'ADA-USD', 'DOT-USD', 'SOL-USD', 'AVAX-USD', 'XRP-USD', 'ATOM-USD', 'NEAR-USD']

# get today's date
today = datetime.today().strftime('%Y-%m-%d')

# get the start date of this year
start_date = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')    

# create a list to store DataFrames
df_list = []

# loop through the list of symbols
for symbol in symbols:
    # download the cryptocurrency data
    data = yf.download(symbol, start=start_date, end=today)

    # check if data is empty
    if data.empty:
        print(f"No data available for {symbol} from Yahoo Finance.")     
        continue

    # calculate YTD gain
    ytd_gain = ((data['Close'][-1] - data['Open'][0]) / data['Open'][0]) * 100

    # create a DataFrame for each symbol and store in list
    df_list.append(pd.DataFrame({'Symbol': [symbol], 'YTD': [ytd_gain]}))
# concatenate all the DataFrames
df_ytd = pd.concat(df_list, ignore_index=True)

print(df_ytd)