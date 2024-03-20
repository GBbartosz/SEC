import os
import pandas as pd
from datetime import timedelta
from functions import pandas_df_display_options
from indicator import Indicators


def current_data(main_folder_path):
    processed_folder_path = f'{main_folder_path}processed_data\\'
    current_data_folder = f'{main_folder_path}current_data\\'
    files = os.listdir(processed_folder_path)

    current_df = None
    for f in files:
        ticker = f[:f.find('_')]
        stock_df = pd.read_csv(f'{processed_folder_path}{f}')
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

    current_df.to_csv(f'{current_data_folder}current_data.csv')


def correlation(main_folder_path):
    processed_folder_path = f'{main_folder_path}processed_data\\'
    correlation_folder_path = f'{main_folder_path}correlation_data\\'
    files = os.listdir(processed_folder_path)

    indicators = Indicators()
    period_years = [1, 2, 3, 5, 10, None]
    year_window = 252

    #for indicator in [indicators.all_indicators[0]]:
    for indicator in indicators.all_indicators:
        indicator_for_csv_file_name = indicator.replace('/', '')
        print(indicator)
        values_df = None
        for f in files:
            ticker = f[:f.find('_')]
            df = pd.read_csv(f'{processed_folder_path}{f}')[['date', indicator]]
            df[indicator] = df[indicator].bfill()
            df = df.rename(columns={indicator: ticker})

            values_df = df if values_df is None else pd.merge(values_df, df, on='date', how='outer')

        values_df['date'] = pd.to_datetime(values_df['date'])
        values_df = values_df.set_index('date')
        tickers = values_df.columns  # omitting dates

        for period_year in period_years:
            corr_df = pd.DataFrame(index=tickers, columns=tickers)
            for tic1 in tickers:
                tic1_min_index = values_df[tic1].dropna().index.min()
                tic1_max_index = values_df[tic1].dropna().index.max()
                for tic2 in tickers:
                    if tic1 != tic2:
                        tic2_min_index = values_df[tic2].dropna().index.min()
                        tic2_max_index = values_df[tic2].dropna().index.max()
                        min_index = max(tic1_min_index, tic2_min_index)
                        max_index = min(tic1_max_index, tic2_max_index)
                        if period_year is None:  # correlation for all available values for both companies not nan
                            corr_calculation_df = values_df[[tic1, tic2]][min_index:max_index]  # selecting period
                            corr_calculation_df = corr_calculation_df.bfill()  # fulfilling nan values inbetween
                            correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2])
                        else:  # correlation for selected period
                            period_ago = max_index - timedelta(days=period_year * 365)
                            if period_ago >= min_index:
                                corr_calculation_df = values_df[(values_df.index >= period_ago) & (values_df.index <= max_index)][[tic1, tic2]]  # selecting period
                                corr_calculation_df = corr_calculation_df.bfill()  # fulfilling nan values inbetween
                                correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2])
                            else:  # available data is too short compared to demanded period
                                correlation = None
                    else:  # case when correlation AAPL: AAPL
                        correlation = 1
                    corr_df.loc[tic1, tic2] = correlation

            corr_df.to_csv(f'{correlation_folder_path}correlation_{indicator_for_csv_file_name}_{period_year}.csv')


pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
#current_data(main_folder_path)
correlation(main_folder_path)
