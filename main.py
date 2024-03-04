import pandas as pd

from dataprocessing import process_data
from functions import download_tickers_df
from secdownload import download_metrics
from sharespricedownload import download_price_and_shares

# googl pierwszy kwartał q3 2014 jest wliczany to sumy 2015 q3 q2 q1, czyli brak 2014 q4, wyjasnic dlaczego  # chyba wyjasnione


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
    #tickers_df = tickers_df[tickers_df['ticker'] == 'GOOGL']
    print(tickers_df.head())
    n = 0  # jesli ==0 odpala funkcje printujaca opisy metrics
    for i in tickers_df.index:

        cik = tickers_df['cik_str'][i]
        ticker = tickers_df['ticker'][i]
        company_name = tickers_df['title'][i]
        print(f'{ticker}: {cik}')

        download_metrics(ticker, cik, main_folder_path, headers, n)
        download_price_and_shares(ticker, cik, main_folder_path, headers)

        process_data(ticker, cik, main_folder_path)

        n += 1
