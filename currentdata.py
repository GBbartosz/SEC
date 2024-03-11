import os
import pandas as pd
from functions import pandas_df_display_options


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
                                  'stock_splits',
                                  'Revenues',
                                  'SalesRevenueNet',
                                  'RevenueFromContractWithCustomerExcludingAssessedTax',
                                  'NetIncomeLoss',
                                  'ttm_Revenues',
                                  'ttm_SalesRevenueNet',
                                  'ttm_RevenueFromContractWithCustomerExcludingAssessedTax'])
    current_df = current_df.T

    print(current_df)

    current_df.to_csv(f'{current_data_folder}current_data.csv')


pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
current_data(main_folder_path)
