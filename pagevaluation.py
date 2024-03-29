import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

import dashboard_objects as dash_obj

from app import app
from functions import Keeper, plotly_lines, plotly_markers, color_generator


class Valuation:
    def __init__(self, df):
        self.df = df

        self.ticker = None
        self.series = None

        self.predicted_pe = None
        self.predicted_cagr = None
        self.predicted_period = None
        self.net_income_growth_valuation_result = None

    def select_ticker(self, ticker):
        self.ticker = ticker
        self.series = self.df[self.df['Stock'] == ticker].reset_index()

    def net_income_growth_valuation_calculation(self):
        if all(p is not None for p in [self.predicted_pe, self.predicted_cagr, self.predicted_period]):
            future_net_income = self.series['ttm_net_income_coalesce'] * ((self.predicted_cagr + 1) ** self.predicted_period)
            future_eps = future_net_income / self.series['shares']
            self.net_income_growth_valuation_result = (self.predicted_pe * future_eps).round(2)
        else:
            self.net_income_growth_valuation_result = None


def page_valuation(main_folder_path):

    df = pd.read_csv(f'{main_folder_path}current_data\\current_data.csv')
    tickers = df['Stock']
    valuation = Valuation(df)

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(5)),
        html.Div(html.H1(id='ticker_name', children='Ticker not selected')),
        html.Div(html.H3(id='ticker_price', children='')),
        html.Div(dash_obj.dd_single('dd_tickers', 'Select Stock', tickers, None)),
        html.Div([
            html.Div(html.H3(children='Present metrics')),
            html.Div(html.H5(id='present_metrics', children=None))
        ]),
        html.Div([
            html.Div(html.H3('Net income growth valuation')),
            html.Div([
                html.Div([
                    html.Div(html.H5('Predicted P/E')),
                    html.Div(html.H5('Predicted income growth')),
                    html.Div(html.H5('Time period'))
                ], style={'display': 'inline-block'}),
                html.Div([
                    html.Div(dcc.Input(id='pe_input', type='number')),
                    html.Div(dcc.Input(id='cagr_growth_input', type='number')),
                    html.Div(dcc.Input(id='period_input', type='number')),
                    html.Div(html.H5(id='net_income_growth_valueation_result'))
                ], style={'display': 'inline-block'}),
                html.Div([], style={'display': 'inline-block'})
            ])
        ])
    ])

    dash.register_page('ValuationPage', path='/valuation', layout=page_layout)


    @app.callback(
        [Output(component_id='ticker_name', component_property='children'),
         Output(component_id='ticker_price', component_property='children'),
         Output(component_id='present_metrics', component_property='children')],
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_ticker(value):
        if value is not None:
            valuation.select_ticker(value)
            present_metrics = f'''
                               P/E {valuation.series['ttm_P/E'][0]}\n
                               P/E 3 year avg {valuation.series['ttm_P/E_3y_avg'][0]} 
                               '''
        return valuation.ticker, valuation.series['close'], present_metrics

    @app.callback(
        Output(component_id='net_income_growth_valueation_result', component_property='children'),
        Input(component_id='pe_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_pe(value):
        if value is not None:
            valuation.predicted_pe = value
            valuation.net_income_growth_valuation_calculation()
        return valuation.net_income_growth_valuation_result

    @app.callback(
        Output(component_id='net_income_growth_valueation_result', component_property='children', allow_duplicate=True),
        Input(component_id='cagr_growth_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_cagr(value):
        if value is not None:
            valuation.predicted_cagr = value
            valuation.net_income_growth_valuation_calculation()
        return valuation.net_income_growth_valuation_result

    @app.callback(
        Output(component_id='net_income_growth_valueation_result', component_property='children', allow_duplicate=True),
        Input(component_id='period_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_period(value):
        if value is not None:
            valuation.predicted_period = value
            valuation.net_income_growth_valuation_calculation()
        return valuation.net_income_growth_valuation_result

