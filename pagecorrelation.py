import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

import dashboard_objects as dash_obj
from app import app
from functions import Keeper
from indicator import Indicators


class CorrHMKeeper:
    def __init__(self, tickers, correlation_folder_path):
        self.correlation_folder_path = correlation_folder_path
        self.tickers = tickers
        self.indicator = None
        self.period = 'all'


class HeatMap:
    def __init__(self, keeper):
        self.fig = None
        if keeper.indicator is not None:
            period = None if keeper.period == 'all' else keeper.period
            df = pd.read_csv(f'{keeper.correlation_folder_path}correlation_{keeper.indicator}_{period}.csv', index_col=0)
            df = df.round(2)
            print(df.head())
            self.fig = px.imshow(df, text_auto=True, aspect="auto")


def correlation_page(tickers, main_folder_path):
    correlation_folder_path = f'{main_folder_path}correlation_data\\'
    indicators = Indicators()
    periods = [1, 2, 3, 5, 10, 'all']
    keeper1 = CorrHMKeeper(tickers, correlation_folder_path)
    keeper2 = CorrHMKeeper(tickers, correlation_folder_path)
    keeper3 = CorrHMKeeper(tickers, correlation_folder_path)
    keeper4 = CorrHMKeeper(tickers, correlation_folder_path)

    layout = html.Div(
        html.Div([html.Div([dash_obj.dd_single('dd_indicators1', 'Select indicator', indicators.all_indicators, None),
                            dash_obj.dd_indicators('dd_tickers1', 'Select ticker', tickers, None),
                            dash_obj.dd_single('dd_periods1', 'Select period', periods, 'all')]),
                  html.Div([dcc.Graph(id='heatmap1')])])
    )

    dash.register_page('CorrelationPage', path='/correlation', layout=layout)

    @app.callback(
        Output(component_id='heatmap1', component_property='figure'),
        Input(component_id='dd_indicators1', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_indicators1(value):
        keeper1.indicator = value
        heatmap1 = HeatMap(keeper1)
        return heatmap1.fig
