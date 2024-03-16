import pandas as pd

from currentdata import current_data
from dataprocessing import process_data
from functions import TickerType, pandas_df_display_options, download_tickers_df
from secdownload import download_metrics
from sharespricedownload import download_price_and_shares

# nowe wskazniki
# second y axis
# subdropdown

# googl pierwszy kwartał q3 2014 jest wliczany to sumy 2015 q3 q2 q1, czyli brak 2014 q4, wyjasnic dlaczego  # chyba wyjasnione

#Visa sahres nie do namierzenia
#AVGO brak nowego net income
# BABA i BIDU brak danych
# COST rozjazd net income i revenue
# MCD spadki shares dla 3 okresow
# NKE brak 2 dat w 2011
# PFE brak revenue dla 2014-2018


if __name__ == '__main__':
    pandas_df_display_options()
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
    tickers_df = download_tickers_df(headers)

    # tickers_df.to_excel(f'{main_folder_path}tickers.xlsx')
    tict = TickerType()
    tickers_df = tickers_df[tickers_df['ticker'].isin(tict.tickers)]
    print(tickers_df)
    tickers_df = tickers_df[tickers_df['ticker'] == 'COST']
    n = 0  # jesli ==0 odpala funkcje printujaca opisy metrics
    for i in tickers_df.index:
        cik = tickers_df['cik_str'][i]
        ticker = tickers_df['ticker'][i]
        company_name = tickers_df['title'][i]
        print(f'{ticker}: {cik}')

        download_metrics(tict, ticker, cik, main_folder_path, headers, n)
        download_price_and_shares(ticker, cik, main_folder_path, headers)

        process_data(ticker, cik, main_folder_path)

        n += 1

    current_data(main_folder_path)
