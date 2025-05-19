import numpy as np
import os
import pandas as pd
from datetime import timedelta
from functions import pandas_df_display_options
from indicator2 import Indicators2


def current_data(mypaths):
    files = os.listdir(mypaths.processed_data_folder_path)

    current_df = None
    for f in files:
        ticker = f[:f.find('_')]
        stock_df = pd.read_csv(f'{mypaths.processed_data_folder_path}{f}')
        stock_series = stock_df.ffill().iloc[-1]
        stock_series = stock_series.rename(ticker)
        if current_df is None:
            current_df = stock_series
        else:
            current_df = pd.concat([current_df, stock_series], axis=1)

    current_df = current_df.drop(['Volume',
                                  'dividends',
                                  'stock_splits'])
    current_df = current_df.T
    current_df = current_df.rename_axis('Stock')

    # print(current_df)

    current_df.to_csv(f'{mypaths.current_data_folder_path}current_data.csv')


def correlation(main_folder_path):

    def detect_error(mydf):
        if len(list(mydf.index)) != len(list(set(mydf.index))):
            print('ERROR! Duplicates in some metrics file!')

    def safe_correlation_matrix(values_df, data_time_period_type):

        tickers = values_df.columns

        for correlation_type in ['pearson', 'spearman']:
            for period_year in period_years:
                corr_df = pd.DataFrame(index=tickers, columns=tickers)
                for tic1 in tickers:
                    tic1_min_index = values_df[tic1].dropna().index.min()
                    tic1_max_index = values_df[tic1].dropna().index.max()
                    for tic2 in tickers:
                        tic2_min_index = values_df[tic2].dropna().index.min()
                        tic2_max_index = values_df[tic2].dropna().index.max()
                        if tic1 != tic2 and isinstance(tic1_min_index, tuple) and isinstance(tic2_min_index, tuple):  # handles nan values
                            min_index = max(tic1_min_index, tic2_min_index)
                            max_index = min(tic1_max_index, tic2_max_index)
                            if period_year == 'all':  # correlation for all available values for both companies not nan
                                corr_calculation_df = values_df[[tic1, tic2]][min_index:max_index]  # selecting period
                                #corr_calculation_df = corr_calculation_df.bfill()  # fulfilling nan values inbetween
                                correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2], method=correlation_type)
                            else:  # correlation for selected period

                                if data_time_period_type == 'daily':
                                    period_ago = max_index - timedelta(days=period_year * 365)
                                elif data_time_period_type == 'quarterly':
                                    period_ago = (max_index[0] - period_year, max_index[1])

                                if period_ago >= min_index:
                                    corr_calculation_df = values_df[(values_df.index >= period_ago) & (values_df.index <= max_index)][[tic1, tic2]]  # selecting period
                                    corr_calculation_df = corr_calculation_df.bfill() if data_time_period_type == 'daily' else corr_calculation_df  # fulfilling nan values inbetween
                                    correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2], method=correlation_type)
                                else:  # available data is too short compared to demanded period
                                    correlation = None
                        else:  # case when correlation AAPL: AAPL
                            correlation = None
                        corr_df.loc[tic1, tic2] = correlation

                corr_df = corr_df.dropna(how='all')  # drop rows and columns with not enough data to calculate correlation
                corr_df = corr_df.astype(float).fillna(1)  # fill 1 for nan where AAPL: AAPL

                file_name = f'{correlation_folder_path}correlation_{correlation_type}_{indicator_for_csv_file_name}_{period_year}'
                print(file_name)
                corr_df.to_csv(f'{file_name}.csv')

    processed_folder_path = f'{main_folder_path}processed_data\\'
    correlation_folder_path = f'{main_folder_path}correlation_data\\'
    files = os.listdir(processed_folder_path)

    indicators = Indicators2()
    period_years = [1, 2, 3, 5, 10, 'all']

    for indicator in indicators.correlation_indicators_quarterly[1:]:
        indicator_for_csv_file_name = indicator.replace('/', '')
        values_df = None
        for f in files:
            ticker = f[:f.find('_')]
            df = pd.read_csv(f'{processed_folder_path}{f}')[['year', 'quarter', indicator]]
            df = df.rename(columns={indicator: ticker})
            df = df.dropna(axis=0, how='any')  # calculating correlation only on quarterly data
            values_df = df if values_df is None else pd.merge(values_df, df, on=['year', 'quarter'], how='outer')
        values_df = values_df.set_index(['year', 'quarter'])
        detect_error(values_df)
        safe_correlation_matrix(values_df, 'quarterly')

    for indicator in indicators.correlation_indicators_daily:
        indicator_for_csv_file_name = indicator.replace('/', '')
        values_df = None
        for f in files:
            ticker = f[:f.find('_')]
            df = pd.read_csv(f'{processed_folder_path}{f}')[['date', indicator]]
            df[indicator] = df[indicator].bfill()
            df = df.rename(columns={indicator: ticker})
            values_df = df if values_df is None else pd.merge(values_df, df, on='date', how='outer')
        values_df['date'] = pd.to_datetime(values_df['date'])
        values_df = values_df.set_index('date')
        detect_error(values_df)
        safe_correlation_matrix(values_df, 'daily')


def alerts_calculation(mypaths):
    # new alert metrics must be added to Indicators.alerts

    def lower_than(series1, series2):
        return 1 if series1 < series2 else np.nan

    def higher_than(series1, series2):
        return 1 if series1 > series2 else np.nan

    indicators = Indicators2()
    df = pd.read_csv(f'{mypaths.current_data_folder_path}current_data.csv')

    df['Price < 3 year average'] = df.apply(lambda x: lower_than(x['close'], x['close_3y_avg']), axis=1)
    df['Price < 5 year average'] = df.apply(lambda x: lower_than(x['close'], x['close_5y_avg']), axis=1)
    df['ProfitMargin > 3 year average'] = df.apply(lambda x: higher_than(x['ttm_ProfitMargin'], x['ttm_ProfitMargin3yAvg']), axis=1)
    df['ProfitMargin > 5 year average'] = df.apply(lambda x: higher_than(x['ttm_ProfitMargin'], x['ttm_ProfitMargin5yAvg']), axis=1)
    df['P/E < 3 year average'] = df.apply(lambda x: lower_than(x['ttm_P/E'], x['ttm_P/E_3y_avg']), axis=1)
    df['P/E < 5 year average'] = df.apply(lambda x: lower_than(x['ttm_P/E'], x['ttm_P/E_5y_avg']), axis=1)
    df['P/S < 3 year average'] = df.apply(lambda x: lower_than(x['ttm_P/S'], x['ttm_P/S_3y_avg']), axis=1)
    df['P/S < 5 year average'] = df.apply(lambda x: lower_than(x['ttm_P/S'], x['ttm_P/S_5y_avg']), axis=1)

    df['Total Score'] = df[indicators.alerts].sum(axis=1)

    df = df[['Stock', 'date', 'end'] + indicators.alerts + ['Total Score']]
    df = df.dropna(thresh=4).reset_index(drop=True)
    df = df.replace(np.nan, 0)
    df = df.sort_values('Total Score', ascending=False)
    df.to_csv(f'{mypaths.current_data_folder_path}\\alerts_data.csv')
