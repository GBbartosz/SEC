import requests
import pandas as pd


class TickerType:
    def __init__(self):
        self.name = None
        self.tickers = ['AAPL', 'ADBE', 'AMD', 'AMZN', 'AVGO', 'BABA', 'BIDU', 'COST', 'DIS', 'GOOGL', 'INTC', 'LLY', 'MA', 'MCD', 'META', 'MSFT', 'NFLX', 'NKE', 'NVDA', 'PFE', 'QCOM', 'TSLA', 'TXN', 'V', 'WMT']  # usuniety TSM

        self.us_gaap = ['AAPL', 'ADBE', 'AMD', 'AMZN', 'AVGO', 'BABA', 'BIDU', 'COST', 'DIS', 'GOOGL', 'INTC', 'LLY', 'MA', 'MCD', 'META', 'MSFT', 'NFLX', 'NKE', 'NVDA', 'PFE', 'QCOM', 'TSLA', 'TXN', 'V', 'WMT']  # usuniety TSM

        self.ifrs_full = ['TSM']

        self.currency_usd = ['AAPL', 'ADBE', 'AMD', 'AMZN', 'AVGO', 'BABA', 'BIDU', 'COST', 'DIS', 'GOOGL', 'INTC', 'LLY', 'MA', 'MCD', 'META', 'MSFT', 'NFLX', 'NKE', 'NVDA', 'PFE', 'QCOM', 'TSLA', 'TXN', 'V', 'WMT']  # usuniety TSM
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

ticker_color_dict = {'AAPL': 'green',
                     'ADBE': '#FA0C00',
                     'AMZN': '#FF9900',
                     'GOOGL': '#EA4335',
                     'META': '#0668E1',
                     'MSFT': ' #66CC33',
                     'NFLX': '#D81F26',
                     'NVDA': '#76B900',
                     'TSLA': '#E82127',
                     'TSM': '#bb8f8f',
                     'TXN': '#de538a'}
