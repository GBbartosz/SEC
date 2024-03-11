from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import os
import pandas as pd


import plotly.graph_objects as go
from indicator import Indicators


def summarize_quarters_to_ttm_years(indicators, metricsdf):
    metriccols = metricsdf.columns[3:]
    for metriccol in metriccols:
        if metriccol in indicators.summarizing_indicators:
            metricsdf[f'ttm_{metriccol}'] = metricsdf[metriccol].rolling(window=4, min_periods=4).sum()
    return metricsdf


def coalesce(indicators, metricsdf):
    # petla po grupach coalesce z Indicators
    # sprawdza liczbę kolumn dla danego tickera które wchodza w sklad grupy
    # w zaleznosci od liczby znalezionych kolumn robi coalesce tworzac dluzszy szereg danych (byly przypadki (googl) revenue do 2021, od 2020 nastepnie RevenueFromContractWithCustomerExcludingAssessedTax)
    for attr, value in indicators.coalesce.__dict__.items():
        coalesce_group = indicators.coalesce.__getattribute__(attr)
        columns = [c for c in metricsdf.columns if c in coalesce_group]
        if len(columns) == 1:
            metricsdf[f'{attr}'] = metricsdf[f'{columns[0]}']
        if len(columns) == 2:
            metricsdf[f'{attr}'] = metricsdf[f'{columns[0]}'].fillna(metricsdf[f'{columns[1]}'])
        if len(columns) == 3:
            metricsdf[f'{attr}'] = metricsdf[f'{columns[0]}'].fillna(metricsdf[f'{columns[1]}']).fillna(metricsdf[f'{columns[2]}'])
        if len(columns) == 4:
            metricsdf[f'{attr}'] = metricsdf[f'{columns[0]}'].fillna(metricsdf[f'{columns[1]}']).fillna(metricsdf[f'{columns[2]}']).fillna(metricsdf[f'{columns[3]}'])
    return metricsdf


