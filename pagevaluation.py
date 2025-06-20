import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output

import dashboard_objects as dash_obj

from app import app


class Valuation:
    def __init__(self, current_df):
        self.current_df = current_df

        self.ticker = None
        self.df = None

        self.predicted_pe = None
        self.predicted_net_income_cagr = None
        self.predicted_period = None
        self.net_income_growth_valuation_result = None
        self.net_income_growth_valuation_change = None

        self.predicted_ps = None
        self.predicted_revenue_cagr  = None
        self.predicted_rv_period = None
        self.revenue_growth_valuation_result = None
        self.revenue_growth_valuation_change = None

    def select_ticker(self, ticker):
        self.ticker = ticker
        self.df = self.current_df[self.current_df['Stock'] == ticker].reset_index()

    def net_income_growth_valuation_calculation(self):
        if all(p is not None for p in [self.predicted_pe, self.predicted_net_income_cagr, self.predicted_period]):
            future_net_income = self.df['ttm_NetIncome'] * ((self.predicted_net_income_cagr + 1) ** self.predicted_period)
            future_eps = future_net_income / self.df['Shares']
            self.net_income_growth_valuation_result = (self.predicted_pe * future_eps).round(2)
            self.net_income_growth_valuation_change = (self.net_income_growth_valuation_result / self.df['close'] - 1).round(3)
        else:
            self.net_income_growth_valuation_result = None
            self.net_income_growth_valuation_change = None

    def revenue_growth_valuation_calculation(self):
        if all(p is not None for p in [self.predicted_ps, self.predicted_revenue_cagr, self.predicted_rv_period]):
            future_revenue = self.df['ttm_Revenue'] * ((self.predicted_revenue_cagr + 1) ** self.predicted_rv_period)
            future_rps = future_revenue / self.df['Shares']
            self.revenue_growth_valuation_result = (self.predicted_ps * future_rps).round(2)
            self.revenue_growth_valuation_change = (self.revenue_growth_valuation_result / self.df['close'] - 1).round(3)
        else:
            self.revenue_growth_valuation_result = None
            self.revenue_growth_valuation_change = None

    def pm_graph_obj(self, columns):
        table_df = self.df[columns]
        fig = go.Figure(go.Table(cells=dict(values=table_df.T.reset_index().T)))
        fig.update_layout(margin=dict(r=0, l=0, t=0, b=0))
        graph_obj = dcc.Graph(figure=fig, style={'width': '40vh', 'height': '20vh'})
        return graph_obj


