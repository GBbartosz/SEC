import requests
import pandas as pd


def pandas_df_display_options():
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 20)
    pd.set_option('display.width', 400)


pandas_df_display_options()


headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
tickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers).json()
tickers_df = pd.DataFrame(tickers).transpose()
tickers_df['cik_str'] = tickers_df['cik_str'].astype(str).str.zfill(10)

for i in tickers_df.index[[0]]:
    cik = tickers_df['cik_str'][i]
    ticker = tickers_df['ticker'][i]
    company_name = tickers_df['title'][i]
    print(cik)
    print(ticker)
    print(company_name)
    #metadata = requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json', headers=headers).json()
    #print(metadata)
    #print()
    #print(metadata.keys())
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    print(facts.keys())
    print(facts['facts']['us-gaap'].keys())
    print(facts['facts']['dei'].keys())
    print()
    print(facts['facts']['us-gaap']['NetIncomeLoss'])
    print(facts['facts']['dei']['EntityCommonStockSharesOutstanding'])
    print(facts['facts']['dei']['EntityListingParValuePerShare'])
    print()
    print(facts['facts']['us-gaap']['NetIncomeLoss'].keys())
    print(facts['facts']['us-gaap']['NetIncomeLoss']['units'])
    print(facts['facts']['us-gaap']['NetIncomeLoss']['units']['USD'])

    timel = facts['facts']['us-gaap']['NetIncomeLoss']['units']['USD']
    for t in timel:
        start = t['start']
        end = t['end']
        val = t['val']
        print(f'{start}-{end}: {val}')