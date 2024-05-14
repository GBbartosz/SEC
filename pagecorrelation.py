import dash
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

import dashboard_objects as dash_obj
from app import app
from indicator2 import Indicators2


class CorrHMKeeper:
    def __init__(self, tickers, correlation_folder_path):
        self.correlation_folder_path = correlation_folder_path
        self.tickers = tickers
        self.indicator = None
        self.period = 'all'
        self.correlation_type = 'spearman'


class HeatMap:
    def __init__(self, keeper):
        self.fig = None
        if keeper.indicator is not None:
            indicator_in_file_name = keeper.indicator.replace('/', '')
            df = pd.read_csv(f'{keeper.correlation_folder_path}correlation_{keeper.correlation_type}_{indicator_in_file_name}_{keeper.period}.csv', index_col=0)
            df = df.round(2)
            df = df.loc[keeper.tickers, keeper.tickers]
            self.fig = px.imshow(df,
                                 text_auto=True,
                                 aspect="auto",
                                 color_continuous_scale='RdBu_r',
                                 zmin=-1,
                                 zmax=1)
            self.fig.update_layout(title=f'{keeper.indicator}, years: {keeper.period}',
                                   xaxis=dict(tickfont=dict(size=8)),
                                   yaxis=dict(tickfont=dict(size=8))
                                   )


class HeatMapArea:
    def __init__(self, tickers, indicators, periods, keepers):
        self.tickers = tickers
        self.indicators = indicators
        self.periods = periods
        self.keepers = keepers
        self.keeper1 = keepers[0]
        self.keeper2 = keepers[1]
        self.keeper3 = keepers[2]
        self.keeper4 = keepers[3]

        self.heatmaps_number = 1
        self.heatmap_layout_area = None  # wartosc wprowadzono po update ponizej
        self.update()

    def get_heatmap_layout(self, i, heatmap):
        if heatmap.fig is None:
            graph_obj = dcc.Graph(id=f'heatmap{i}')
        else:
            graph_obj = dcc.Graph(id=f'heatmap{i}', figure=heatmap.fig)

        if self.heatmaps_number == 1:
            chart_width = '180vh'
            chart_height = '200vh'
        else:
            chart_width = '100vh'
            chart_height = '70vh'

        heatmap_layout = html.Div([
            html.Div([
                html.Div(dash_obj.dd_single(f'dd_indicators{i}', 'Select indicator', self.indicators.all_indicators),
                         style={'display': 'inline-block', 'width': '40vh', 'height': '3vh', 'fontSize': '12px'}),
                html.Div(dash_obj.dd_single(f'dd_periods{i}', 'Select period', self.periods),
                         style={'display': 'inline-block', 'width': '20vh', 'height': '3vh', 'fontSize': '12px'})
            ], style={'width': '60vh', 'height': '4vh'}),
            html.Div([graph_obj], style={'width': chart_width})
        ], style={'display': 'inline-block'})
        return heatmap_layout

    def update(self):
        heatmap_layouts1 = []
        heatmap_layouts2 = []
        for i in list(range(1, self.heatmaps_number + 1)):
            heatmap = HeatMap(getattr(self, f'keeper{i}'))
            heatmap_layout = self.get_heatmap_layout(i, heatmap)
            if i < 3:
                heatmap_layouts1.append(heatmap_layout)
            else:
                heatmap_layouts2.append(heatmap_layout)

        if self.heatmaps_number < 3:
            self.heatmap_layout_area = html.Div(heatmap_layouts1, style={'textAlign': 'center'})
        else:
            self.heatmap_layout_area = html.Div([html.Div(heatmap_layouts1), html.Div(heatmap_layouts2)])


