from datetime import timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go
from indicator2 import Indicators2


def summarize_quarters_to_ttm_years(indicators, metricsdf):
    metriccols = metricsdf.columns[3:]
    for metriccol in metriccols:
        if metriccol in indicators.summarizing_indicators:
            metricsdf[f'ttm_{metriccol}'] = metricsdf[metriccol].rolling(window=4, min_periods=4).sum()
    return metricsdf


def calculate_metrics_indicators2(mdf):
    # create new indicator and add new indicator's name to obj indicators.metrics_indicators in file indicators

    def calculate_change(mydf, col_name, years_num):
        shifted_value = mydf[col_name].shift(year_window * years_num)
        current_value = mydf[col_name]

        res = np.where(
            shifted_value == 0,
            np.where(current_value > 0, 1, np.where(current_value < 0, -1, 0)),  # if shifted value == 0
            round(current_value / shifted_value - 1, 2)  # if shifted_value != 0
        )
        return res

    def calculate_net_income_cagr(mydf, years_num):
        mdf[f'calc_growth_{years_num}y'] = (mdf['ttm_NetIncome'] / mdf['ttm_NetIncome'].shift(year_window * years_num))
        mdf[f'calc_growth_{years_num}y'] = mdf[f'calc_growth_{years_num}y'].apply(lambda x: x if x >= 0 or np.isnan(x) else 0.00000001)
        mdf[f'NetIncomeCAGR{years_num}y'] = mdf[f'calc_growth_{years_num}y'].apply(lambda x: x if x == 0.00000001 or np.isnan(x) else round(x ** (1 / years_num) - 1, 3))
        return mydf

    year_window = 4

    # Shares
    mdf['SharesChg1q'] = (mdf['Shares'] / mdf['Shares'].shift(1) - 1).round(4)
    mdf['SharesChg1y'] = (mdf['Shares'] / mdf['Shares'].shift(year_window * 1) - 1).round(4)
    mdf['SharesChg3y'] = (mdf['Shares'] / mdf['Shares'].shift(year_window * 3) - 1).round(4)
    mdf['SharesChg5y'] = (mdf['Shares'] / mdf['Shares'].shift(year_window * 5) - 1).round(4)

    # Profit Margin
    mdf['ttm_ProfitMargin'] = (mdf['ttm_NetIncome'] / mdf['ttm_Revenue']).round(4)

    mdf['ttm_ProfitMarginChg1y'] = (mdf['ttm_ProfitMargin'] / mdf['ttm_ProfitMargin'].shift(year_window * 1) - 1).round(4)
    mdf['ttm_ProfitMarginChg2y'] = (mdf['ttm_ProfitMargin'] / mdf['ttm_ProfitMargin'].shift(year_window * 2) - 1).round(4)
    mdf['ttm_ProfitMarginChg3y'] = (mdf['ttm_ProfitMargin'] / mdf['ttm_ProfitMargin'].shift(year_window * 3) - 1).round(4)
    mdf['ttm_ProfitMarginChg4y'] = (mdf['ttm_ProfitMargin'] / mdf['ttm_ProfitMargin'].shift(year_window * 4) - 1).round(4)
    mdf['ttm_ProfitMarginChg5y'] = (mdf['ttm_ProfitMargin'] / mdf['ttm_ProfitMargin'].shift(year_window * 5) - 1).round(4)

    mdf['ttm_ProfitMargin3yAvg'] = round(mdf['ttm_ProfitMargin'].rolling(window=year_window * 3, min_periods=year_window * 3).mean(), 4)
    mdf['ttm_ProfitMargin5yAvg'] = round(mdf['ttm_ProfitMargin'].rolling(window=year_window * 5, min_periods=year_window * 5).mean(), 4)

    # Revenue
    mdf['ttm_RevenueGrowth1y'] = round(mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 1) - 1, 3)
    mdf['ttm_RevenueGrowth3y'] = round(mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 3) - 1, 3)
    mdf['ttm_RevenueGrowth5y'] = round(mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 5) - 1, 3)

    mdf['RevenueAAGR3y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 1) + mdf['ttm_Revenue'].shift(year_window * 1) / mdf['ttm_Revenue'].shift(year_window * 2) + mdf['ttm_Revenue'].shift(year_window * 2) / mdf['ttm_Revenue'].shift(year_window * 3)) / 3 - 1, 3)
    mdf['RevenueAAGR5y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 1) + mdf['ttm_Revenue'].shift(year_window * 1) / mdf['ttm_Revenue'].shift(year_window * 2) + mdf['ttm_Revenue'].shift(year_window * 2) / mdf['ttm_Revenue'].shift(year_window * 3) + mdf['ttm_Revenue'].shift(year_window * 3) / mdf['ttm_Revenue'].shift(year_window * 4) + mdf['ttm_Revenue'].shift(year_window * 4) / mdf['ttm_Revenue'].shift(year_window * 5)) / 5 - 1, 3)

    # Revenue CAGR
    mdf['RevenueCAGR2y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 2)) ** (1 / 2) - 1, 3)
    mdf['RevenueCAGR3y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 3)) ** (1 / 3) - 1, 3)
    mdf['RevenueCAGR4y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 4)) ** (1 / 4) - 1, 3)
    mdf['RevenueCAGR5y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 5)) ** (1 / 5) - 1, 3)
    mdf['RevenueCAGR10y'] = round((mdf['ttm_Revenue'] / mdf['ttm_Revenue'].shift(year_window * 10)) ** (1 / 10) - 1, 3)

    # Revenue Future
    mdf['Future1yRevenue_Real'] = mdf['ttm_Revenue'].shift(year_window * -1)
    mdf['Future2yRevenue_Real'] = mdf['ttm_Revenue'].shift(year_window * -2)
    mdf['Future3yRevenue_Real'] = mdf['ttm_Revenue'].shift(year_window * -3)
    mdf['Future4yRevenue_Real'] = mdf['ttm_Revenue'].shift(year_window * -4)
    mdf['Future5yRevenue_Real'] = mdf['ttm_Revenue'].shift(year_window * -5)

    mdf['Future1yRevenue_on_ttm_RevenueGrowth1y'] = (mdf['ttm_Revenue'] * (1 + mdf['ttm_RevenueGrowth1y'])).round(1)
    mdf['Future2yRevenue_on_ttm_RevenueGrowth1y'] = (mdf['ttm_Revenue'] * ((1 + mdf['ttm_RevenueGrowth1y']) ** 2)).round(1)
    mdf['Future3yRevenue_on_ttm_RevenueGrowth1y'] = (mdf['ttm_Revenue'] * ((1 + mdf['ttm_RevenueGrowth1y']) ** 3)).round(1)
    mdf['Future4yRevenue_on_ttm_RevenueGrowth1y'] = (mdf['ttm_Revenue'] * ((1 + mdf['ttm_RevenueGrowth1y']) ** 4)).round(1)
    mdf['Future5yRevenue_on_ttm_RevenueGrowth1y'] = (mdf['ttm_Revenue'] * ((1 + mdf['ttm_RevenueGrowth1y']) ** 5)).round(1)

    mdf['Future1yRevenue_on_RevenueCAGR3y'] = (mdf['ttm_Revenue'] * (1 + mdf['RevenueCAGR3y'])).round(1)
    mdf['Future2yRevenue_on_RevenueCAGR3y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR3y']) ** 2)).round(1)
    mdf['Future3yRevenue_on_RevenueCAGR3y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR3y']) ** 3)).round(1)
    mdf['Future4yRevenue_on_RevenueCAGR3y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR3y']) ** 4)).round(1)
    mdf['Future5yRevenue_on_RevenueCAGR3y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR3y']) ** 5)).round(1)

    mdf['Future1yRevenue_on_RevenueCAGR5y'] = (mdf['ttm_Revenue'] * (1 + mdf['RevenueCAGR5y'])).round(1)
    mdf['Future2yRevenue_on_RevenueCAGR5y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR5y']) ** 2)).round(1)
    mdf['Future3yRevenue_on_RevenueCAGR5y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR5y']) ** 3)).round(1)
    mdf['Future4yRevenue_on_RevenueCAGR5y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR5y']) ** 4)).round(1)
    mdf['Future5yRevenue_on_RevenueCAGR5y'] = (mdf['ttm_Revenue'] * ((1 + mdf['RevenueCAGR5y']) ** 5)).round(1)

    # Net Income
    mdf['ttm_NetIncomeGrowth1y'] = calculate_change(mdf, 'ttm_NetIncome', 1)
    mdf['ttm_NetIncomeGrowth3y'] = calculate_change(mdf, 'ttm_NetIncome', 3)
    mdf['ttm_NetIncomeGrowth5y'] = calculate_change(mdf, 'ttm_NetIncome', 5)

    # Net Income historical average
    mdf['ttm_NetIncome_3y_mean'] = mdf['NetIncome'].rolling(window=year_window * 3, min_periods=year_window * 3).sum() / 3
    mdf['ttm_NetIncome_5y_mean'] = mdf['NetIncome'].rolling(window=year_window * 5, min_periods=year_window * 5).sum() / 5
    mdf['ttm_NetIncome_7y_mean'] = mdf['NetIncome'].rolling(window=year_window * 7, min_periods=year_window * 7).sum() / 7
    mdf['ttm_NetIncome_10y_mean'] = mdf['NetIncome'].rolling(window=year_window * 10, min_periods=year_window * 10).sum() / 10

    # Net Income AAGR
    mdf['NetIncomeAAGR3y'] = round((mdf['ttm_NetIncome'] / mdf['ttm_NetIncome'].shift(year_window * 1) + mdf['ttm_NetIncome'].shift(year_window * 1) / mdf['ttm_NetIncome'].shift(year_window * 2) + mdf['ttm_NetIncome'].shift(year_window * 2) / mdf['ttm_NetIncome'].shift(year_window * 3)) / 3 - 1, 2)
    mdf['NetIncomeAAGR5y'] = round((mdf['ttm_NetIncome'] / mdf['ttm_NetIncome'].shift(year_window * 1) + mdf['ttm_NetIncome'].shift(year_window * 1) / mdf['ttm_NetIncome'].shift(year_window * 2) + mdf['ttm_NetIncome'].shift(year_window * 2) / mdf['ttm_NetIncome'].shift(year_window * 3) + mdf['ttm_NetIncome'].shift(year_window * 3) / mdf['ttm_NetIncome'].shift(year_window * 4) + mdf['ttm_NetIncome'].shift(year_window * 4) / mdf['ttm_NetIncome'].shift(year_window * 5)) / 5 - 1, 2)

    # Net Income CAGR
    mdf = calculate_net_income_cagr(mdf, 2)
    mdf = calculate_net_income_cagr(mdf, 3)
    mdf = calculate_net_income_cagr(mdf, 4)
    mdf = calculate_net_income_cagr(mdf, 5)
    mdf = calculate_net_income_cagr(mdf, 10)

    # Net Income Future
    mdf['Future1yNetIncome_Real'] = mdf['ttm_NetIncome'].shift(year_window * -1)
    mdf['Future2yNetIncome_Real'] = mdf['ttm_NetIncome'].shift(year_window * -2)
    mdf['Future3yNetIncome_Real'] = mdf['ttm_NetIncome'].shift(year_window * -3)
    mdf['Future4yNetIncome_Real'] = mdf['ttm_NetIncome'].shift(year_window * -4)
    mdf['Future5yNetIncome_Real'] = mdf['ttm_NetIncome'].shift(year_window * -5)

    mdf['Future1yNetIncome_on_ttm_NetIncomeGrowth1y'] = (mdf['ttm_NetIncome'] * (1 + mdf['ttm_NetIncomeGrowth1y'])).round(1)
    mdf['Future2yNetIncome_on_ttm_NetIncomeGrowth1y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['ttm_NetIncomeGrowth1y']) ** 2)).round(1)
    mdf['Future3yNetIncome_on_ttm_NetIncomeGrowth1y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['ttm_NetIncomeGrowth1y']) ** 3)).round(1)
    mdf['Future4yNetIncome_on_ttm_NetIncomeGrowth1y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['ttm_NetIncomeGrowth1y']) ** 4)).round(1)
    mdf['Future5yNetIncome_on_ttm_NetIncomeGrowth1y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['ttm_NetIncomeGrowth1y']) ** 5)).round(1)

    mdf['Future1yNetIncome_on_NetIncomeCAGR3y'] = (mdf['ttm_NetIncome'] * (1 + mdf['NetIncomeCAGR3y'])).round(1)
    mdf['Future2yNetIncome_on_NetIncomeCAGR3y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR3y']) ** 2)).round(1)
    mdf['Future3yNetIncome_on_NetIncomeCAGR3y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR3y']) ** 3)).round(1)
    mdf['Future4yNetIncome_on_NetIncomeCAGR3y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR3y']) ** 4)).round(1)
    mdf['Future5yNetIncome_on_NetIncomeCAGR3y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR3y']) ** 5)).round(1)

    mdf['Future1yNetIncome_on_NetIncomeCAGR5y'] = (mdf['ttm_NetIncome'] * (1 + mdf['NetIncomeCAGR5y'])).round(1)
    mdf['Future2yNetIncome_on_NetIncomeCAGR5y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR5y']) ** 2)).round(1)
    mdf['Future3yNetIncome_on_NetIncomeCAGR5y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR5y']) ** 3)).round(1)
    mdf['Future4yNetIncome_on_NetIncomeCAGR5y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR5y']) ** 4)).round(1)
    mdf['Future5yNetIncome_on_NetIncomeCAGR5y'] = (mdf['ttm_NetIncome'] * ((1 + mdf['NetIncomeCAGR5y']) ** 5)).round(1)

    return mdf


