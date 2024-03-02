import os
import pandas as pd

from indicator import Indicators


def summarize_quarters_to_ttm_years(metricsdf):
    indicators = Indicators()
    print(metricsdf.columns)
    metriccols = metricsdf.columns[4:]
    print(metricsdf)
    for metriccol in metriccols:
        if metriccol in indicators.summarizing_indicators:
            metricsdf[f'__{metriccol}'] = metricsdf[metriccol].rolling(window=4, min_periods=4).sum()
    print(metricsdf)


def process_data(ticker, cik, main_folder_path):
    metrics_folder_path = f'{main_folder_path}metrics\\'
    processed_folder_path = f'{main_folder_path}processed_data\\'
    files = os.listdir(metrics_folder_path)
    print(files)
    ticker_files = [f for f in files if f'{ticker}_' in f]
    print(ticker_files)
    print('ERROR IN SELECTING TICKER FILES ALGORITHM! Files probably taken from another ticker!') if len(ticker_files) > 3 else None

    metricsdf = pd.read_csv(f'{metrics_folder_path}{ticker}_metrics.csv')
    pricedf = pd.read_csv(f'{metrics_folder_path}{ticker}_price.csv')
    sharesdf = pd.read_csv(f'{metrics_folder_path}{ticker}_shares.csv')

    summarize_quarters_to_ttm_years(metricsdf)


#pd.reset_option('display.max_rows')
#pd.reset_option('display.max_columns')
#pd.reset_option('display.width')
#pd.reset_option('display.float_format')
#pd.reset_option('display.max_colwidth')
#pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_colwidth', 40)
#pd.set_option('display.width', 400)
#ticker = 'GOOGL'
#cik = '0001652044'
#main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
#process_data(ticker, cik, main_folder_path)
