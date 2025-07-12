from app import app
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dashboard_objects as dash_obj
import pandas as pd
import plotly.graph_objects as go

# filtering filters based on keeper.period_type (html.Div)
# calculating price change for range
# leaving only rows for quarters for period_type quarter
# setting cmin cmax for chart

class Keeper:
    def __init__(self, tickers_df, concated_df, cam_features):

        self.tickers_df = tickers_df

        self.cam_features = cam_features
        self.period_type = 'date'
        self.features = []
        self.update_features()
        self.selected_feature = 'PriceChangeDaily'

        self.df = concated_df
        self.df['yearQ'] = self.df['year'].astype(str) + self.df['quarter'].astype(str)

        self.min_date_allowed = self.df['date'].min()
        self.max_date_allowed = self.df['date'].max()
        self.selected_period = self.max_date_allowed

        self.filtered_df = None
        self.update_df()

    def update_features(self):
        if self.period_type == 'date':
            self.features = self.cam_features.concated.board.date_features
        elif self.period_type == 'range':
            self.features = self.cam_features.concated.board.range_features
        elif self.period_type == 'quarter':
            self.features = self.cam_features.concated.board.quarter_features

    def update_df(self):
        period_col = 'yearQ' if self.period_type == 'quarter' else 'date'
        self.filtered_df = self.df[self.df[period_col] == self.selected_period][['ticker', 'sector', self.selected_feature]].copy()


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
        #print(tree_data.head(20))
        print(f'tree data: {len(tree_data.index)}')

        fig = go.Figure(go.Treemap(labels=tree_data['labels'],
                                   parents=tree_data['parents'],
                                   values=tree_data['abs_values'],
                                   customdata=round(tree_data['values'] * 100, 1),
                                   hovertemplate='<b>%{label}<b><br>%{customdata}%<extra></extra>',
                                   marker=dict(colors=tree_data['color'],
                                               colorscale=[[0.0, 'red'],
                                                           [0.5, 'white'],
                                                           [1.0, 'springgreen']],
                                               cmin=-0.05,
                                               cmax=0.05)
                                   ))

        return fig

    print(len(concated_df['ticker'].unique()))
    keeper = Keeper(tickers_df, concated_df, cam_features)
    fig = make_tree_chart()

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(10)),
        html.Div([
            #html.Div([dash_obj.dd_indicators('dd_periods', 'Select period', keeper.features, keeper.selected_period)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dcc.DatePickerSingle(id='dd_dates',
                                                   min_date_allowed=keeper.min_date_allowed,
                                                   max_date_allowed=keeper.max_date_allowed,
                                                   initial_visible_month=keeper.max_date_allowed,
                                                   date=keeper.max_date_allowed)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'}),
            html.Div([dash_obj.dd_indicators('dd_features', 'Select feature', keeper.features, keeper.selected_feature)], style={'width': '34%', 'display': 'inline-block', 'marginRight': '0.5%'})
        ]),
        html.Div([dcc.Graph(id='TreeChart', figure=fig, style={'width': '100%', 'height': '100vh'})])
    ])

    dash.register_page('Board', path='/board', layout=page_layout)

    @app.callback(
        Output(component_id='TreeChart', component_property='figure'),
        Input(component_id='dd_dates', component_property='date'),
        prevent_initial_call=True
    )
    def date_selection(chosen_val):
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
