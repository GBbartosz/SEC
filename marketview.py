import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import dashboard_objects as dash_obj
from matplotlib import colors as mcolors
from app import app


def page_marketview(main_folder_path):
    tickers_df = pd.read_excel(f'{main_folder_path}tickers_data.xlsx')

    industries = tickers_df['industry'].unique()
    for industry in industries:
        industry_df = tickers_df.query('industry == @industry')
        for ticker in industry_df['ticker']:
            ticdf = pd.read_csv(f'{main_folder_path}processed_data\\{ticker}_processed.csv')
            #print(ticdf.head())


    sectors = tickers_df['sector'].unique()


    layout_market_view = html.Div([
        dash_obj.navigation_menu(8),
        html.Div([dash_obj.dd_single('dd_industry_sector', 'Select industry or sector', ['industry', 'sector'], 'industry')], style={'width': '12%'})
    ])


    #dash.register_page('MarketViewPage', path='/marketview', layout=layout_market_view)


main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
page_marketview(main_folder_path)
