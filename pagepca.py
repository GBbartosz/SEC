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


class KeeperPCA:
    def __init__(self, main_folder_path, tickers, indicators):
        self.main_folder_path = main_folder_path
        self.tickers = tickers
        self.indicators = indicators

        self.current_year = datetime.datetime.now().year
        self.periods = ([p for p in list(range(2010, self.current_year + 1))] + ['Current'])[::-1]
        self.period = 'Current'


class PCACalculation:
    def __init__(self, keeper):
        self.keeper = keeper

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
                df = df.drop(['date',
                              'end',
                              'year',
                              'quarter',
                              'dividends',
                              'stock_splits',
                              'Net_Income_AAGR_3y',
                              'Net_Income_AAGR_5y',
                              'Revenue_AAGR_3y',
                              'Revenue_AAGR_5y'], axis=1)
                if total_df is None:
                    total_df = df
                else:
                    total_df = pd.concat([total_df, df])

        total_df = total_df.dropna(axis=1)  # drop columns with any nan value
        self.total_df = total_df

        scaler = preprocessing.StandardScaler()
        scaled_df = scaler.fit_transform(total_df)
        self.pca = PCA()
        self.X = self.pca.fit_transform(scaled_df)


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

        self.fig.update_layout(width=800,
                               height=700)
        self.fig.update_xaxes(title_text="PCA 0")
        self.fig.update_yaxes(title_text="PCA 1")


def page_pca(indicators, tickers, main_folder_path):

    keeper1 = KeeperPCA(main_folder_path, tickers, indicators)
    keeper2 = KeeperPCA(main_folder_path, tickers, indicators)

    div_scree_height = '50vh'
    div_heatmap_height = '900'
    div_pca_scatter_height = '80vh'

    layout = html.Div([
        dash_obj.navigation_menu(3),
        html.Div([
            html.Div([
                html.Div(dash_obj.dd_single('dd_period_1', 'Select Period', keeper1.periods)),
                html.Div([dcc.Graph(id='scree_plot_1')], style={'height': div_scree_height}),
                html.Div(dcc.Graph(id='component_heatmap_1'), style={'height': div_heatmap_height}),
                html.Div(dcc.Graph(id='pca_scatter_1', style={'width': '50vh', 'textAligh': 'center'}), style={'width': '50vh', 'height': div_pca_scatter_height, 'textAligh': 'center'})
                ], style={'width': '49.5%', 'display': 'inline-block'}),
            html.Div([
                html.Div(dash_obj.dd_single('dd_period_2', 'Select Period', keeper2.periods)),
                html.Div([dcc.Graph(id='scree_plot_2')], style={'height': div_scree_height}),
                html.Div(dcc.Graph(id='component_heatmap_2'), style={'height': div_heatmap_height}),
                html.Div(dcc.Graph(id='pca_scatter_2', style={'width': '50vh', 'textAligh': 'center'}), style={'width': '50vh', 'height': div_pca_scatter_height, 'textAligh': 'center'})
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
        if value is not None:
            keeper2.period = value
            mypca2 = PCACalculation(keeper2)
            screeplot2 = ScreePlot(keeper2, mypca2)
            heatmap2 = PCAHeatMap(mypca2)
            pcascatter2 = PCAScatter(mypca2)
        return screeplot2.fig, heatmap2.fig, pcascatter2.fig
