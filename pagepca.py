import dash
import datetime
import os
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
from sklearn import preprocessing
from sklearn.decomposition import PCA

from app import app
import dashboard_objects as dash_obj
from functions import color_generator
from indicator2 import Indicators2


class KeeperPCA:
    def __init__(self, main_folder_path, tickers, indicators):
        self.main_folder_path = main_folder_path
        self.tickers = tickers
        self.indicators = indicators
        self.indicator1 = None
        self.indicator2 = None

        self.current_year = datetime.datetime.now().year
        self.periods = ([p for p in list(range(2010, self.current_year + 1))] + ['Current'])[::-1]
        self.period = None


class PCACalculation:
    def __init__(self, keeper):
        self.keeper = keeper

        if self.keeper.period is not None:
            processed_folder_path = f'{self.keeper.main_folder_path}processed_data\\'
            files = os.listdir(processed_folder_path)
            total_df = None
            for f in files:
                ticker = f[:f.find('_')]
                if ticker in self.keeper.tickers:

                    # read csv
                    df = pd.read_csv(f'{processed_folder_path}{f}')
                    df['end'] = pd.to_datetime(df['end'])
                    df = df.dropna(subset=['end'])

                    # filter period
                    if keeper.period == 'Current':
                        max_index = df['end'].idxmax()
                        df = df.loc[[max_index]]
                    else:
                        if keeper.period in df['end'].dt.year.tolist():
                            df = df[df['end'].dt.year == keeper.period]
                            min_index = df['end'].idxmin()
                            df = df.loc[[min_index]]  # first end date in year
                        else:
                            continue

                    # concat
                    df.index = [ticker]
                    if total_df is None:
                        total_df = df
                    else:
                        total_df = pd.concat([total_df, df])

            self.all_indicators_df = total_df.copy()
            total_df = total_df.drop(['date',
                                      'end',
                                      'year',
                                      'quarter',
                                      'dividends',
                                      'stock_splits',
                                      'close',
                                      'NetIncomeAAGR3y',
                                      'NetIncomeAAGR5y',
                                      'RevenueAAGR3y',
                                      'RevenueAAGR5y'], axis=1)
            total_df = total_df.dropna(axis=1)  # drop columns with any nan value
            self.total_df = total_df

            scaler = preprocessing.StandardScaler()
            print(total_df)
            scaled_df = scaler.fit_transform(total_df)
            self.pca = PCA()
            self.X = self.pca.fit_transform(scaled_df)
            print(self.X)


class ScreePlot:
    def __init__(self, keeper, mypca):
        self.tickers = keeper.tickers
        self.indicators = keeper.indicators
        self.period = keeper.period

        self.fig = go.Figure(go.Bar(name='Scree Plot',
                                    x=mypca.pca.get_feature_names_out(),
                                    y=mypca.pca.explained_variance_ratio_))
        self.fig.update_layout(title='Scree Plot')


class PCAHeatMap:
    def __init__(self, mypca):
        self.fig = px.imshow((mypca.pca.components_**2).round(2).T,
                             x=mypca.pca.get_feature_names_out(),
                             y=mypca.total_df.columns,
                             text_auto=True,
                             height=900)
        self.fig.update_layout(font=dict(size=9))


class PCAScatter:
    # when there are lacking tickers for this period it means there is no available data
    # there are few tickers for current year (not 'Current') because it takes min end date from this year. So not all companies released financial statements yet
    def __init__(self, mypca):
        self.fig = go.Figure()
        for i in list(range(len(mypca.X))):
            ticker = mypca.total_df.index[i]
            self.fig.add_trace(go.Scatter(x=[mypca.X[i][0]],
                                          y=[mypca.X[i][1]],
                                          name=ticker,
                                          marker=dict(symbol='circle-open',
                                                      size=14,
                                                      color=color_generator(ticker),
                                                      opacity=0.8,
                                                      line=dict(width=2))
                                          )
                               )

        self.fig.update_layout(width=900,
                               height=700)
        self.fig.update_xaxes(title_text="PCA 0")
        self.fig.update_yaxes(title_text="PCA 1")


