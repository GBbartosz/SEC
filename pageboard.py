from app import app
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dashboard_objects as dash_obj
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# filtering filters based on keeper.period_type (html.Div)
# calculating price change for range
# leaving only rows for quarters for period_type quarter
# setting cmin cmax for chart

class Keeper:
    def __init__(self, tickers_df, concated_df, cam_features):

        self.tickers_df = tickers_df

        self.df = concated_df
        self.qdf = self.df.dropna(subset='year').reset_index(drop=True)
        self.qdf['yearQ'] = (self.qdf['year'].astype(int).astype(str) + ' Q' + self.qdf['quarter'].astype(int).astype(str))
        self.quarters = sorted(self.qdf['yearQ'].unique(), reverse=True)

        self.min_date_allowed = self.df['date'].min()
        self.max_date_allowed = self.df['date'].max()
        self.selected_period = self.max_date_allowed  # period for period_type in ['date', 'quarter']
        self.selected_start_date = self.min_date_allowed  # start date for range
        self.selected_end_date = self.max_date_allowed  # end date for range

        self.cam_features = cam_features
        self.period_type = 'date'
        self.features = []
        self.period_filters_div = None
        self.update_period_filters_and_features()
        self.selected_feature = 'PriceChangeDaily'

        self.filtered_df = None
        self.update_df()

    def update_period_filters_and_features(self):
        if self.period_type == 'date':
            self.selected_period = self.max_date_allowed
            self.period_filters_div = html.Div(dcc.DatePickerSingle(id='date_picker',
                                                                    min_date_allowed=self.min_date_allowed,
                                                                    max_date_allowed=self.max_date_allowed,
                                                                    initial_visible_month=self.max_date_allowed,
                                                                    date=self.max_date_allowed))
            self.features = self.cam_features.concated.board.date_features
        elif self.period_type == 'range':
            self.selected_start_date = self.min_date_allowed  # start date for range
            self.selected_end_date = self.max_date_allowed  # end date for range

            # first trading day
            year = self.max_date_allowed[:4]
            first_trading_day = pd.Timestamp(f'{year}-01-02')
            while first_trading_day.weekday() > 4:  # 5=Saturday, 6=Sunday
                first_trading_day += timedelta(days=1)
            first_trading_day = first_trading_day.strftime('%Y-%m-%d')

            self.period_filters_div = html.Div([
                                                html.Div([
                                                          html.Label('Start Date'),
                                                          dcc.DatePickerSingle(id='start_date_picker',
                                                                               min_date_allowed=self.min_date_allowed,
                                                                               max_date_allowed=self.max_date_allowed,
                                                                               initial_visible_month=self.max_date_allowed,
                                                                               date=first_trading_day)
                                                ]),
                                                html.Div([
                                                          html.Label('End Date'),
                                                          dcc.DatePickerSingle(id='end_date_picker',
                                                                               min_date_allowed=self.min_date_allowed,
                                                                               max_date_allowed=self.max_date_allowed,
                                                                               initial_visible_month=self.max_date_allowed,
                                                                               date=self.selected_end_date)
                                                          ])
                                            ])
            self.features = self.cam_features.concated.board.range_features

        elif self.period_type == 'quarter':
            self.selected_period = self.quarters[0]
            self.period_filters_div = html.Div(dash_obj.dd_single('quarter_picker', 'Select quarter', self.quarters, self.selected_period))
            self.features = self.cam_features.concated.board.quarter_features

        self.selected_feature = self.features[0]  # default first feature from the available features list

    def update_df(self):
        if self.period_type == 'date':
            self.filtered_df = self.df[self.df['date'] == self.selected_period][['ticker', 'sector', self.selected_feature]].copy()
        elif self.period_type == 'range':
            df0 = self.df[self.df['date'] == self.selected_start_date][['ticker', 'sector', self.selected_feature]].reset_index(drop=True).rename(columns={self.selected_feature: 'start'})
            df1 = self.df[self.df['date'] == self.selected_end_date][['ticker', 'sector', self.selected_feature]].reset_index(drop=True).rename(columns={self.selected_feature: 'end'})
            self.filtered_df = df0.merge(df1, on=['ticker', 'sector'], how='inner')
            self.filtered_df[self.selected_feature] = (self.filtered_df['end'] / self.filtered_df['start'] - 1).round(3)
        elif self.period_type == 'quarter':
            self.filtered_df = self.qdf[self.qdf['yearQ'] == self.selected_period][['ticker', 'sector', self.selected_feature]].copy()


