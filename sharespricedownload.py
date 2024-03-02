import yfinance as yf
import requests
import pandas as pd
import datetime
from matplotlib import pyplot as plt


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


def download_price_and_shares(ticker, cik, main_folder_path, headers):
    # niektore firmy nie posiadaja pozycji WeightedAverageNumberOfDilutedSharesOutstanding ktora uwzglednia stock
    # options, convertible bonds, or warrants (jesli pozycji nie ma to wowczas wskazane zmienne nie wystepuja?)
    share_types = ['WeightedAverageNumberOfDilutedSharesOutstanding', 'CommonStockSharesOutstanding']
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    #print(facts['facts']['us-gaap']['WeightedAverageNumberOfDilutedSharesOutstanding'])

    try:
        share_type = share_types[0]
        sharedf = pd.DataFrame(facts['facts']['us-gaap'][share_type]['units']['shares'])
    except KeyError:  # gdy WeightedAverageNumberOfDilutedSharesOutstanding nei wystepuje ddla tickera
        share_type = share_types[1]
        sharedf = pd.DataFrame(facts['facts']['us-gaap'][share_type]['units']['shares'])

    sharedf = sharedf.dropna(subset='frame')
    sharedf['end'] = pd.to_datetime(sharedf['end'])
    sharedf['filed'] = pd.to_datetime(sharedf['filed'])
    sharedf = sharedf.sort_values(by='filed').reset_index(drop=True)
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
    stock_split_df = pricedf[pricedf['stock_splits'] > 0][['date', 'stock_splits']]

    sharedf = pd.merge_asof(sharedf, stock_split_df, left_on='filed', right_on='date', direction='forward')

    sharedf['stock_splits'] = sharedf['stock_splits'].bfill()
    sharedf['shares'] = sharedf.apply(lambda x: x['val'] if pd.isna(x['stock_splits']) else x['val'] * x['stock_splits'], axis=1)
    sharedf['shares'] = sharedf['shares'] / 1000000
    sharedf = sharedf.sort_values(by='end')
    sharedf = correct_errors(sharedf, ticker)
    sharedf = sharedf.rename(columns={'val': share_type})
    try:
        sharedf = sharedf.drop(['start', 'accn', 'fy', 'fp', 'form', 'frame', 'date'], axis=1)
    except KeyError:
        sharedf = sharedf.drop(['accn', 'fy', 'fp', 'form', 'frame', 'date'], axis=1)

    pricedf.to_csv(f'{main_folder_path}metrics\\{ticker}_price.csv', index=False)
    sharedf.to_csv(f'{main_folder_path}metrics\\{ticker}_shares.csv', index=False)

    # fig = plt.figure()
    # plt.plot(sharedf['end'], sharedf['shares'])
    # plt.title(ticker)
    # plt.show()


#pd.reset_option('display.max_rows')
#pd.reset_option('display.max_columns')
#pd.reset_option('display.width')
#pd.reset_option('display.float_format')
#pd.reset_option('display.max_colwidth')
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_colwidth', 40)
#pd.set_option('display.width', 400)
#main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
#headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
#ticker = 'GOOGL'
#cik = '0001652044'
#download_price_and_shares(ticker, cik, main_folder_path, headers)

