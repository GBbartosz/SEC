import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
from dash import dcc, html
from dash.dependencies import Input, Output

import dashboard_objects as dash_obj

from app import app
from functions import Keeper, plotly_lines, plotly_markers, ticker_color_dict


class MainChart:
    def __init__(self, keeper, main_folder_path):

        self.processed_folder_path = f'{main_folder_path}processed_data\\'
        self.tickers = keeper.tickers
        self.indicators = keeper.indicators + keeper.indicators2
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

                # selecting yaxis base on chosen dropdown
                yaxis = 'y' if indicator in keeper.indicators else 'y2'

                self.fig.add_trace(go.Scatter(name=f'{ticker}, {indicator}',
                                              x=x,
                                              y=y,
                                              mode=mode,
                                              line=dict(dash=plotly_lines[line_idx], color=color),
                                              marker=dict(symbol=plotly_markers[marker_idx], color=color, size=8),
                                              hovertemplate='(%{x}, %{y:.2f})',
                                              yaxis=yaxis
                                              )
                                   )

        self.fig.update_traces(connectgaps=True)
        self.fig.update_layout(hovermode='closest',
                               yaxis2=dict(overlaying='y', side='right')
                               )


def main_page(indicators, tickers, main_folder_path):

    keeper = Keeper()

    layout_main_page = html.Div([
        dash_obj.navigation_menu(0),
        html.Div([
            html.Div([dash_obj.dd_indicators('dd_indicators', 'Select indicator (left y-axis)', indicators.all_indicators, None)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dash_obj.dd_indicators('dd_indicators2', 'Select indicator (right y-axis)', indicators.all_indicators, None)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dash_obj.dd_indicators('dd_tickers', 'Select stock', tickers, None)], style={'width': '30%', 'display': 'inline-block'})
            ], style={'width': '100%', 'height': '6vh'}),
        html.Div([dcc.Graph(id='MainChart', style={'width': '100%', 'height': '88vh'})], style={'text-align': 'center'})
    ])

    dash.register_page('MainPage', path='/', layout=layout_main_page)

    @app.callback(
        Output(component_id='MainChart', component_property='figure'),
        Input(component_id='dd_indicators', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_indicator(chosen_val):
        keeper.indicators = list(chosen_val)
        return MainChart(keeper, main_folder_path).fig

    @app.callback(
        Output(component_id='MainChart', component_property='figure', allow_duplicate=True),
        Input(component_id='dd_indicators2', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_indicator2(chosen_val):
        keeper.indicators2 = list(chosen_val)
        return MainChart(keeper, main_folder_path).fig

    @app.callback(
        Output(component_id='MainChart', component_property='figure', allow_duplicate=True),
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_ticker(chosen_val):
        keeper.tickers = list(chosen_val)
        return MainChart(keeper, main_folder_path).fig
