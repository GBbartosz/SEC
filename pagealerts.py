import dash
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib
import dashboard_objects as dash_obj
from dash.dependencies import Output, Input
from indicator import Indicators
from app import app


class AlertTable:
    def __init__(self, df, indicators):

        def style_color_df():
            styled_df = self.df.copy()
            for c in df.columns:
                if c in self.indicators.alerts:
                    styled_df[c] = styled_df[c].astype(str)
                    styled_df.loc[:, c] = styled_df[c].apply(lambda y: '#EC91E9' if y == '1.0' else '#8EE1EB')
                elif c == 'Total Score':
                    cmap = plt.cm.cool
                    norm = Normalize(vmin=styled_df['Total Score'].min(), vmax=styled_df['Total Score'].max())
                    normalized_values = norm(styled_df['Total Score'])
                    rgba_colors = [cmap(value) for value in normalized_values]
                    hex_colors = [matplotlib.colors.to_hex(color, keep_alpha=False) for color in rgba_colors]
                    styled_df['Total Score'] = hex_colors
                else:
                    styled_df.loc[:, c] = '#341A96'
            return styled_df

        self.indicators = indicators

        self.df = df
        self.data = [self.df[col].tolist() for col in self.df.columns]

        self.color_df = style_color_df()
        self.color_data = [self.color_df[col].tolist() for col in self.color_df.columns]

        self.fig = go.Figure(go.Table(
            header=dict(values=list(df.columns),
                        fill_color='#341A96',
                        align='center',
                        font=dict(color='white', size=12)),
            cells=dict(values=self.data,
                       fill_color=self.color_data,
                       font=dict(color='white')
                       ),

        ))
        self.fig.update_layout(
            margin=dict(l=50, r=50, t=50, b=50)
            #paper_bgcolor='#211D2D'
        )


def page_alerts(main_folder_path):

    indicators = Indicators()
    df = pd.read_csv(f'{main_folder_path}current_data\\alerts_data.csv', index_col=0)
    tickers = df['Stock'].tolist()
    alerttable = AlertTable(df, indicators)

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(4), style={}),
        html.Div([dash_obj.dd_indicators('dd_tickers', 'Select Tickers', tickers, None)]),
        html.Div([
            dcc.Graph(id='AlertTable', figure=alerttable.fig, style={'height': '800px'})
        ], style={'height': '800px'})
    ])

    dash.register_page('Alerts', path='/alerts', layout=page_layout)

    @app.callback(
        Output(component_id='AlertTable', component_property='figure'),
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_selection_of_ticker(value):
        nonlocal df, alerttable
        if value is not None:
            df = pd.read_csv(f'{main_folder_path}current_data\\alerts_data.csv', index_col=0)
            df = df[df['Stock'].isin(value)]
            alerttable = AlertTable(df, indicators)
        return alerttable.fig
