import pandas as pd

from functions import download_tickers_df
from secdownload import download_metrics
from sharespricedownload import download_price_and_shares

# CommonStockSharesOutstanding -- prawdopodobnie te shares dla googl

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


if __name__ == '__main__':
    pandas_df_display_options()
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
    tickers_df = download_tickers_df(headers)
    # tickers_df.to_excel(f'{main_folder_path}tickers.xlsx')
    tickers_df = tickers_df[tickers_df['ticker'].isin(['AAPL', 'AMZN', 'GOOGL', 'META', 'NVDA', 'TSLA'])]
    print(tickers_df.head())
    n = 0  # jesli ==0 odpala funkcje printujaca opisy metrics
    for i in tickers_df.index:

        cik = tickers_df['cik_str'][i]
        ticker = tickers_df['ticker'][i]
        company_name = tickers_df['title'][i]
        print(ticker)

        download_metrics(ticker, cik, main_folder_path, headers, n)
        download_price_and_shares(ticker, cik, main_folder_path, headers)

        n += 1
