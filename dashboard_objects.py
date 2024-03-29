import dash
from dash import html, dcc


def dd_indicators(obj_id, placeholder, all_indicators, initial_value):
    obj = dcc.Dropdown(id=obj_id,
                       placeholder=placeholder,
                       options=all_indicators,
                       value=initial_value,
                       multi=True)
    return obj


def dd_single(obj_id, placeholder, all_values, initial_value=None):
    obj = dcc.Dropdown(id=obj_id,
                       placeholder=placeholder,
                       options=all_values,
                       value=initial_value,
                       multi=False,
                       style={'height': '3vh'})
    return obj


def link_style(disabled):
    bg_color = 'black' if disabled else '#8763EE'
    style = {'minWidth': '10vh',
             'height': '3vh',
             'background-color': bg_color,
             'color': 'white',
             'border': '2px',
             'border-radius': '6px',
             'alignItems': 'center'}
    return style


def page_link(obj_id, name, path, disabled=False):
    obj = dash.dcc.Link(dash.html.Button(name,
                                         style=link_style(disabled),
                                         disabled=disabled),
                        id=obj_id,
                        href=path,
                        refresh=True)
    return obj


def navigation_menu(disabled_position):
    clicable_elements = [False for e in list(range(6))]
    clicable_elements[disabled_position] = True
    page_link_html_style = {'display': 'inline-block', 'marginLeft': '10px'}
    nm = html.Div([
        html.Div(page_link('MainPageLink', 'Main', '/', disabled=clicable_elements[0]), style=page_link_html_style),
        html.Div(page_link('CurrentDataLink', 'Current Data Table', '/current_data', disabled=clicable_elements[1]), style=page_link_html_style),
        html.Div(page_link('CorrelationLink', 'Correlation', '/correlation', disabled=clicable_elements[2]), style=page_link_html_style),
        html.Div(page_link('PCALink', 'PCA', '/pca', disabled=clicable_elements[3]), style=page_link_html_style),
        html.Div(page_link('AlertsLink', 'Alerts', '/alerts', disabled=clicable_elements[4]), style=page_link_html_style),
        html.Div(page_link('ValuationLink', 'Valuation', '/valuation', disabled=clicable_elements[5]), style=page_link_html_style)
        ], style={'height': '4vh', 'display': 'inline-block', 'textAlign': 'left', 'alignItems': 'center'})
    return nm
