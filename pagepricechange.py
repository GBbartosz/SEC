from app import app
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dashboard_objects as dash_obj
import pandas as pd
import datetime as dt
import plotly.graph_objects as go


class Keeper:
    def __init__(self):
        self.main_folder_path = None
        self.selected_tickers = []
        self.df = None
        self.filtered_data = None
        self.tickers_df = None
        self.all_tickers_df = None


def page_pricechange(tickers_df, main_folder_path):
    keeper = Keeper()
    keeper.main_folder_path = main_folder_path
    keeper.tickers_df = tickers_df

    all_tickers_df = None
    for tic in keeper.tickers_df['ticker']:
        ticdf = pd.read_csv(f'{main_folder_path}\\processed_data\\{tic}_processed.csv')[['date', 'close']]
        ticdf = ticdf.rename(columns={'close': tic})
        all_tickers_df = ticdf if all_tickers_df is None else all_tickers_df.merge(ticdf, on='date', how='inner')
    all_tickers_df = all_tickers_df.set_index('date')
    keeper.all_tickers_df = all_tickers_df

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(9)),
        html.Div(dcc.Dropdown(
            id='ticker_dropdown',
            placeholder='Select stocks',
            options=tickers_df['ticker'].values,
            value=None,
            multi=True
        )),
        html.Div(dcc.RangeSlider(id='date_range_slider', step=1)),
        html.Div([dcc.Graph(id='PriceChart', style={'width': '100%', 'height': '88vh'})]),
        html.Div([html.Div(dcc.Graph(id='MinHeatmapChart', style={'height': '220vh'}), style={'width': '30%', 'display': 'inline-block'}),
                  html.Div(dcc.Graph(id='MaxHeatmapChart', style={'height': '220vh'}), style={'width': '30%', 'display': 'inline-block'}),
                  html.Div(dcc.Graph(id='EndHeatmapChart', style={'height': '220vh'}), style={'width': '30%', 'display': 'inline-block'})],
                 style={'width': '60%'})
    ])

    dash.register_page('Price Change', path='/pricechange', layout=page_layout)

    @app.callback(
        [Output('date_range_slider', 'min'),
         Output('date_range_slider', 'max'),
         Output('date_range_slider', 'marks'),
         Output('PriceChart', 'figure'),
         Output('MinHeatmapChart', 'figure'),
         Output('MaxHeatmapChart', 'figure'),
         Output('EndHeatmapChart', 'figure')],
        Input('ticker_dropdown', 'value'),
        prevent_initial_call=True
    )
    def update_tickers(selected_tickers):
        slider_min = 0
        if not selected_tickers:
            slider_max = 1,
            marks = {}
            fig = go.Figure()
            return slider_min, slider_max, marks, fig

        keeper.selected_tickers = selected_tickers
        df = None
        for tic in selected_tickers:
            ticdf = pd.read_csv(f'{main_folder_path}\\processed_data\\{tic}_processed.csv')[['date', 'close']]
            ticdf = ticdf.rename(columns={'close': tic})
            df = ticdf if df is None else df.merge(ticdf, on='date', how='inner')
        df = df.set_index('date')
        keeper.df = df
        keeper.filtered_data = df

        slider_max = len(df.index)
        marks = {i: df.index[i] for i in range(0, len(df), len(df) // 20)}
        fig = price_chart()
        min_hfig, max_hfig, end_hfig = heatmap_chart()

        return slider_min, slider_max, marks, fig, min_hfig, max_hfig, end_hfig

    @app.callback(
        [Output('PriceChart', 'figure', allow_duplicate=True),
         Output('MinHeatmapChart', 'figure', allow_duplicate=True),
         Output('MaxHeatmapChart', 'figure', allow_duplicate=True),
         Output('EndHeatmapChart', 'figure', allow_duplicate=True)],
        Input('date_range_slider', 'value'),
        prevent_initial_call=True
    )
    def update_slider(date_range):
        if not keeper.selected_tickers:
            fig = go.Figure()
            return fig

        if not date_range:
            fig = price_chart()
            return fig

        start_index, end_index = date_range
        filtered_data = keeper.df.iloc[start_index:end_index + 1]
        keeper.filtered_data = filtered_data
        fig = price_chart()
        min_hfig, max_hfig, end_hfig = heatmap_chart()

        return fig, min_hfig, max_hfig, end_hfig

    def price_chart():
        fig = go.Figure()

        for ticker in keeper.selected_tickers:
            base_price = keeper.filtered_data[ticker].iloc[0]
            percentage_change = (((keeper.filtered_data[ticker] - base_price) / base_price) * 100).round(1)
            color = keeper.tickers_df.query(f'ticker == "{ticker}"')['color'].values[0]

            fig.add_trace(go.Scatter(x=keeper.filtered_data.index,
                                     y=percentage_change,
                                     mode='lines',
                                     name=ticker,
                                     line={'color': color}))

        fig.update_layout(
            title='Percentage Change in Stock Price',
            xaxis_title='Date',
            yaxis_title='Percentage Change (%)',
            hovermode='x unified')

        fig.update_xaxes(range=[pd.to_datetime(keeper.filtered_data.index.min()) - dt.timedelta(days=20),
                                pd.to_datetime(keeper.filtered_data.index.max()) + dt.timedelta(days=20)])

        return fig

    def heatmap_chart():
        all_tickers_df = keeper.all_tickers_df
        filtered_data = keeper.filtered_data
        df = all_tickers_df[
            (all_tickers_df.index >= filtered_data.index.min()) & (all_tickers_df.index <= filtered_data.index.max())]
        start_df = df.iloc[0]
        min_df = ((df.min() / start_df - 1) * 100).to_frame().round(1)
        max_df = ((df.max() / start_df - 1) * 100).to_frame().round(1)
        end_df = ((df.iloc[-1] / start_df - 1) * 100).to_frame().round(1)

        min_hfig = go.Figure(go.Heatmap(z=min_df,
                                        x=['Max Drop'],
                                        y=min_df.index,
                                        colorscale='Reds',
                                        reversescale=True))

        max_hfig = go.Figure(go.Heatmap(z=max_df,
                                        x=['Max Gain'],
                                        y=max_df.index,
                                        colorscale='Greens'))

        end_hfig = go.Figure(go.Heatmap(z=end_df,
                                        x=['Final Change'],
                                        y=end_df.index,
                                        colorscale='RdBu',
                                        zmid=0))

        return min_hfig, max_hfig, end_hfig
