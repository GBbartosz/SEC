import os
import pandas as pd
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
    files = os.listdir(processed_folder_path)

    indicators = Indicators()

    for indicator in [indicators.all_indicators[0]]:
        print(indicator)
        values_df = None
        for f in files:
            ticker = f[:f.find('_')]
            df = pd.read_csv(f'{processed_folder_path}{f}')[['date', indicator]]
            df[indicator] = df[indicator].bfill()
            df = df.rename(columns={indicator: ticker})

            values_df = df if values_df is None else pd.merge(values_df, df, on='date', how='outer')

        tickers = values_df.columns[1:]  # omitting dates
        corr_df = pd.DataFrame(index=tickers, columns=tickers)
        for tic1 in tickers:
            for tic2 in tickers:
                corr_calculation_df = values_df[[tic1, tic2]].dropna()
                if tic1 != tic2:
                    correlation = corr_calculation_df[tic1].corr(corr_calculation_df[tic2])
                else:
                    correlation = 1
                corr_df.loc[tic1, tic2] = correlation

        print(corr_df)

pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
#current_data(main_folder_path)
correlation(main_folder_path)
