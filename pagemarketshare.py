import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.io as pio
import dashboard_objects as dash_obj
from matplotlib import colors as mcolors
from app import app


class MarketShareKeeper:
    def __init__(self):
        self.ticker = None
        self.indicator = None
        self.industry_sector = 'industry'


class MarketShareChart:
    def __init__(self, keeper, main_folder_path):
        self.nominal_fig = go.Figure()
        self.pcg_fig = go.Figure()
        self.industry_sector = ''
        if keeper.ticker is not None and keeper.indicator is not None:  # necessary selected values
            self.tickers_df = pd.read_excel(f'{main_folder_path}tickers_data.xlsx')
            self.keeper = keeper

            self.industry_sector = self.tickers_df.query(f'ticker == \'{self.keeper.ticker}\'')[self.keeper.industry_sector].to_list()[0]
            ind_sec_df = self.tickers_df.query(f'{self.keeper.industry_sector} == \'{self.industry_sector}\'')
            tickers_from_industry_sector = ind_sec_df['ticker'].to_list()
            # putting chosen ticker on first position
            tickers_from_industry_sector.remove(self.keeper.ticker)
            tickers_from_industry_sector = [self.keeper.ticker] + tickers_from_industry_sector
            ind_sec_df.index = ind_sec_df['ticker']
            ind_sec_df = ind_sec_df.reindex(tickers_from_industry_sector)  # necessary for keeping colors in order

            # conversion of colors to rgba
            line_colors = [f'rgba{str(tuple([i * 255 for i in mcolors.to_rgba(c)[:-1]] + [1.0]))}' for c in ind_sec_df['color'].to_list()]
            fill_colors = [f'rgba{str(tuple([i * 255 for i in mcolors.to_rgba(c)[:-1]] + [0.5]))}' for c in ind_sec_df['color'].to_list()]

            total_df = pd.DataFrame(columns=['year', 'quarter', self.keeper.indicator])
            nominal_columns = []
            # creating dataframe with all data from industry/sector
            for tic in tickers_from_industry_sector:
                tic_df = pd.read_csv(f'{main_folder_path}processed_data\\{tic}_processed.csv')[['year', 'quarter', self.keeper.indicator]]
                tic_df = tic_df.dropna(how='any', axis=0)
                nominal_column = f'{self.keeper.indicator}_{tic}'
                nominal_columns.append(nominal_column)
                tic_df = tic_df.rename(columns={self.keeper.indicator: nominal_column})
                if total_df.empty:
                    total_df = tic_df.copy()
                else:
                    total_df = total_df.merge(tic_df, how='inner', on=['year', 'quarter'])
            total_df[f'{self.keeper.indicator}_total'] = total_df.sum(axis=1)  # summing values for periods

            # creating percentage market share
            pcg_columns = []
            for c in total_df.columns[2:-1]:  # omitting total column
                pcg_column = f'{c}_pcg'
                pcg_columns.append(pcg_column)
                total_df[pcg_column] = (total_df[c] / total_df[f'{self.keeper.indicator}_total'])

            total_df['date'] = total_df.apply(lambda x: x['year'].astype(int).astype(str) + '-' + x['quarter'].astype(int).astype(str), axis=1).astype(str)

            # nominal chart
            nominal_traces = []
            y = None
            for tic, nc, line_color, fill_color in zip(tickers_from_industry_sector, nominal_columns, line_colors, fill_colors):
                if y is None:
                    y = np.array(total_df[nc].copy())
                else:
                    y += np.array(total_df[nc].copy())
                trace = go.Scatter(x=total_df['date'], y=y, fill='tonexty', text=total_df[nc], name=tic, fillcolor=fill_color, line=dict(color=line_color))
                nominal_traces.append(trace)

            self.nominal_fig = go.Figure(data=nominal_traces)
            self.nominal_fig.update_layout(title='Nominal', xaxis_type='category', template='plotly_dark')
            self.nominal_fig.update_xaxes(range=[-1, len(total_df['date'])])

            # pcg chart
            pcg_traces = []
            y = None
            for tic, pc, line_color, fill_color in zip(tickers_from_industry_sector, pcg_columns, line_colors, fill_colors):
                if y is None:
                    y = np.array(total_df[pc])
                else:
                    y += np.array(total_df[pc])
                trace = go.Scatter(x=total_df['date'],
                                   y=y,
                                   mode='lines+markers',
                                   fill='tonexty',
                                   text=[round(c, 2) for c in total_df[pc]],
                                   name=tic,
                                   fillcolor=fill_color,
                                   line=dict(color=line_color))
                pcg_traces.append(trace)

            self.pcg_fig = go.Figure(data=pcg_traces)
            self.pcg_fig.update_layout(title='Percentage', xaxis_type='category', template='plotly_dark')
            self.pcg_fig.update_xaxes(range=[-1, len(total_df['date'])])


def page_marketshare(tickers, main_folder_path):

    keeper = MarketShareKeeper()

    layout_market_share_page = html.Div([
        dash_obj.navigation_menu(7),
        html.Div([
            html.Div([dash_obj.dd_single('dd_indicators', 'Select indicator', ['Revenue', 'ttm_Revenue'],None)], style={'width': '12%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dash_obj.dd_single('dd_tickers', 'Select stock', tickers, None)], style={'width': '12%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dash_obj.dd_single('dd_industry_sector', 'Select industry or sector', ['industry', 'sector'], 'industry')], style={'width': '12%', 'display': 'inline-block'})
        ], style={'width': '100%', 'height': '6vh'}),
        html.Div(html.H1(id='industry_sector_h1', children=''), style={'text-align': 'center'}),
        html.Div([
            html.Div([dcc.Graph(id='MarketShareNominalChart', style={'width': '80%', 'height': '66vh'})]),
            html.Div([dcc.Graph(id='MarketSharePcgChart', style={'width': '80%', 'height': '66vh'})])
        ], style={'width': '100%', 'marginLeft': '10%'})
    ])

    dash.register_page('MarketSharePage', path='/marketshare', layout=layout_market_share_page)

    @app.callback(
        [Output(component_id='MarketShareNominalChart', component_property='figure'),
         Output(component_id='MarketSharePcgChart', component_property='figure')],
        Input(component_id='dd_indicators', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_indicator(chosen_val):
        keeper.indicator = chosen_val
        market_share_chart = MarketShareChart(keeper, main_folder_path)
        return market_share_chart.nominal_fig, market_share_chart.pcg_fig

    @app.callback(
        [Output(component_id='MarketShareNominalChart', component_property='figure', allow_duplicate=True),
         Output(component_id='MarketSharePcgChart', component_property='figure', allow_duplicate=True),
         Output(component_id='industry_sector_h1', component_property='children', allow_duplicate=True)],
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_ticker(chosen_val):
        keeper.ticker = chosen_val
        market_share_chart = MarketShareChart(keeper, main_folder_path)
        return market_share_chart.nominal_fig, market_share_chart.pcg_fig, market_share_chart.industry_sector

    @app.callback(
        [Output(component_id='MarketShareNominalChart', component_property='figure', allow_duplicate=True),
         Output(component_id='MarketSharePcgChart', component_property='figure', allow_duplicate=True),
         Output(component_id='industry_sector_h1', component_property='children')],
        Input(component_id='dd_industry_sector', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_indicator(chosen_val):
        keeper.industry_sector = chosen_val
        market_share_chart = MarketShareChart(keeper, main_folder_path)
        return market_share_chart.nominal_fig, market_share_chart.pcg_fig, market_share_chart.industry_sector
