import os

import pandas as pd

from app import app
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


def read_files(my_main_folder_path):
    processed_folder_path = f'{my_main_folder_path}processed_data\\'
    files = os.listdir(processed_folder_path)
    tickers = [f[:f.find('_')] for f in files]
    #print(tickers)
    return tickers


if __name__ == "__main__":
    pandas_df_display_options()
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2025\\'
    tickers = read_files(main_folder_path)
    tickers_df = pd.read_excel(f'{main_folder_path}\\tickers_data.xlsx')
    indicators = Indicators2()

    main_page(indicators, tickers, main_folder_path)
    current_status(main_folder_path)
    correlation_page(tickers, main_folder_path)
    page_pca(tickers, main_folder_path)
    page_alerts(main_folder_path)
    page_valuation(main_folder_path)
    page_update(main_folder_path)
    page_marketshare(tickers, main_folder_path)
    #page_marketview(main_folder_path)
    page_pricechange(tickers_df, main_folder_path)

    app.run_server(debug=True)
