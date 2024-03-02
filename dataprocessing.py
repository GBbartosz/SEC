import numpy as np
import os
import pandas as pd

from indicator import Indicators


def summarize_quarters_to_ttm_years(metricsdf):
    indicators = Indicators()
    metriccols = metricsdf.columns[3:]
    for metriccol in metriccols:
        if metriccol in indicators.summarizing_indicators:
            metricsdf[f'ttm_{metriccol}'] = metricsdf[metriccol].rolling(window=4, min_periods=4).sum()
    print(metricsdf)
    return metricsdf


def coalesce(metricsdf):
    # petla po grupach coalesce z Indicators
    # sprawdza liczbę kolumn dla danego tickera które wchodza w sklad grupy
    # w zaleznosci od liczby znalezionych kolumn robi coalesce tworzac dluzszy szereg danych (byly przypadki (googl) revenue do 2021, od 2020 nastepnie RevenueFromContractWithCustomerExcludingAssessedTax)
    indicators = Indicators()
    for attr, value in indicators.coalesce.__dict__.items():
        coalesce_group = indicators.coalesce.__getattribute__(attr)
        columns = [c for c in metricsdf.columns if c in coalesce_group]
        if len(columns) == 1:
            metricsdf[f'ttm_{attr}_coalesce'] = metricsdf[f'ttm_{columns[0]}']
        if len(columns) == 2:
            metricsdf[f'ttm_{attr}_coalesce'] = metricsdf[f'ttm_{columns[0]}'].fillna(metricsdf[f'ttm_{columns[1]}'])
        if len(columns) == 3:
            metricsdf[f'ttm_{attr}_coalesce'] = metricsdf[f'ttm_{columns[0]}'].fillna(metricsdf[f'ttm_{columns[1]}']).fillna(metricsdf[f'ttm_{columns[2]}'])
        if len(columns) == 4:
            metricsdf[f'ttm_{attr}_coalesce'] = metricsdf[f'ttm_{columns[0]}'].fillna(metricsdf[f'ttm_{columns[1]}']).fillna(metricsdf[f'ttm_{columns[2]}']).fillna(metricsdf[f'ttm_{columns[3]}'])
    return metricsdf


def calculate_metrics_indicators(metricsdf):

    def calculate_profit_margin(metricsdf):
        metricsdf['ttm_ProfitMargin'] = (metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_revenue_coalesce']).round(4)

        # Perform the calculation using np.where()
        #metricsdf['ttm_ProfitMargin'] = np.where(metricsdf['ttm_Revenues'].isna(),
        #                  (metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_RevenueFromContractWithCustomerExcludingAssessedTax']).round(2),
        #                  (metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_Revenues']).round(2))
        return metricsdf

    metricsdf = calculate_profit_margin(metricsdf)
    return metricsdf


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

    metricsdf = summarize_quarters_to_ttm_years(metricsdf)
    metricsdf = coalesce(metricsdf)
    metricsdf = calculate_metrics_indicators(metricsdf)
    print(metricsdf)

pd.reset_option('display.max_rows')
pd.reset_option('display.max_columns')
pd.reset_option('display.width')
pd.reset_option('display.float_format')
pd.reset_option('display.max_colwidth')
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 40)
pd.set_option('display.width', 400)
ticker = 'GOOGL'
cik = '0001652044'
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
process_data(ticker, cik, main_folder_path)
