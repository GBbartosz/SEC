import pandas as pd
import random
import requests


class TickerType:
    def __init__(self):
        self.name = None
        self.tickers = ['AAPL', 'ADBE', 'AMD', 'AMZN', 'AVGO', 'DIS', 'GOOGL', 'INTC', 'LLY', 'MA', 'MCD', 'META', 'MP', 'MSFT', 'NFLX', 'NKE', 'NVDA', 'PFE', 'QCOM', 'SKX', 'TSLA', 'TXN', 'UA', 'WMT']  # usuniety TSM

        self.us_gaap = ['AAPL', 'ADBE', 'AMD', 'AMZN', 'AVGO', 'DIS', 'GOOGL', 'INTC', 'LLY', 'MA', 'MCD', 'META', 'MP', 'MSFT', 'NFLX', 'NKE', 'NVDA', 'PFE', 'QCOM', 'SKX', 'TSLA', 'TXN', 'UA', 'WMT']  # usuniety TSM

        self.ifrs_full = ['TSM']

        self.currency_usd = ['AAPL', 'ADBE', 'AMD', 'AMZN', 'AVGO', 'DIS', 'GOOGL', 'INTC', 'LLY', 'MA', 'MCD', 'META', 'MP', 'MSFT', 'NFLX', 'NKE', 'NVDA', 'PFE', 'QCOM', 'SKX', 'TSLA', 'TXN', 'UA', 'WMT']  # usuniety TSM
        self.currency_twd = ['TSM']

    def get_facts_key(self):
        if self.name in self.us_gaap:
            mykey = 'us-gaap'
        elif self.name in self.ifrs_full:
            mykey = 'ifrs-full'
        return mykey

    def get_units_key(self):
        if self.name in self.currency_usd:
            mykey = 'USD'
        elif self.name in self.currency_twd:
            mykey = 'TWD'
        return mykey


class Keeper:
    def __init__(self):
        self.tickers = []
        self.indicators = []
        self.indicators2 = []


class KeeperCurrentStatus:
    def __init__(self):
        self.tickers = []
        self.base_columns = ['Stock', 'date', 'end']
        self.indicators = self.base_columns

    def update_indicators(self, new_values):
        self.indicators = self.base_columns + new_values


def pandas_df_display_options():
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 400)


def download_tickers_df(headers):
    mytickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers).json()
    mytickers_df = pd.DataFrame(mytickers).transpose()
    mytickers_df['cik_str'] = mytickers_df['cik_str'].astype(str).str.zfill(10)
    return mytickers_df


plotly_lines = ['solid', 'dash', 'dot', 'dashdot', 'longdash', 'longdashdot']

plotly_markers = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down', 'pentagon']


def color_generator(ticker):

    ticker_color_dict = {'AAPL': '#A2AAAD',
                         'ADBE': '#FF0000',
                         'ALB': '#52B595',
                         'AMZN': '#FF9900',
                         'AVGO': '#CC092F',
                         'COST': '#E32A36',
                         'CRM': '#00A1E0',
                         'GOOGL': '#EA4335',
                         'JNJ': '#D71600',
                         'KO': '#DA1E2C',
                         'LLY': '#D52B1E',
                         'MA': '#FF5F00',
                         'MCD': '#FFCC00',
                         'META': '#0081FB',
                         'MP': '#5C5C9C',
                         'MSFT': '#7EB900',
                         'NFLX': '#B20710',
                         'NVDA': '#76B900',
                         'NVO': '#001965',
                         'PEP': '#28458E',
                         'PYPL': '#009cde',
                         'TSLA': '#E31937',
                         'V': '#1A1F71',
                         'WMT': '#ffc220'}

    if ticker in ticker_color_dict.keys():
        color = ticker_color_dict[ticker]
    else:
        color = f'rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})'
    return color