def page_valuation(main_folder_path):

    df = pd.read_csv(f'{main_folder_path}current_data\\current_data.csv')
    tickers = df['Stock']
    valuation = Valuation(df)

    input_label_width = '20vh'
    input_width = '9vh'
    input_height = '3vh'

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(5)),
        html.Div(html.H1(id='ticker_name', children='Ticker not selected')),
        html.Div(html.H3(id='ticker_price', children='')),
        html.Div(dash_obj.dd_single('dd_tickers', 'Select Stock', tickers, None)),
        html.Div([
            html.Div(html.H3(children='Present metrics')),
            html.Div([
                html.Div(id='pm_pe', style={'display': 'inline-block'}),
                html.Div(id='pm_cagr', style={'display': 'inline-block'}),
                html.Div(id='pm_ps', style={'display': 'inline-block'}),
                html.Div(id='pm_revenue_cagr', style={'display': 'inline-block'})
            ])
        ]),
        # PE valuation
        html.Div([
            html.Div(html.H3('Net income growth valuation'), style={'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.Div(html.H5('Predicted PE'), style={'display': 'inline-block', 'width': input_label_width, 'height': input_height, 'textAlign': 'right', 'marginRight': '1vh'}),
                    html.Div(dcc.Input(id='pe_input', type='number', style={'width': '10vh'}), style={'display': 'inline-block', 'width': input_width, 'height': input_height})
                ], style={'width': '30vh'}),
                html.Div([
                    html.Div(html.H5('Predicted income growth'), style={'display': 'inline-block', 'width': input_label_width, 'height': input_height, 'textAlign': 'right', 'marginRight': '1vh'}),
                    html.Div(dcc.Input(id='cagr_growth_input', type='number', style={'width': '10vh'}), style={'display': 'inline-block', 'width': input_width, 'height': input_height})
                ], style={'width': '30vh'}),
                html.Div([
                    html.Div(html.H5('Time period'), style={'display': 'inline-block', 'width': input_label_width, 'height': input_height, 'textAlign': 'right', 'marginRight': '1vh'}),
                    html.Div(dcc.Input(id='period_input', type='number', style={'width': '10vh'}), style={'display': 'inline-block', 'width': input_width, 'height': input_height})
                ], style={'width': '30vh'}),
                html.Div([
                    html.Div(html.H5(children='Price:', style={'height': '2vh'}), style={'display': 'inline-block', 'marginRight': '1vh', 'height': '2vh', 'padding': 0, 'margin': 0}),
                    html.Div(html.H5(id='net_income_growth_valueation_result', style={'height': '2vh'}), style={'display': 'inline-block', 'height': '2vh', 'padding': 0, 'margin': 0})
                ], style={'textAlign': 'center'}),
                html.Div([
                    html.Div(html.H5(children='Change:', style={'height': '1vh', 'padding': 0, 'margin': 0}), style={'display': 'inline-block', 'marginRight': '1vh', 'height': '1vh'}),
                    html.Div(html.H5(id='net_income_growth_valueation_change', style={'height': '1vh', 'padding': 0, 'margin': 0}), style={'display': 'inline-block', 'height': '1vh'})
                ], style={'textAlign': 'center', 'marginBottom': '2vh'})
            ])
        ], style={'width': '35vh', 'border': '2px solid black', 'border-radius': '10px', 'display': 'inline-block', 'marginRight': '0.5%'}),
        # PS valuation
        html.Div([
            html.Div(html.H3('Revenue growth valuation'), style={'textAlign': 'center'}),
            html.Div([
                html.Div([
                    html.Div(html.H5('Predicted PS'), style={'display': 'inline-block', 'width': input_label_width, 'height': input_height, 'textAlign': 'right', 'marginRight': '1vh'}),
                    html.Div(dcc.Input(id='ps_input', type='number', style={'width': '10vh'}), style={'display': 'inline-block', 'width': input_width, 'height': input_height})
                ], style={'width': '30vh'}),
                html.Div([
                    html.Div(html.H5('Predicted revenue growth'), style={'display': 'inline-block', 'width': input_label_width, 'height': input_height, 'textAlign': 'right', 'marginRight': '1vh'}),
                    html.Div(dcc.Input(id='revenue_cagr_growth_input', type='number', style={'width': '10vh'}), style={'display': 'inline-block', 'width': input_width, 'height': input_height})
                ], style={'width': '30vh'}),
                html.Div([
                    html.Div(html.H5('Time period'), style={'display': 'inline-block', 'width': input_label_width, 'height': input_height, 'textAlign': 'right', 'marginRight': '1vh'}),
                    html.Div(dcc.Input(id='rv_period_input', type='number', style={'width': '10vh'}), style={'display': 'inline-block', 'width': input_width, 'height': input_height})
                ], style={'width': '30vh'}),
                html.Div([
                    html.Div(html.H5(children='Price:', style={'height': '2vh'}), style={'display': 'inline-block', 'marginRight': '1vh', 'height': '2vh', 'padding': 0, 'margin': 0}),
                    html.Div(html.H5(id='revenue_growth_valuation_result', style={'height': '2vh'}), style={'display': 'inline-block', 'height': '2vh', 'padding': 0, 'margin': 0})
                ], style={'textAlign': 'center'}),
                html.Div([
                    html.Div(html.H5(children='Change:', style={'height': '1vh', 'padding': 0, 'margin': 0}), style={'display': 'inline-block', 'marginRight': '1vh', 'height': '1vh'}),
                    html.Div(html.H5(id='revenue_growth_valuation_change', style={'height': '1vh', 'padding': 0, 'margin': 0}), style={'display': 'inline-block', 'height': '1vh'})
                ], style={'textAlign': 'center', 'marginBottom': '2vh'})
            ])
        ], style={'width': '35vh', 'border': '2px solid black', 'border-radius': '10px', 'display': 'inline-block'})
    ])

    dash.register_page('ValuationPage', path='/valuation', layout=page_layout)

    @app.callback(
        [Output(component_id='ticker_name', component_property='children'),
         Output(component_id='ticker_price', component_property='children'),
         Output(component_id='pm_pe', component_property='children'),
         Output(component_id='pm_cagr', component_property='children'),
         Output(component_id='pm_ps', component_property='children'),
         Output(component_id='pm_revenue_cagr', component_property='children')],
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_ticker(value):
        if value is not None:
            print(value)
            valuation.select_ticker(value)
            pm_pe_table = valuation.pm_graph_obj(['ttm_PE', 'ttm_PE_1y_avg', 'ttm_PE_3y_avg', 'ttm_PE_5y_avg'])
            pm_cagr_table = valuation.pm_graph_obj(['NetIncomeCAGR3y', 'NetIncomeCAGR5y'])
            pm_ps_table = valuation.pm_graph_obj(['ttm_PS', 'ttm_PS_1y_avg', 'ttm_PS_3y_avg', 'ttm_PS_5y_avg'])
            pm_revenue_cagr_table = valuation.pm_graph_obj(['RevenueCAGR3y', 'RevenueCAGR5y'])
            return valuation.ticker, valuation.df['close'], pm_pe_table, pm_cagr_table, pm_ps_table, pm_revenue_cagr_table

    ############ PE valuation ############
    @app.callback(
        [Output(component_id='net_income_growth_valueation_result', component_property='children', allow_duplicate=True),
         Output(component_id='net_income_growth_valueation_change', component_property='children', allow_duplicate=True)],
        Input(component_id='pe_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_pe(value):
        if value is not None:
            valuation.predicted_pe = value
            valuation.net_income_growth_valuation_calculation()
        return valuation.net_income_growth_valuation_result, valuation.net_income_growth_valuation_change

    @app.callback(
        [Output(component_id='net_income_growth_valueation_result', component_property='children', allow_duplicate=True),
         Output(component_id='net_income_growth_valueation_change', component_property='children', allow_duplicate=True)],
        Input(component_id='cagr_growth_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_net_income_cagr(value):
        if value is not None:
            valuation.predicted_net_income_cagr = value
            valuation.net_income_growth_valuation_calculation()
        return valuation.net_income_growth_valuation_result, valuation.net_income_growth_valuation_change

    @app.callback(
        [Output(component_id='net_income_growth_valueation_result', component_property='children', allow_duplicate=True),
         Output(component_id='net_income_growth_valueation_change', component_property='children', allow_duplicate=True)],
        Input(component_id='period_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_period(value):
        if value is not None:
            valuation.predicted_period = value
            valuation.net_income_growth_valuation_calculation()
        return valuation.net_income_growth_valuation_result, valuation.net_income_growth_valuation_change

############ PS valuation ############
    @app.callback(
        [Output(component_id='revenue_growth_valuation_result', component_property='children', allow_duplicate=True),
         Output(component_id='revenue_growth_valuation_change', component_property='children', allow_duplicate=True)],
        Input(component_id='ps_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_ps(value):
        if value is not None:
            valuation.predicted_ps = value
            valuation.revenue_growth_valuation_calculation()
        return valuation.revenue_growth_valuation_result, valuation.revenue_growth_valuation_change

    @app.callback(
        [Output(component_id='revenue_growth_valuation_result', component_property='children', allow_duplicate=True),
         Output(component_id='revenue_growth_valuation_change', component_property='children', allow_duplicate=True)],
        Input(component_id='revenue_cagr_growth_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_revenue_cagr(value):
        if value is not None:
            valuation.predicted_revenue_cagr = value
            valuation.revenue_growth_valuation_calculation()
        return valuation.revenue_growth_valuation_result, valuation.revenue_growth_valuation_change

    @app.callback(
        [Output(component_id='revenue_growth_valuation_result', component_property='children', allow_duplicate=True),
         Output(component_id='revenue_growth_valuation_change', component_property='children', allow_duplicate=True)],
        Input(component_id='rv_period_input', component_property='value'),
        prevent_initial_call=True
    )
    def input_rv_period(value):
        if value is not None:
            valuation.predicted_rv_period = value
            valuation.revenue_growth_valuation_calculation()
        return valuation.revenue_growth_valuation_result, valuation.revenue_growth_valuation_change

