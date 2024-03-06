import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go
import random
from functions import plotly_markers, ticker_color_dict
from indicator import Indicators
import dashboard_objects as dash_obj


class Keeper:
    def __init__(self):
        self.tickers = []
        self.indicators = []


class MainChart:
    def __init__(self):
        self.processed_folder_path = f'C:\\Users\\barto\\Desktop\\SEC2024\\processed_data\\'
        self.tickers = keeper.tickers
        self.indicators = keeper.indicators
        self.fig = go.Figure()
        for ticker in self.tickers:
            df = pd.read_csv(f'{self.processed_folder_path}{ticker}_processed.csv')

            if ticker in ticker_color_dict.keys():
                color = ticker_color_dict[ticker]
            else:
                color = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
            m = 0
            for indicator in self.indicators:
                x = df['date']
                try:
                    y = df[indicator]
                except KeyError:
                    df[indicator] = np.nan
                    y = df[indicator]

                size = 4 if len([ynn for ynn in y if not np.isnan(ynn)]) > 1000 else 8

                self.fig.add_trace(go.Scatter(name=ticker,
                                              x=x,
                                              y=y,
                                              mode='lines+markers',
                                              marker=dict(symbol=plotly_markers[m], size=size),
                                              line=dict(color=color)))
                m += 1
        self.fig.update_traces(connectgaps=True)


def pandas_df_display_options():
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 400)


def read_files():
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    processed_folder_path = f'{main_folder_path}processed_data\\'
    files = os.listdir(processed_folder_path)
    tickers = [f[:f.find('_')] for f in files]
    print(tickers)
    return tickers


def main_page(indicators):
    global tickers

    layout_main_page = html.Div([
        html.Div([
            html.Div([dash_obj.dd_indicators(indicators.all_indicators)], style={'width': '50%', 'display': 'inline-block'}),
            html.Div([dash_obj.dd_tickers(tickers)], style={'width': '50%', 'display': 'inline-block'})
            ], style={'width': '100%', 'height': '20%'}),
        html.Div([dcc.Graph(id='MainChart', style={'width': '90%', 'height': '90vh'})], style={'height': '80%', 'text-align': 'center'})
    ])

    dash.register_page('MainPage', path='/', layout=layout_main_page)

    @app.callback(
        Output(component_id='MainChart', component_property='figure'),
        Input(component_id='dd_indicators', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_indicator(chosen_val):
        keeper.indicators = list(chosen_val)
        return MainChart().fig

    @app.callback(
        Output(component_id='MainChart', component_property='figure', allow_duplicate=True),
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_ticker(chosen_val):
        keeper.tickers = list(chosen_val)
        return MainChart().fig


tickers = read_files()
indicators = Indicators()
keeper = Keeper()

app = dash.Dash(__name__, pages_folder="", use_pages=True)

main_page(indicators)
app.run_server(debug=True)
