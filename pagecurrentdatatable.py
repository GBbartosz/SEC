import dash
import dash_ag_grid as ag
import pandas as pd
from dash import html
from dash.dependencies import Input, Output

import dashboard_objects as dash_obj

from app import app
from functions import KeeperCurrentStatus


def current_status(main_folder_path):

    def columns_property(column, mydf):

        def column_width(column_name, mydf):
            len_column_name = len(column_name)
            len_column_content = len(str(mydf.loc[0, column_name]))
            if len_column_name >= len_column_content:
                col_width = len_column_name * 6.5 + 50
            else:
                col_width = len_column_content * 6.5 + 50
            return col_width

        if column in ['Stock']:
            res = {'field': column, 'pinned': 'left', 'filter': True}
        else:
            width = column_width(column, mydf)
            res = {'field': column, 'sortable': True, 'width': width}

        return res

    def ag_grid_table(df):
        print([columns_property(c, df) for c in df.columns])
        table = ag.AgGrid(id='current_status_table',
                          rowData=df.to_dict('records'),
                          columnDefs=[columns_property(c, df) for c in df.columns],
                          className='ag-theme-alpine-dark',
                          style={'height': '800px', 'width': '1800px', 'borderRadius': '5px'})
        return table

    current_df = pd.read_csv(f'{main_folder_path}current_data\\current_data.csv').drop(['year', 'quarter'], axis=1)
    initial_columns = list(current_df.columns)
    initial_columns.remove('Stock')
    initial_columns.remove('date')
    initial_columns.remove('end')
    keeper = KeeperCurrentStatus()
    keeper.indicators = initial_columns
    keeper.tickers = current_df['Stock'].to_list()

    layout_current_status_page = html.Div([
        html.Div([html.Div(dash_obj.page_link('MainPageLink', 'Main', '/'), style={'display': 'inline-block', 'textAlign': 'left'}),
                  html.Div(html.Button('Refresh', id='refresh_button'), style={'display': 'inline-block', 'textAlign': 'right'})
                  ], style={'display': 'flex', 'justifyContent': 'space-between', 'height': '4vh', 'margin': '0'}),
        html.Div([html.Div(dash_obj.dd_indicators('dd_indicators', 'Select indicator', initial_columns, None), style={'width': '60%', 'display': 'inline-block'}),
                  html.Div(dash_obj.dd_indicators('dd_tickers', 'Select ticker', current_df['Stock'].to_list(), None), style={'width': '40%', 'display': 'inline-block'})],
                 ),
        html.Div(ag_grid_table(current_df), id='aggrid_table_containter'),
        html.Div(id='reset_output')
    ])

    dash.register_page('CurrentStatus', path='/current_data', layout=layout_current_status_page)

    @app.callback(
        [Output('dd_indicators', 'value'),
         Output('dd_tickers', 'value'),
         Output(component_id='aggrid_table_containter', component_property='children')],
        [Input('refresh_button', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_values(n_clicks):
        nonlocal keeper

        if n_clicks is not None:
            keeper = KeeperCurrentStatus()
            keeper.update_indicators([])
            keeper.tickers = []
            table = ag_grid_table(current_df)
            return keeper.indicators, keeper.tickers, table
        else:
            raise dash.exceptions.PreventUpdate

    @app.callback(
        Output(component_id='aggrid_table_containter', component_property='children', allow_duplicate=True),
        Input(component_id='dd_indicators', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_indicators_filter_table(value):
        if value != keeper.base_columns:
            keeper.update_indicators(list(value))
            filtered_current_df = current_df[current_df['Stock'].isin(keeper.tickers)][keeper.indicators]
        else:
            filtered_current_df = current_df.copy()
            keeper.tickers = current_df['Stock'].to_list()
        table = ag_grid_table(filtered_current_df)
        return table

    @app.callback(
        Output(component_id='aggrid_table_containter', component_property='children', allow_duplicate=True),
        Input(component_id='dd_tickers', component_property='value'),
        prevent_initial_call=True
    )
    def dropdown_tickers_filter_table(value):
        if value:
            keeper.tickers = list(value)
            filtered_current_df = current_df[current_df['Stock'].isin(keeper.tickers)][keeper.indicators]
        else:
            filtered_current_df = current_df.copy()
            keeper.indicators = initial_columns
        table = ag_grid_table(filtered_current_df)
        return table
