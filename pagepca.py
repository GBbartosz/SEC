import dash

from dash import dcc, html
from dash.dependencies import Input, Output

import dashboard_objects as dash_obj





def page_pca(indicators, tickers, main_folder_path):

    layout = html.Div([
        dash_obj.navigation_menu(3),
        html.Div([])
    ])

    dash.register_page('PCAPage', path='/pca', layout=layout)







