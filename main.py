import pandas as pd

from advancedprocessing import current_data, correlation, alerts_calculation
from dataprocessing import process_data2
from functions import TickerType, pandas_df_display_options, download_tickers_df
from secdownload import download_metrics
from sharespricedownload import download_price_and_shares2

# subdropdown
# correlation  - pierwszy kwartal przedluzyc o 30 dni w dol>?
# pca
    # 3d graph for pca

# nierozwiazane
    # Visa sahres nie do namierzenia
    # COST rozjazd net income i revenue - co 4 kwartał niezgodność

# do rozwiazania
    # DIS zduplikowane Q3 2020
    # googl pierwszy kwartał q3 2014 jest wliczany to sumy 2015 q3 q2 q1, czyli brak 2014 q4, wyjasnic dlaczego  # chyba wyjasnione

# do kontroli
    # MCD prawdopodobnie co roku w grudniu raportuje shares w mln (dodac 2024 w sharepricedownload correct_errors jesli problem wystapi)


def add_manual_ticker_to_tickers_df(tdf, mtickers):
    for mtic in mtickers:
        mtic_l = [None, mtic, None]
        tdf.loc[len(tdf)] = mtic_l
    return tdf


if __name__ == '__main__':
    pandas_df_display_options()
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    #headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
    #tickers_df = download_tickers_df(headers)

    tickers_df = pd.read_excel(f'{main_folder_path}tickers_data.xlsx')
    tickers = tickers_df['ticker'].tolist()
    #tickers = ['KER.PA']

    # tickers_df.to_excel(f'{main_folder_path}tickers.xlsx')
    #tict = TickerType()
    #tickers_df = tickers_df[tickers_df['ticker'].isin(tict.tickers)]

    #manual_tickers = ['KER.PA']  # metrics and shares files created manually
    #tickers_df = add_manual_ticker_to_tickers_df(tickers_df, manual_tickers)

    #print(tickers_df)
    #tickers_df = tickers_df[tickers_df['ticker'] == 'META']
    #tickers_df = tickers_df[tickers_df['ticker'].isin(['GOOGL', 'META'])]
    n = 0  # jesli ==0 odpala funkcje printujaca opisy metrics
    for ticker in tickers:
    #for i in tickers_df.index:
        #cik = tickers_df['cik_str'][i]
        #ticker = tickers_df['ticker'][i]
        #company_name = tickers_df['title'][i]
        #print(f'{ticker}: {cik}')
        print(ticker)
        #if cik is not None:  # don't download for manuals
        #    download_metrics(tict, ticker, cik, main_folder_path, headers, n)

        download_price_and_shares2(ticker, main_folder_path)
        process_data2(ticker, main_folder_path)

        n += 1

    current_data(main_folder_path)
    correlation(main_folder_path)
    alerts_calculation(main_folder_path)
