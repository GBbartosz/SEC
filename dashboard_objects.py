import dash
from dash import dcc


def dd_indicators(all_indicators):
    obj = dcc.Dropdown(id='dd_indicators',
                       options=all_indicators,
                       multi=True)
    return obj


def dd_tickers(all_tickers):
    obj = dcc.Dropdown(id='dd_tickers',
                       options=all_tickers,
                       multi=True)
    return obj


def link_style():
    style = {'height': '3vh',
             'background-color': 'blue',
             'color': 'white',
             'border': '2px',
             'border-radius': '6px'}
    return style


def page_link(obj_id, name, path):
    obj = dash.dcc.Link(dash.html.Button(name, style=link_style()),
                        id=obj_id,
                        href=path,
                        refresh=True)
    return obj
