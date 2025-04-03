import pandas as pd

from advancedprocessing import current_data, correlation, alerts_calculation
from dataprocessing import process_data2
from functions import TickerType, pandas_df_display_options, download_tickers_df
from secdownload import download_metrics
from sharespricedownload import download_price_and_shares2


def add_manual_ticker_to_tickers_df(tdf, mtickers):
    for mtic in mtickers:
        mtic_l = [None, mtic, None]
        tdf.loc[len(tdf)] = mtic_l
    return tdf


if __name__ == '__main__':
    pandas_df_display_options()
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'

    tickers_df = pd.read_excel(f'{main_folder_path}tickers_data.xlsx')
    tickers = tickers_df['ticker'].tolist()

    #n = 0  # jesli ==0 odpala funkcje printujaca opisy metrics
    for ticker in tickers:
        print(ticker)
        download_price_and_shares2(ticker, main_folder_path)
        process_data2(ticker, main_folder_path)
        #n += 1

    current_data(main_folder_path)
    #correlation(main_folder_path)
    alerts_calculation(main_folder_path)