def create_all_data_df2(indicators, base_columns, metricsdf, pricedf):
    # joins all tables (price, metrics and shares)
    # fulfills metrics and shares for price dates
    totaldf = pd.merge_asof(pricedf, metricsdf, left_on='date', right_on='end', direction='backward')

    indicators.valid_indicators = [i for i in indicators.indicators if i in totaldf.columns]
    indicators.valid_ttm_indicators = [i for i in indicators.ttm_indicators if i in totaldf.columns]
    ordered_columns = base_columns + indicators.valid_indicators + indicators.valid_ttm_indicators + indicators.metrics_indicators
    totaldf = totaldf[ordered_columns]
    totaldf = totaldf.sort_values(by='date')
    return totaldf


def calculate_price_indicators2(total_df):
    # create new indicator and add new indicator's name to obj indicators.price_indicators in file indicators

    # Average window data
    year_window = 252
    min_year_window = 248

    # Price
    total_df['PriceChangeDaily'] = round(total_df['close'] / total_df['close'].shift(1) - 1, 4)
    total_df['close_1y_avg'] = round(total_df['close'].rolling(window=year_window, min_periods=min_year_window).mean(), 4)
    total_df['close_3y_avg'] = round(total_df['close'].rolling(window=year_window * 3, min_periods=min_year_window * 3).mean(), 4)
    total_df['close_5y_avg'] = round(total_df['close'].rolling(window=year_window * 5, min_periods=min_year_window * 5).mean(), 4)

    # Current price to avg
    total_df['price_to_1y_avg_ratio'] = (total_df['close'] / total_df['close_1y_avg'] - 1).round(4)
    total_df['price_to_3y_avg_ratio'] = (total_df['close'] / total_df['close_3y_avg'] - 1).round(4)
    total_df['price_to_5y_avg_ratio'] = (total_df['close'] / total_df['close_5y_avg'] - 1).round(4)

    # market capitalization
    total_df['market_capitalization'] = round(total_df['Shares'] * total_df['close'], 0)

    total_df['market_capitalization_growth_1y'] = round(total_df['market_capitalization'] / total_df['market_capitalization'].shift(year_window * 1) - 1, 2)
    total_df['market_capitalization_growth_3y'] = round(total_df['market_capitalization'] / total_df['market_capitalization'].shift(year_window * 3) - 1, 2)
    total_df['market_capitalization_growth_5y'] = round(total_df['market_capitalization'] / total_df['market_capitalization'].shift(year_window * 5) - 1, 2)

    # P/E
    total_df['ttm_P/E'] = np.where(total_df['ttm_NetIncome'].isna(),  # before first full year available data
                                   np.nan,
                                   np.where(total_df['ttm_NetIncome'] > 0,  # Negative Income
                                            round(total_df['market_capitalization'] / total_df['ttm_NetIncome'], 2),
                                            0)
                                   )

    total_df['ttm_P/E_1y_avg'] = round(total_df['ttm_P/E'].rolling(window=year_window, min_periods=min_year_window).mean(), 2)
    total_df['ttm_P/E_3y_avg'] = round(total_df['ttm_P/E'].rolling(window=year_window * 3, min_periods=min_year_window * 3).mean(), 2)
    total_df['ttm_P/E_5y_avg'] = round(total_df['ttm_P/E'].rolling(window=year_window * 5, min_periods=min_year_window * 5).mean(), 2)

    total_df['ttm_PE_to_1y_ratio'] = (total_df['ttm_P/E'] / total_df['ttm_P/E_1y_avg'] - 1).round(4)
    total_df['ttm_PE_to_3y_ratio'] = (total_df['ttm_P/E'] / total_df['ttm_P/E_3y_avg'] - 1).round(4)
    total_df['ttm_PE_to_5y_ratio'] = (total_df['ttm_P/E'] / total_df['ttm_P/E_5y_avg'] - 1).round(4)

    # P/E to historical mean net income
    total_df['ttm_P/E_3y_earnings'] = np.where(total_df['ttm_NetIncome_3y_mean'].isna(),
                                               np.nan,
                                               np.where(total_df['ttm_NetIncome_3y_mean'] > 0,  # Negative Income
                                                        round(total_df['market_capitalization'] / total_df['ttm_NetIncome_3y_mean'], 4),
                                                        0))
    total_df['ttm_P/E_5y_earnings'] = np.where(total_df['ttm_NetIncome_5y_mean'].isna(),
                                               np.nan,
                                               np.where(total_df['ttm_NetIncome_5y_mean'] > 0,  # Negative Income
                                                        round(total_df['market_capitalization'] / total_df['ttm_NetIncome_5y_mean'], 4),
                                                        0))
    total_df['ttm_P/E_7y_earnings'] = np.where(total_df['ttm_NetIncome_7y_mean'].isna(),
                                               np.nan,
                                               np.where(total_df['ttm_NetIncome_7y_mean'] > 0,  # Negative Income
                                                        round(total_df['market_capitalization'] / total_df['ttm_NetIncome_7y_mean'], 4),
                                                        0))
    total_df['ttm_P/E_10y_earnings'] = np.where(total_df['ttm_NetIncome_10y_mean'].isna(),
                                                np.nan,
                                                np.where(total_df['ttm_NetIncome_10y_mean'] > 0,  # Negative Income
                                                         round(total_df['market_capitalization'] / total_df['ttm_NetIncome_10y_mean'], 4),
                                                         0))

    # PEG
    total_df['ttm_PEG_historical_3y'] = round(total_df['ttm_P/E'] / (total_df['NetIncomeCAGR3y'] * 100).replace(0, 1), 2)
    total_df['ttm_PEG_historical_5y'] = round(total_df['ttm_P/E'] / (total_df['NetIncomeCAGR5y'] * 100).replace(0, 1), 2)

    # P/S
    total_df['ttm_P/S'] = np.where(total_df['ttm_Revenue'].isna(),  # before first full year available data
                                   np.nan,
                                   np.where(total_df['ttm_Revenue'] > 0,  # Negative Revenue
                                            round(total_df['market_capitalization'] / total_df['ttm_Revenue'], 2),
                                            0)
                                   )

    total_df['ttm_P/S_1y_avg'] = round(total_df['ttm_P/S'].rolling(window=year_window, min_periods=min_year_window).mean(), 2)
    total_df['ttm_P/S_3y_avg'] = round(total_df['ttm_P/S'].rolling(window=year_window * 3, min_periods=min_year_window * 3).mean(), 2)
    total_df['ttm_P/S_5y_avg'] = round(total_df['ttm_P/S'].rolling(window=year_window * 5, min_periods=min_year_window * 5).mean(), 2)

    total_df['ttm_PS_to_1y_ratio'] = (total_df['ttm_P/S'] / total_df['ttm_P/S_1y_avg'] - 1).round(4)
    total_df['ttm_PS_to_3y_ratio'] = (total_df['ttm_P/S'] / total_df['ttm_P/S_3y_avg'] - 1).round(4)
    total_df['ttm_PS_to_5y_ratio'] = (total_df['ttm_P/S'] / total_df['ttm_P/S_5y_avg'] - 1).round(4)

    # PSG - PEG for revenue
    total_df['ttm_PSG_historical_3y'] = round(total_df['ttm_P/S'] / (total_df['RevenueCAGR3y'] * 100).replace(0, 1), 2)
    total_df['ttm_PSG_historical_5y'] = round(total_df['ttm_P/S'] / (total_df['RevenueCAGR5y'] * 100).replace(0, 1), 2)

    return total_df


