import dash
from dash import dcc, html
import dashboard_objects as dash_obj
import pandas as pd
import datetime
import plotly.graph_objects as go


def check_validity_of_data(main_folder_path):
    current_df = pd.read_csv(f'{main_folder_path}current_data\\current_data.csv')
    current_df = current_df[['Stock', 'end']]
    current_df = current_df.rename(columns={'end': 'last_update'})
    current_df.loc[:, 'today'] = datetime.date.today()
    current_df['today'] = pd.to_datetime(current_df['today'])
    current_df['last_update'] = pd.to_datetime(current_df['last_update'])
    current_df['next_update'] = current_df['last_update'] + pd.DateOffset(months=3)
    current_df['updated'] = current_df.apply(lambda x: 1 if x['today'] < x['next_update'] else 0, axis=1)  # if today is more than 3 months since last metrics data
    current_df['last_update'] = current_df['last_update'].dt.date  # shorten date for display in table (before impossible due to comparison conditions)
    return current_df


def create_update_table(current_df):

    color_df = current_df[['Stock', 'last_update', 'updated']].copy()
    color_df.loc[:, ['Stock', 'last_update']] = 'snow'
    color_df['updated'] = color_df['updated'].astype(str).apply(lambda x: 'lightgreen' if x == '1' else 'pink')

    fig = go.Figure(go.Table(
        header=dict(values=list(['Stock', 'Last Update', 'Updated']),
                    align='center',
                    fill_color='#8763EE',
                    font=dict(color='snow')),
        cells=dict(values=current_df[['Stock', 'last_update', 'updated']].T,
                   fill_color=color_df.T)
    ))
    return fig


def page_update(main_folder_path):

    current_df = check_validity_of_data(main_folder_path)
    updatetable_fig = create_update_table(current_df)

    page_layout = html.Div([
        html.Div(dash_obj.navigation_menu(6)),
        html.Div([
            dcc.Graph(id='UpdateTable', figure=updatetable_fig, style={'width': '450px', 'height': '800px'})
        ])
    ])

    dash.register_page('Update', path='/update', layout=page_layout)

