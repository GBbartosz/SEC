import os
import time
import pandas as pd

from app import app
from functools import reduce
from functions import pandas_df_display_options
from indicator2 import Indicators2
from pagemain import main_page
from pagecorrelation import correlation_page
from pagecurrentdatatable import current_status
from pagepca import page_pca
from pagealerts import page_alerts
from pagevaluation import page_valuation
from pageupdate import page_update
from pagemarketshare import page_marketshare
from marketview import page_marketview
from pagepricechange import page_pricechange
from pageboard import page_board
from types import SimpleNamespace


def read_files(my_main_folder_path):
    processed_folder_path = f'{my_main_folder_path}processed_data\\'
    files = os.listdir(processed_folder_path)
    tickers = [f[:f.find('_')] for f in files]
    return tickers


def save_app_data(tickers_df, processed_folder_path, app_data_folder_path, cam_features):
    start_time = time.time()
    concat_l = []
    merge_l = []
    for i in tickers_df.index:
        tic = tickers_df.at[i, 'ticker']
        company_name = tickers_df.at[i, 'company_name']
        sector = tickers_df.at[i, 'sector']
        industry = tickers_df.at[i, 'industry']
        ticdf = pd.read_csv(f'{processed_folder_path}{tic}_processed.csv')

        ticdf_concat = ticdf.copy()[['date', 'end', 'year', 'quarter'] + cam_features.concated.concated_features]
        ticdf_concat['ticker'] = tic
        ticdf_concat['company_name'] = company_name
        ticdf_concat['sector'] = sector
        ticdf_concat['industry'] = industry
        concat_l.append(ticdf_concat)

        ticdf_merge = ticdf.copy()[['date', 'end', 'year', 'quarter'] + cam_features.merged.merged_features]
        ticdf_merge.columns = [f'{tic}_{c}' if c != 'date' else c for c in ticdf_merge.columns]
        merge_l.append(ticdf_merge)

    concated_df = pd.concat(concat_l, ignore_index=True)
    concated_df.to_csv(f'{app_data_folder_path}concated_df.csv', index=False)

    merged_df = reduce(lambda left, right: pd.merge(left, right, on='date', how='outer'), merge_l)
    merged_df.to_csv(f'{app_data_folder_path}merged_df.csv', index=False)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'preparing data time: {elapsed_time:.2f}')


def read_app_date(app_data_folder_path):
    concated_df = pd.read_csv(f'{app_data_folder_path}concated_df.csv')
    merged_df = pd.read_csv(f'{app_data_folder_path}merged_df.csv')
    return concated_df, merged_df


############### Concated ###############
class PageBoardFeatures:
    def __init__(self):
        self.range_features = ['close']
        self.date_features = ['PriceChangeDaily', 'ttm_PE', 'ttm_PS', 'ttm_PEG_historical_3y', 'ttm_PEG_historical_5y']
        self.quarter_features = ['ttm_Revenue', 'qq_RevenueGrowth', 'ttm_RevenueGrowth1y', 'ttm_RevenueGrowth3y', 'ttm_RevenueGrowth5y',
                                 'ttm_NetIncome', 'qq_NetIncomeGrowth', 'ttm_NetIncomeGrowth1y', 'ttm_NetIncomeGrowth3y', 'ttm_NetIncomeGrowth5y',
                                 'ttm_ProfitMargin']

        self.board_features = self.range_features + self.date_features + self.quarter_features


class Concated:
    def __init__(self):
        self.board = PageBoardFeatures()

        self.concated_features = self.board.board_features


############### Merged ###############
class PagePriceChangeFeatures:
    def __init__(self):
        self.pricechange_features = ['close']


class Merged:
    def __init__(self):
        self.pricechange = PagePriceChangeFeatures()

        self.merged_features = self.pricechange.pricechange_features


############### ALL ###############
class ConcatedAndMergedFeatures:
    def __init__(self):
        self.concated = Concated()
        self.merged = Merged()


if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # This block runs only once, not in the reloader (even when dash in debug mode)
        pandas_df_display_options()
        main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2025\\'
        processed_folder_path = f'{main_folder_path}processed_data\\'
        app_data_folder_path = f'{main_folder_path}app_data\\'
        tickers = read_files(main_folder_path)
        tickers_df = pd.read_excel(f'{main_folder_path}\\tickers_data.xlsx')
        indicators = Indicators2()

        cam_features = ConcatedAndMergedFeatures()
        #save_app_data(tickers_df, processed_folder_path, app_data_folder_path, cam_features) # saves data for further use in the app (turn off when debugging)
        concated_df, merged_df = read_app_date(app_data_folder_path)

        main_page(indicators, tickers, main_folder_path)
        current_status(main_folder_path)
        correlation_page(tickers, main_folder_path)
        page_pca(tickers, main_folder_path)
        page_alerts(main_folder_path)
        page_valuation(main_folder_path)
        page_update(main_folder_path)
        page_marketshare(tickers, main_folder_path)
        #page_marketview(main_folder_path)
        page_pricechange(tickers_df, merged_df)
        page_board(tickers_df, concated_df, cam_features)

    app.run_server(debug=True)