def fill_nan_values_for_metrics(indicators, base_columns, total_df, metricsdf, pricedf):
    # puts nan for columns where there is no need to have every day value for example revenue which is reported quarterly
    # it's done after calculating price indicators
    # there are left values only for the end of quarters
    direct_join_df = pd.merge_asof(metricsdf, pricedf, left_on='end', right_on='date', direction='forward')[['end', 'date']]
    total_df = total_df.merge(direct_join_df, on=['date', 'end'], how='left', indicator=True)
    columns_to_apply_nan = [c for c in base_columns if c not in ['date', 'close', 'Volume', 'dividends', 'stock_splits']] + indicators.valid_indicators + indicators.valid_ttm_indicators + indicators.metrics_indicators
    total_df.loc[total_df['_merge'] == 'left_only', columns_to_apply_nan] = np.nan
    total_df = total_df.drop('_merge', axis=1)
    return total_df


def process_data2(ticker, main_folder_path):
    indicators = Indicators2()
    base_columns = ['date', 'end', 'year', 'quarter', 'Shares', 'close', 'Volume', 'dividends', 'stock_splits']
    metrics_folder_path = f'{main_folder_path}metrics\\'
    processed_folder_path = f'{main_folder_path}processed_data\\'

    file_name = f'{ticker}_metrics.csv'
    metricsdf = pd.read_csv(f'{metrics_folder_path}{file_name}')
    metricsdf['end'] = pd.to_datetime(metricsdf['end'])

    pricedf = pd.read_csv(f'{metrics_folder_path}{ticker}_price.csv')
    pricedf['date'] = pd.to_datetime(pricedf['date'])

    metricsdf = summarize_quarters_to_ttm_years(indicators, metricsdf)
    metricsdf = calculate_metrics_indicators2(metricsdf)
    total_df = create_all_data_df2(indicators, base_columns, metricsdf, pricedf)
    total_df = calculate_price_indicators2(total_df)
    total_df = fill_nan_values_for_metrics(indicators, base_columns, total_df, metricsdf, pricedf)

    total_df.to_csv(f'{processed_folder_path}{ticker}_processed.csv', index=False)
