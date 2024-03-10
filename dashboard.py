import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import numpy as np
import os
import pandas as pd
import plotly.graph_objects as go
import random
from functions import plotly_lines, plotly_markers, ticker_color_dict
from indicator import Indicators
import dashboard_objects as dash_obj


class Keeper:
    def __init__(self):
        self.tickers = []
        self.indicators = []


class MainChart:
    def __init__(self):
        global main_folder_path

        self.processed_folder_path = f'{main_folder_path}processed_data\\'
        self.tickers = keeper.tickers
        self.indicators = keeper.indicators
        self.fig = go.Figure()
        for ticker in self.tickers:
            df = pd.read_csv(f'{self.processed_folder_path}{ticker}_processed.csv')

            if ticker in ticker_color_dict.keys():
                color = ticker_color_dict[ticker]
            else:
                color = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
            pl = -1
            pm = -1
            for indicator in self.indicators:
                x = df['date']
                try:
                    y = df[indicator]
                except KeyError:
                    df[indicator] = np.nan
                    y = df[indicator]

                # changing line type for data with many values (close price) and changing markers for data with few values (revenue)
                constant_line = all(False if np.isnan(a) else True for a in y[-5:-1])  # checks last 5 values if all are not nan
                if constant_line:
                    mode = 'lines'
                    pl += 1
                    line_idx = pl
                    marker_idx = 0
                else:
                    mode = 'lines+markers'
                    pm += 1
                    line_idx = 0
                    marker_idx = pm

                self.fig.add_trace(go.Scatter(name=ticker,
                                              x=x,
                                              y=y,
                                              mode=mode,
                                              line=dict(dash=plotly_lines[line_idx], color=color),
                                              marker=dict(symbol=plotly_markers[marker_idx], color=color, size=8)))

        self.fig.update_traces(connectgaps=True)


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
        html.Div([dash_obj.page_link('CurrentDataLink', 'Current Data Table', '/current_data')]),
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


def current_status():
    global main_folder_path

    current_df = pd.read_csv(f'{main_folder_path}current_data\\current_data.csv')

    layout_current_status_page = html.Div([
        html.Div(
            dash_table.DataTable(id='current_status_table',
                                 data=current_df.to_dict('records')

            )
        )
    ])

    dash.register_page('CurrentStatus', path='/current_data', layout=layout_current_status_page)


main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
tickers = read_files()
indicators = Indicators()
keeper = Keeper()

app = dash.Dash(__name__, pages_folder="", use_pages=True)

main_page(indicators)
current_status()
app.run_server(debug=True)
