import yfinance as yf
import requests
import pandas as pd
import datetime
from matplotlib import pyplot as plt

import functions


def pandas_df_display_options():
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 400)


def correct_errors(df, tic):
    # correct data errors from sec
    if tic == 'NVDA':
        mapping = ['2008-01-27', '2009-01-25', '2009-04-26', '2009-07-26', '2009-10-25', '2010-05-02', '2010-08-01']
        df['shares'] = df.apply(lambda x: x['shares'] * 1000 if x['end'] in pd.to_datetime(mapping) else x['shares'], axis=1)

    return df


pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
tickers_df = functions.download_tickers_df(headers)

tickers_df = tickers_df[tickers_df['ticker'] == 'NVDA']
for i in tickers_df.index[[0]]:
    cik = tickers_df['cik_str'][i]
    ticker = tickers_df['ticker'][i]
    company_name = tickers_df['title'][i]
    print(f'{ticker}: {cik}')
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    print(facts['facts']['us-gaap']['WeightedAverageNumberOfDilutedSharesOutstanding'])
    sharedf = pd.DataFrame(facts['facts']['us-gaap']['WeightedAverageNumberOfDilutedSharesOutstanding']['units']['shares'])
    sharedf = sharedf.dropna(subset='frame')
    sharedf['end'] = pd.to_datetime(sharedf['end'])
    sharedf['filed'] = pd.to_datetime(sharedf['filed'])
    sharedf = sharedf.sort_values(by='filed').reset_index(drop=True)
    #print(sharedf)
    min_date = sharedf['filed'].min()


# Download shares outstanding data
    stock_info = yf.Ticker(ticker)
    pricedf = stock_info.history(period='1d', start=min_date, end=datetime.date.today())
    pricedf = pricedf.reset_index()
    pricedf = pricedf.rename(columns={'Date': 'date', 'Close': 'close', 'Volumne': 'volume', 'Dividends': 'dividends', 'Stock Splits': 'stock_splits'})
    pricedf = pricedf.drop(columns=['Open', 'High', 'Low'])
    pricedf['date'] = pd.to_datetime(pricedf['date'])
    pricedf['date'] = pricedf['date'].dt.date
    pricedf['date'] = pd.to_datetime(pricedf['date'])
    #print(pricedf.head(10))
    #print(pricedf.tail(10))
    stock_split_df = pricedf[pricedf['stock_splits'] > 0][['date', 'stock_splits']]
    #print(stock_split_df)

    sharedf = pd.merge_asof(sharedf, stock_split_df, left_on='filed', right_on='date', direction='forward')

    sharedf['stock_splits'] = sharedf['stock_splits'].fillna(method='bfill')
    sharedf['shares'] = sharedf.apply(lambda x: x['val'] if pd.isna(x['stock_splits']) else x['val'] * x['stock_splits'], axis=1)
    sharedf['shares'] = sharedf['shares'] / 1000000
    sharedf = sharedf.sort_values(by='end')
    print(sharedf.head())
    sharedf = correct_errors(sharedf, ticker)

    print(sharedf)



#tickerDf['Date'] = tickerDf['Date'].dt.date
#print(tickerDf)
#
fig, ax = plt.subplots()
#
ax.plot(sharedf['end'], sharedf['shares'])
plt.show()

# 45  2020-01-27 2020-04-26                                622000000         2021-05-26  2021      Q1
# 46  2020-04-27 2020-07-26                               2504000000         2021-08-20  2021      Q2