import datetime
import pandas as pd
from advancedprocessing import current_data, correlation, alerts_calculation
from dataprocessing import process_data2
from functions import TickerType, pandas_df_display_options, download_tickers_df
import yfinance as yf


class MyPaths:
    def __init__(self):
        self.main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2025\\'
        self.converted_raw_files_folder_path = f'{self.main_folder_path}converter_to_2025\\converted_raw_files\\'
        self.metrics_folder_path = f'{self.main_folder_path}metrics\\'
        self.processed_data_folder_path = f'{self.main_folder_path}processed_data\\'
        self.current_data_folder_path = f'{self.main_folder_path}current_data\\'


def converter(tic):
    month_num_str_to_quarter_dict = {'01': 1,
                                     '02': 1,
                                     '03': 1,
                                     '04': 2,
                                     '05': 2,
                                     '06': 2,
                                     '07': 3,
                                     '08': 3,
                                     '09': 3,
                                     '10': 4,
                                     '11': 4,
                                     '12': 4}

    file_path = f'{mypaths.converted_raw_files_folder_path}{tic}_metrics_raw.csv'
    df = pd.read_csv(file_path, sep=',')

    for c in df.columns:
        if 'Unnamed' in c:
            df = df.drop(c, axis=1)

    df['end'] = pd.to_datetime(df['end']) + pd.Timedelta(days=1)  # wyniki podawane po zamknięciu sesji
    df['quarter'] = df['end_period'].apply(lambda x: month_num_str_to_quarter_dict[x.split('-')[1]])
    df['year'] = df['end_period'].str[:4]
    df = df[['end', 'year', 'quarter', 'Revenue', 'NetIncome', 'Shares']]
    df = df.sort_values(by='end').reset_index(drop=True)

    df.to_csv(f'{mypaths.metrics_folder_path}{tic}_metrics.csv', index=False)


def download_price_and_shares2(tic):

    metrics_df = pd.read_csv(f'{mypaths.metrics_folder_path}{tic}_metrics.csv')
    min_date = metrics_df['end'].min()  # data od której importowane są ceny

    # Download shares outstanding data
    stock_info = yf.Ticker(tic)
    pricedf = stock_info.history(period='1d', start=min_date, end=datetime.date.today() + datetime.timedelta(days=1)).reset_index()
    pricedf = pricedf.rename(columns={'Date': 'date', 'Close': 'close', 'Volumne': 'volume', 'Dividends': 'dividends', 'Stock Splits': 'stock_splits'})
    pricedf = pricedf.drop(columns=['Open', 'High', 'Low'])
    pricedf['date'] = pd.to_datetime(pricedf['date'])
    pricedf['date'] = pricedf['date'].dt.date
    pricedf['date'] = pd.to_datetime(pricedf['date'])
    pricedf['close'] = pricedf['close'].round(2)

    pricedf.to_csv(f'{mypaths.metrics_folder_path}{tic}_price.csv', index=False)


def add_manual_ticker_to_tickers_df(tdf, mtickers):
    for mtic in mtickers:
        mtic_l = [None, mtic, None]
        tdf.loc[len(tdf)] = mtic_l
    return tdf


if __name__ == '__main__':
    pandas_df_display_options()

    mypaths = MyPaths()

    tickers_df = pd.read_excel(f'{mypaths.main_folder_path}tickers_data.xlsx')
    tickers = tickers_df['ticker'].tolist()

    #n = 0  # jesli ==0 odpala funkcje printujaca opisy metrics
    for ticker in tickers:
        print(ticker)
        converter(ticker)
        download_price_and_shares2(ticker)
        process_data2(ticker, mypaths)
        #n += 1

    current_data(mypaths)
    #correlation(main_folder_path)
    alerts_calculation(mypaths)