def correlation_page(tickers, main_folder_path):
    correlation_folder_path = f'{main_folder_path}correlation_data\\'
    indicators = Indicators2()
    periods = [1, 2, 3, 5, 10, 'all']
    keeper1 = CorrHMKeeper(tickers, correlation_folder_path)
    keeper2 = CorrHMKeeper(tickers, correlation_folder_path)
    keeper3 = CorrHMKeeper(tickers, correlation_folder_path)
    keeper4 = CorrHMKeeper(tickers, correlation_folder_path)
    keepers = [keeper1, keeper2, keeper3, keeper4]

    hma = HeatMapArea(tickers, indicators, periods, keepers)

    page_layout = html.Div([
        html.Div([
            dash_obj.navigation_menu(2),
            html.Div([
                html.Div([
                    html.Div(html.Button('Select All Tickers', id='refresh_tickers_button'), style={'width': '15vh', 'display': 'inline-block'}),
                    html.Div(
                        dash_obj.dd_single('dd_correlation_type', 'Select correlation type', ['pearson', 'spearman'], 'spearman'), style={'width': '25vh', 'display': 'inline-block', 'margin-left': '10px'}),
                    html.Div(dash_obj.dd_single('dd_heatmaps_number', 'Select number of displayed heatmaps', [1, 2, 3, 4], 1), style={'width': '25vh', 'display': 'inline-block', 'margin-left': '10px'})
                    ], style={'width': '80vh'})
                ], style={'textAlign': 'right', 'fontSize': '12px'})
            ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        html.Div(dash_obj.dd_indicators('dd_tickers1', 'Select ticker', tickers, None), style={'height': '4vh', 'fontSize': '12px'}),
        html.Div(id='heatmap_layout_area')
       ])

    dash.register_page('CorrelationPage', path='/correlation', layout=page_layout)

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children'),
        Input(component_id='dd_heatmaps_number', component_property='value')
    )
    def selection_number_of_heatmaps(value):
        if value is not None:
            hma.heatmaps_number = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_correlation_type', component_property='value'),
        prevent_initial_call=True
    )
    def selection_correlation_type(value):
        if value is not None:
            hma.keeper1.correlation_type = value
            hma.keeper2.correlation_type = value
            hma.keeper3.correlation_type = value
            hma.keeper4.correlation_type = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_tickers1', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_tickers1(value):
        if value is not None:
            hma.keeper1.tickers = value
            hma.keeper2.tickers = value
            hma.keeper3.tickers = value
            hma.keeper4.tickers = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        [Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
         Output(component_id='dd_tickers1', component_property='value')],
        Input(component_id='refresh_tickers_button', component_property='n_clicks'),
        prevent_initial_call=True
    )
    def refresh_all_tickers(n_clicks):
        if n_clicks is not None:
            print('click')
            hma.keeper1.tickers = tickers
            hma.keeper2.tickers = tickers
            hma.keeper3.tickers = tickers
            hma.keeper4.tickers = tickers
            print(tickers)
            hma.update()
        return hma.heatmap_layout_area, tickers

    # ###---###---###---###--- Indicators dropdowns ---###---###---###---###
    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_indicators1', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_indicators1(value):
        if value is not None:
            hma.keeper1.indicator = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_indicators2', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_indicators2(value):
        if value is not None:
            hma.keeper2.indicator = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_indicators3', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_indicators3(value):
        if value is not None:
            hma.keeper3.indicator = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_indicators4', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_indicators4(value):
        if value is not None:
            hma.keeper4.indicator = value
            hma.update()
        return hma.heatmap_layout_area

    # ###---###---###---###--- Period dropdowns ---###---###---###---###
    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_periods1', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_periods1(value):
        if value is not None:
            hma.keeper1.period = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_periods2', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_periods2(value):
        if value is not None:
            hma.keeper2.period = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_periods3', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_periods3(value):
        if value is not None:
            hma.keeper3.period = value
            hma.update()
        return hma.heatmap_layout_area

    @app.callback(
        Output(component_id='heatmap_layout_area', component_property='children', allow_duplicate=True),
        Input(component_id='dd_periods4', component_property='value'),
        prevent_initial_call=True
    )
    def selection_dd_periods4(value):
        if value is not None:
            hma.keeper4.period = value
            hma.update()
        return hma.heatmap_layout_area