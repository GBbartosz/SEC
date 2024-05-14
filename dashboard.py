import os

from app import app
from functions import pandas_df_display_options
from indicator2 import Indicators2
from pagemain import main_page
from pagecorrelation import correlation_page
from pagecurrentdatatable import current_status
from pagepca import page_pca
from pagealerts import page_alerts
from pagevaluation import page_valuation


def read_files(my_main_folder_path):
    processed_folder_path = f'{my_main_folder_path}processed_data\\'
    files = os.listdir(processed_folder_path)
    tickers = [f[:f.find('_')] for f in files]
    #print(tickers)
    return tickers


if __name__ == "__main__":
    pandas_df_display_options()
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    tickers = read_files(main_folder_path)
    indicators = Indicators2()

    main_page(indicators, tickers, main_folder_path)
    current_status(main_folder_path)
    correlation_page(tickers, main_folder_path)
    page_pca(tickers, main_folder_path)
    page_alerts(main_folder_path)
    page_valuation(main_folder_path)

    app.run_server(debug=True)
