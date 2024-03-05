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

