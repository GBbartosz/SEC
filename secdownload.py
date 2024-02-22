import requests
import pandas as pd
import datetime

from matplotlib import pyplot as plt


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


def get_quarter(x):
    return x[-2:] if pd.isna(x) is False and 'Q' in x else None


pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'

headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
tickers = requests.get('https://www.sec.gov/files/company_tickers.json', headers=headers).json()
tickers_df = pd.DataFrame(tickers).transpose()
tickers_df['cik_str'] = tickers_df['cik_str'].astype(str).str.zfill(10)
# tickers_df.to_excel(f'{main_folder_path}tickers.xlsx')

tickers_df = tickers_df[tickers_df['ticker'] == 'NVDA']
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
    #print(facts['facts']['dei']['EntityListingParValuePerShare'])
    print()
    print(facts['facts']['us-gaap']['NetIncomeLoss'].keys())
    print(facts['facts']['us-gaap']['NetIncomeLoss']['units'])
    print(facts['facts']['us-gaap']['NetIncomeLoss']['units']['USD'])

    timel = facts['facts']['us-gaap']['NetIncomeLoss']['units']['USD']

    df = pd.DataFrame(timel)

    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])

    df = df.dropna(subset='frame')
    df['year'] = df['end'].dt.year
    df['quarter'] = df['frame'].apply(get_quarter)
    print(df)
    df = df.drop(['accn', 'fy', 'fp', 'form', 'filed', 'frame'], axis=1)

    years = sorted(df['year'].unique())
    first_year = min(years)
    years = years[1:]
    df = df[df['year'] > first_year]
    df = df.sort_values(by=['end'])
    df = df.reset_index(drop=True)

    indexes_to_update = []
    for year in years:
        ydf = df[df['year'] == year]
        if all(q in ydf['quarter'].values for q in ['Q1', 'Q2', 'Q3', 'Q4']) is False:
            ind = ydf[ydf['quarter'].isna()].index[0]
            if ind >= 3:  # nie mozna odjac poprzednich kwartalow
                indexes_to_update.append(ind)

    for i in indexes_to_update:
        start = df.iloc[i - 1]['end'] + datetime.timedelta(days=1)
        end = df.iloc[i]['end']

        year_value = df.iloc[i]['val']
        prev_q1 = df.iloc[i - 1]['val']
        prev_q2 = df.iloc[i - 2]['val']
        prev_q3 = df.iloc[i - 3]['val']
        lacking_quarter_val = year_value - prev_q1 - prev_q2 - prev_q3

        year = df.iloc[i]['year']
        prev_q = df.iloc[i - 1]['quarter']
        quarter = f'Q{int(prev_q[-1]) + 1}'

        new_row = [start, end, lacking_quarter_val, year, quarter]
        df.iloc[i, :] = new_row

    df = df.sort_values(by=['end'])
    df = df.dropna().reset_index(drop=True)
    print(df)

    plt.figure()
    plt.plot(df['end'], df['val'])
    plt.show()

    #for t in timel:
    #    form = t['form']
    #    start = t['start']
    #    end = t['end']
    #    val = t['val']
    #    print(f'{form}: {start}-{end}: {val}')

        # 44161000000