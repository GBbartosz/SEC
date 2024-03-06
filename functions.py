import requests
import pandas as pd


def download_tickers_df(headers):
    mytickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers).json()
    mytickers_df = pd.DataFrame(mytickers).transpose()
    mytickers_df['cik_str'] = mytickers_df['cik_str'].astype(str).str.zfill(10)
    return mytickers_df


plotly_markers = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 'triangle-down', 'pentagon']

ticker_color_dict = {'AAPL': 'green',
                     'AMZN': '#FF9900',
                     'GOOGL': '#EA4335',
                     'META': '#0668E1',
                     'NVDA': '#76B900',
                     'TSLA': '#E82127'}