class IndicatorScatter:
    def __init__(self, keeper, mypca):
        self.fig = go.Figure()
        if keeper.indicator1 is not None and keeper.indicator2 is not None:
            for ticker in keeper.tickers:
                self.fig.add_trace(go.Scatter(x=[mypca.all_indicators_df[keeper.indicator1][ticker]],
                                              y=[mypca.all_indicators_df[keeper.indicator2][ticker]],
                                              name=ticker,
                                              marker=dict(size=14,
                                                          color=color_generator(ticker),
                                                          opacity=0.8))
                                   )
        self.fig.update_layout(width=900,
                               height=700)
        self.fig.update_xaxes(title_text=keeper.indicator1)
        self.fig.update_yaxes(title_text=keeper.indicator2)


def page_pca(tickers, main_folder_path):

    indicators = Indicators2()

    keeper1 = KeeperPCA(main_folder_path, tickers, indicators)
    keeper2 = KeeperPCA(main_folder_path, tickers, indicators)

    mypca1 = PCACalculation(keeper1)
    mypca2 = PCACalculation(keeper2)

    div_scree_height = '50vh'
    div_heatmap_height = '900'
    div_pca_scatter_height = '80vh'

    layout = html.Div([
        dash_obj.navigation_menu(3),
        html.Div([
            html.Div([
                html.Div(dash_obj.dd_single('dd_period_1', 'Select Period', keeper1.periods)),
                #html.Div(dash_obj.dd_indicators('dd_indicators_1', 'Select Indicators', keeper1.indicators, [None])),
                html.Div([dcc.Graph(id='scree_plot_1')], style={'height': div_scree_height}),
                html.Div(dcc.Graph(id='component_heatmap_1'), style={'height': div_heatmap_height}),
                html.Div(dcc.Graph(id='pca_scatter_1'), style={'textAligh': 'center'}),
                html.Div([
                    html.Div([
                        html.Div(dash_obj.dd_single('dd_indicator_11', 'Select Indicator X', keeper1.indicators.all_indicators), style={'width': '40vh', 'display': 'inline-block', 'marginRight': '0.5'}),
                        html.Div(dash_obj.dd_single('dd_indicator_12', 'Select Indicator Y', keeper1.indicators.all_indicators), style={'width': '40vh', 'display': 'inline-block', 'marginLeft': '0.5'})
                    ], style={'textAlign': 'center'}),
                    html.Div(dcc.Graph(id='indicator_scatter_1'))
                ])
            ], style={'width': '49.5%', 'display': 'inline-block'}),
            html.Div([
                html.Div(dash_obj.dd_single('dd_period_2', 'Select Period', keeper2.periods)),
                html.Div([dcc.Graph(id='scree_plot_2')], style={'height': div_scree_height}),
                html.Div(dcc.Graph(id='component_heatmap_2'), style={'height': div_heatmap_height}),
                html.Div(dcc.Graph(id='pca_scatter_2'), style={'textAligh': 'center'}),
                html.Div([
                    html.Div([
                        html.Div(dash_obj.dd_single('dd_indicator_21', 'Select Indicator X',
                                                    keeper1.indicators.all_indicators),
                                 style={'width': '40vh', 'display': 'inline-block', 'marginRight': '0.5'}),
                        html.Div(dash_obj.dd_single('dd_indicator_22', 'Select Indicator Y',
                                                    keeper1.indicators.all_indicators),
                                 style={'width': '40vh', 'display': 'inline-block', 'marginLeft': '0.5'})
                    ], style={'textAlign': 'center'}),
                    html.Div(dcc.Graph(id='indicator_scatter_2'))
                ])
            ], style={'width': '49.5%', 'display': 'inline-block', 'textAlign': 'Right'})
        ], style={'display': 'flex', 'justifyContent': 'space-between'})
    ])

    dash.register_page('PCAPage', path='/pca', layout=layout)

    @app.callback(
        [Output(component_id='scree_plot_1', component_property='figure'),
         Output(component_id='component_heatmap_1', component_property='figure'),
         Output(component_id='pca_scatter_1', component_property='figure')],
        Input(component_id='dd_period_1', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_period_1(value):
        nonlocal keeper1, mypca1
        if value is not None:
            keeper1.period = value
            mypca1 = PCACalculation(keeper1)
            screeplot1 = ScreePlot(keeper1, mypca1)
            heatmap1 = PCAHeatMap(mypca1)
            pcascatter1 = PCAScatter(mypca1)
        return screeplot1.fig, heatmap1.fig, pcascatter1.fig

    @app.callback(
        [Output(component_id='scree_plot_2', component_property='figure'),
         Output(component_id='component_heatmap_2', component_property='figure'),
         Output(component_id='pca_scatter_2', component_property='figure')],
        Input(component_id='dd_period_2', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_period_2(value):
        nonlocal keeper2, mypca2
        if value is not None:
            keeper2.period = value
            mypca2 = PCACalculation(keeper2)
            screeplot2 = ScreePlot(keeper2, mypca2)
            heatmap2 = PCAHeatMap(mypca2)
            pcascatter2 = PCAScatter(mypca2)
        return screeplot2.fig, heatmap2.fig, pcascatter2.fig

    #@app.callback(
    #    [Output(component_id='scree_plot_1', component_property='figure', allow_duplicate=True),
    #     Output(component_id='component_heatmap_1', component_property='figure', allow_duplicate=True),
    #     Output(component_id='pca_scatter_1', component_property='figure', allow_duplicate=True)],
    #    Input(component_id='dd_indicators_1', component_property='value'),
    #    prevent_initial_call=True
    #)
    #def dropdown_selection_indicators_1(value):
    #    nonlocal keeper1, mypca1
    #    if value is not None:
    #        print('xxx')
    #        keeper1.indicators = [value]
    #        mypca1 = PCACalculation(keeper1)
    #        screeplot1 = ScreePlot(keeper1, mypca1)
    #        heatmap1 = PCAHeatMap(mypca1)
    #        pcascatter1 = PCAScatter(mypca1)
    #    return screeplot1.fig, heatmap1.fig, pcascatter1.fig

    @app.callback(
        Output(component_id='indicator_scatter_1', component_property='figure'),
        Input(component_id='dd_indicator_11', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_indicator_11(value):
        nonlocal keeper1, mypca1
        if value is not None:
            keeper1.indicator1 = value
            indicator_scatter1 = IndicatorScatter(keeper1, mypca1)
        return indicator_scatter1.fig

    @app.callback(
        Output(component_id='indicator_scatter_1', component_property='figure', allow_duplicate=True),
        Input(component_id='dd_indicator_12', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_indicator_12(value):
        nonlocal keeper1, mypca1
        if value is not None:
            keeper1.indicator2 = value
            indicator_scatter1 = IndicatorScatter(keeper1, mypca1)
        return indicator_scatter1.fig

    @app.callback(
        Output(component_id='indicator_scatter_2', component_property='figure'),
        Input(component_id='dd_indicator_21', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_indicator_21(value):
        nonlocal keeper2, mypca2
        if value is not None:
            keeper2.indicator1 = value
            indicator_scatter2 = IndicatorScatter(keeper2, mypca2)
        return indicator_scatter2.fig

    @app.callback(
        Output(component_id='indicator_scatter_2', component_property='figure', allow_duplicate=True),
        Input(component_id='dd_indicator_22', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_indicator_22(value):
        nonlocal keeper2, mypca2
        if value is not None:
            keeper2.indicator2 = value
            indicator_scatter2 = IndicatorScatter(keeper2, mypca2)
        return indicator_scatter2.fig