def calculate_metrics_indicators(indicators, metricsdf):
    # create new indicator and add new indicator's name to obj indicators.metrics_indicators in file indicators

    year_window = 4

    # Profit Margin
    metricsdf['ttm_ProfitMargin'] = (metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_revenue_coalesce']).round(4)

    metricsdf['ttm_ProfitMargin_3y_avg'] = round(metricsdf['ttm_ProfitMargin'].rolling(window=year_window * 3, min_periods=year_window * 3).mean(), 4)
    metricsdf['ttm_ProfitMargin_5y_avg'] = round(metricsdf['ttm_ProfitMargin'].rolling(window=year_window * 5, min_periods=year_window * 5).mean(), 4)

    # Revenue
    metricsdf['ttm_revenue_coalesce_growth_1y'] = round(metricsdf['ttm_revenue_coalesce'] / metricsdf['ttm_revenue_coalesce'].shift(year_window * 1) - 1, 2)
    metricsdf['ttm_revenue_coalesce_growth_3y'] = round(metricsdf['ttm_revenue_coalesce'] / metricsdf['ttm_revenue_coalesce'].shift(year_window * 3) - 1, 2)
    metricsdf['ttm_revenue_coalesce_growth_5y'] = round(metricsdf['ttm_revenue_coalesce'] / metricsdf['ttm_revenue_coalesce'].shift(year_window * 5) - 1, 2)

    metricsdf['ttm_revenue_coalesce_growth_3y_avg'] = round((metricsdf['ttm_revenue_coalesce'] / metricsdf['ttm_revenue_coalesce'].shift(year_window * 3)) ** (1 / 3) - 1, 2)
    metricsdf['ttm_revenue_coalesce_growth_5y_avg'] = round((metricsdf['ttm_revenue_coalesce'] / metricsdf['ttm_revenue_coalesce'].shift(year_window * 5)) ** (1 / 5) - 1, 2)

    # Net Income
    metricsdf['ttm_NetIncomeLoss_growth_1y'] = round(metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_NetIncomeLoss'].shift(year_window * 1) - 1, 2)
    metricsdf['ttm_NetIncomeLoss_growth_3y'] = round(metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_NetIncomeLoss'].shift(year_window * 3) - 1, 2)
    metricsdf['ttm_NetIncomeLoss_growth_5y'] = round(metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_NetIncomeLoss'].shift(year_window * 5) - 1, 2)

    metricsdf['ttm_NetIncomeLoss_growth_3y_avg'] = round((metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_NetIncomeLoss'].shift(year_window * 3)) ** (1 / 3) - 1, 2)
    metricsdf['ttm_NetIncomeLoss_growth_5y_avg'] = round((metricsdf['ttm_NetIncomeLoss'] / metricsdf['ttm_NetIncomeLoss'].shift(year_window * 5)) ** (1 / 5) - 1, 2)

    return metricsdf


def create_all_data_df(indicators, base_columns, metricsdf, pricedf, sharesdf):
    totaldf = pd.merge_asof(pricedf, metricsdf, left_on='date', right_on='end', direction='backward')

    totaldf = pd.merge_asof(totaldf, sharesdf, left_on='date', right_on='end', direction='backward', suffixes=('', '_drop'))
    drop_columns = [col for col in totaldf.columns if col.endswith('_drop')]
    totaldf = totaldf.drop(columns=drop_columns)

    indicators.valid_indicators = [i for i in indicators.indicators if i in totaldf.columns]
    indicators.valid_ttm_indicators = [i for i in indicators.ttm_indicators if i in totaldf.columns]
    ordered_columns = base_columns + indicators.valid_indicators + indicators.valid_ttm_indicators + indicators.coalesce_indicators + indicators.metrics_indicators
    totaldf = totaldf[ordered_columns]
    totaldf = totaldf.sort_values(by='date')

    return totaldf


def calculate_price_indicators(indicators, total_df):
    # create new indicator and add new indicator's name to obj indicators.price_indicators in file indicators

    # Average window data
    year_window = 252
    min_year_window = 248

    # Price
    total_df['close_1y_avg'] = round(total_df['close'].rolling(window=year_window, min_periods=min_year_window).mean(), 2)
    total_df['close_3y_avg'] = round(total_df['close'].rolling(window=year_window * 3, min_periods=min_year_window * 3).mean(), 2)
    total_df['close_5y_avg'] = round(total_df['close'].rolling(window=year_window * 5, min_periods=min_year_window * 5).mean(), 2)

    # market capitalization
    total_df['market_capitalization'] = round(total_df['shares'] * total_df['close'], 0)

    total_df['market_capitalization_growth_1y'] = round(total_df['market_capitalization'] / total_df['market_capitalization'].shift(year_window * 1) - 1, 2)
    total_df['market_capitalization_growth_3y'] = round(total_df['market_capitalization'] / total_df['market_capitalization'].shift(year_window * 3) - 1, 2)
    total_df['market_capitalization_growth_5y'] = round(total_df['market_capitalization'] / total_df['market_capitalization'].shift(year_window * 5) - 1, 2)

    # P/E
    total_df['ttm_P/E'] = round(total_df['market_capitalization'] / total_df['ttm_NetIncomeLoss'], 2)

    total_df['ttm_P/E_1y_avg'] = round(total_df['ttm_P/E'].rolling(window=year_window, min_periods=min_year_window).mean(), 2)
    total_df['ttm_P/E_3y_avg'] = round(total_df['ttm_P/E'].rolling(window=year_window * 3, min_periods=min_year_window * 3).mean(), 2)
    total_df['ttm_P/E_5y_avg'] = round(total_df['ttm_P/E'].rolling(window=year_window * 5, min_periods=min_year_window * 5).mean(), 2)

    # PEG
    total_df['ttm_PEG_historical_3y'] = round(total_df['ttm_P/E'] / total_df['ttm_NetIncomeLoss_growth_3y_avg'], 2)
    total_df['ttm_PEG_historical_5y'] = round(total_df['ttm_P/E'] / total_df['ttm_NetIncomeLoss_growth_5y_avg'], 2)

    # P/S
    total_df['ttm_P/S'] = round(total_df['market_capitalization'] / total_df['ttm_revenue_coalesce'], 2)

    total_df['ttm_P/S_1y_avg'] = round(total_df['ttm_P/S'].rolling(window=year_window, min_periods=min_year_window).mean(), 2)
    total_df['ttm_P/S_3y_avg'] = round(total_df['ttm_P/S'].rolling(window=year_window * 3, min_periods=min_year_window * 3).mean(), 2)
    total_df['ttm_P/S_5y_avg'] = round(total_df['ttm_P/S'].rolling(window=year_window * 5, min_periods=min_year_window * 5).mean(), 2)

    # PSG - PEG for revenue
    total_df['ttm_PSG_historical_3y'] = round(total_df['ttm_P/S'] / total_df['ttm_revenue_coalesce_growth_3y_avg'], 2)
    total_df['ttm_PSG_historical_5y'] = round(total_df['ttm_P/S'] / total_df['ttm_revenue_coalesce_growth_5y_avg'], 2)

    return total_df


def fill_nan_values_for_metrics(indicators, base_columns, total_df, metricsdf, pricedf):
    # puts nan for columns where there is not need to have every day value for example revenue which is reported quarterly
    # it's done after calculating price indicators
    # there are left values only for the end of quarters
    direct_join_df = pd.merge_asof(metricsdf, pricedf, left_on='end', right_on='date', direction='forward')[['end', 'date']]
    total_df = total_df.merge(direct_join_df, on=['date', 'end'], how='left', indicator=True)
    columns_to_apply_nan = [c for c in base_columns if c not in ['date', 'close', 'Volume', 'dividends', 'stock_splits']] + indicators.valid_indicators + indicators.valid_ttm_indicators + indicators.coalesce_indicators + indicators.metrics_indicators
    total_df.loc[total_df['_merge'] == 'left_only', columns_to_apply_nan] = np.nan
    total_df = total_df.drop('_merge', axis=1)
    return total_df


def process_data(ticker, cik, main_folder_path):
    indicators = Indicators()
    base_columns = ['date', 'end', 'year', 'quarter', 'shares', 'close', 'Volume', 'dividends', 'stock_splits']
    metrics_folder_path = f'{main_folder_path}metrics\\'
    processed_folder_path = f'{main_folder_path}processed_data\\'
    files = os.listdir(metrics_folder_path)
    #print(files)
    ticker_files = [f for f in files if f'{ticker}_' in f]
    #print(ticker_files)
    print('ERROR IN SELECTING TICKER FILES ALGORITHM! Files probably taken from another ticker!') if len(ticker_files) > 3 else None

    metricsdf = pd.read_csv(f'{metrics_folder_path}{ticker}_metrics.csv')
    metricsdf['end'] = pd.to_datetime(metricsdf['end'])

    pricedf = pd.read_csv(f'{metrics_folder_path}{ticker}_price.csv')
    pricedf['date'] = pd.to_datetime(pricedf['date'])

    sharesdf = pd.read_csv(f'{metrics_folder_path}{ticker}_shares.csv')
    sharesdf['end'] = pd.to_datetime(sharesdf['end'])

    metricsdf = summarize_quarters_to_ttm_years(indicators, metricsdf)
    metricsdf = coalesce(indicators, metricsdf)
    metricsdf = calculate_metrics_indicators(indicators, metricsdf)
    total_df = create_all_data_df(indicators, base_columns, metricsdf, pricedf, sharesdf)
    total_df = calculate_price_indicators(indicators, total_df)
    total_df = fill_nan_values_for_metrics(indicators, base_columns, total_df, metricsdf, pricedf)
    #print(total_df)
    total_df.to_csv(f'{processed_folder_path}{ticker}_processed.csv', index=False)

    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=total_df['end'], y=total_df['ttm_NetIncomeLoss'], mode='lines+markers'))
    # fig.add_trace(go.Scatter(x=total_df['date'], y=total_df['ttm_Revenues'], mode='lines+markers'))
    # fig.add_trace(go.Scatter(x=total_df['date'], y=total_df['ttm_revenue_coalesce'], mode='lines+markers'))
    # fig.update_traces(connectgaps=True)
    # fig.show()


# pd.reset_option('display.max_rows')
# pd.reset_option('display.max_columns')
# pd.reset_option('display.width')
# pd.reset_option('display.float_format')
# pd.reset_option('display.max_colwidth')
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_colwidth', 40)
# pd.set_option('display.width', 400)
# ticker = 'GOOGL'
# cik = '0001652044'
# main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
# process_data(ticker, cik, main_folder_path)
