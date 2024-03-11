import dash
from dash import dcc


def dd_indicators(obj_id, placeholder, all_indicators, initial_value):
    obj = dcc.Dropdown(id=obj_id,
                       placeholder=placeholder,
                       options=all_indicators,
                       value=initial_value,
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
