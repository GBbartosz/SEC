import requests
import pandas as pd


def download_tickers_df(headers):
    mytickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers).json()
    mytickers_df = pd.DataFrame(mytickers).transpose()
    mytickers_df['cik_str'] = mytickers_df['cik_str'].astype(str).str.zfill(10)
    return mytickers_df