def page_board(tickers_df, concated_df, cam_features):

    def make_tree_chart():

        mydf = keeper.filtered_df.copy()
        print(f'mydf: {len(mydf.index)}')

        # Create top-level sector nodes
        sectors = mydf['sector'].unique()
        sector_rows = pd.DataFrame({
            'id': sectors,
            'labels': sectors,
            'parents': [''] * len(sectors)#,
#            'values': [None] * len(sectors)  # Optional if children sum up
        })

        # Create stock nodes
        stock_rows = pd.DataFrame({
            'id': mydf['ticker'],
            'labels': mydf['ticker'],
            'parents': mydf['sector'],
            'values': mydf[keeper.selected_feature]
        })

        # Combine both
        tree_data = pd.concat([sector_rows, stock_rows], ignore_index=True).fillna(0)
        tree_data['abs_values'] = tree_data['values'].abs()
        tree_data['color'] = tree_data['values']
        print(f'tree data: {len(tree_data.index)}')

        # color management
        if keeper.selected_feature in ['PriceChangeDaily']:
            marker = dict(colors=tree_data['color'],
                          colorscale=[[0.0, 'red'],
                                      [0.5, 'white'],
                                      [1.0, 'springgreen']],
                          cmin=-0.05,
                          cmax=0.05)
            tree_data['values'] = (tree_data['values'] * 100).round(1)
            unit = '%'

        elif keeper.selected_feature in ['ttm_Revenue']:
            marker = dict(colors=tree_data['color'],
                          colorscale=[[0.0, 'white'],
                                      [1.0, 'springgreen']])
            unit = 'mln'

        elif keeper.selected_feature in ['ttm_NetIncome', 'close']:
            vmin = tree_data['color'].min()
            vmax = tree_data['color'].max()
            norm = lambda x: (x - vmin) / (vmax - vmin)
            tree_data['color_norm'] = tree_data['color'].apply(norm)
            zero_position = norm(0)
            marker = dict(colors=tree_data['color_norm'],  # normalized colors
                          colorscale=[[0.0, 'red'],
                                      [zero_position, 'white'],
                                      [1.0, 'springgreen']],
                          cmin=0,
                          cmax=1)
            if keeper.selected_feature in ['ttm_NetIncome']:
                unit = 'mln'
            elif keeper.selected_feature in ['close']:
                tree_data['values'] = (tree_data['values'] * 100).round(1)
                unit = '%'

        #elif keeper.selected_feature in ['close']:
        #    marker = dict(colors=tree_data['color'],
        #                  colorscale=[[0.0, 'red'],
        #                              [0.5, 'white'],
        #                              [1.0, 'springgreen']])
        #    tree_data['values'] = (tree_data['values'] * 100).round(1)
        #    unit = '%'

        fig = go.Figure(go.Treemap(labels=tree_data['labels'],
                                   parents=tree_data['parents'],
                                   values=tree_data['abs_values'],
                                   customdata=tree_data['values'],
                                   hovertemplate='<b>%{label}<b><br>%{customdata}<extra></extra>' + unit,
                                   marker=marker
                                   ))

        return fig

    print(len(concated_df['ticker'].unique()))
    keeper = Keeper(tickers_df, concated_df, cam_features)
    fig = make_tree_chart()

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(10)),
        html.Div([
            html.Div(dash_obj.dd_single('dd_period_type', 'Select period type', ['date', 'range', 'quarter'], keeper.period_type)),
            #html.Div([dash_obj.dd_indicators('dd_periods', 'Select period', keeper.features, keeper.selected_period)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div(id='period_filters', children=[keeper.period_filters_div], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dash_obj.dd_single('dd_features', 'Select feature', keeper.features, keeper.selected_feature)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'})
        ]),
        html.Div([dcc.Graph(id='TreeChart', figure=fig, style={'width': '100%', 'height': '100vh'})])
    ])

    dash.register_page('Board', path='/board', layout=page_layout)

    @app.callback(
        Output(component_id='period_filters', component_property='children'),
        Output(component_id='dd_features', component_property='options'),
        Output(component_id='dd_features', component_property='value', allow_duplicate=True),
        Output(component_id='TreeChart', component_property='figure'),
        Input(component_id='dd_period_type', component_property='value'),
        prevent_initial_call=True
    )
    def period_type_selection(chosen_val):
        keeper.period_type = chosen_val
        keeper.update_period_filters_and_features()
        keeper.update_df()
        fig = make_tree_chart()
        return keeper.period_filters_div, keeper.features, keeper.selected_feature, fig

    @app.callback(
        Output(component_id='TreeChart', component_property='figure', allow_duplicate=True),
        Input(component_id='date_picker', component_property='date'),
        prevent_initial_call=True
    )
    def date_selection(chosen_val):
        keeper.selected_period = chosen_val
        keeper.update_df()
        fig = make_tree_chart()
        return fig

    @app.callback(
        Output(component_id='TreeChart', component_property='figure', allow_duplicate=True),
        Input(component_id='start_date_picker', component_property='date'),
        Input(component_id='end_date_picker', component_property='date'),
        prevent_initial_call=True
    )
    def start_end_date_selection(chosen_start, chosen_end):
        keeper.selected_start_date = chosen_start
        keeper.selected_end_date = chosen_end
        keeper.update_df()
        fig = make_tree_chart()
        return fig

    @app.callback(
        Output(component_id='TreeChart', component_property='figure', allow_duplicate=True),
        Input(component_id='quarter_picker', component_property='value'),
        prevent_initial_call=True
    )
    def quarter_selection(chosen_val):
        keeper.selected_period = chosen_val
        keeper.update_df()
        fig = make_tree_chart()
        return fig

    @app.callback(
        Output(component_id='TreeChart', component_property='figure', allow_duplicate=True),
        Input(component_id='dd_features', component_property='value'),
        prevent_initial_call=True
    )
    def feature_selection(chosen_val):
        keeper.selected_feature = chosen_val
        keeper.update_df()
        fig = make_tree_chart()
        return fig
