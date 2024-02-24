import requests
import numpy as np
import pandas as pd
import datetime

from matplotlib import pyplot as plt

# class with parameters for each indicator
# divide by 10000000


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
    print(ticker)
    #metadata = requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json', headers=headers).json()
    #print(metadata)
    #print()
    #print(metadata.keys())
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    #print(facts.keys())
    #print(facts['facts']['us-gaap'].keys())
    #print(facts['facts']['dei'].keys())
    #print()
    #print(facts['facts']['us-gaap']['NetIncomeLoss'])
    #print(facts['facts']['dei']['EntityCommonStockSharesOutstanding'])
    #print(facts['facts']['dei']['EntityListingParValuePerShare'])
    #print()
    print(facts['facts']['us-gaap']['CommonStockSharesOutstanding'])
    #not_summarizing_indicators = []
    summarizing_indicators = ['Revenues', 'NetIncomeLoss']
    #indicators = not_summarizing_indicators + summarizing_indicators
    indicators = summarizing_indicators
    base_columns = ['start', 'end', 'filed', 'year', 'quarter']
    total_df = None
    for indicator in indicators:
        df = pd.DataFrame(facts['facts']['us-gaap'][indicator]['units']['USD'])
        df = df.rename(columns={'val': indicator})
        #inddf.to_excel(f'{main_folder_path}_ind_tst_{indicator}.xlsx')


        print(df.sort_values(by='end').tail(1000))
        df['start'] = pd.to_datetime(df['start'])
        df['end'] = pd.to_datetime(df['end'])

        df = df.dropna(subset='frame')
        df['year'] = df['end'].dt.year
        df['quarter'] = df['frame'].apply(get_quarter)
        df = df.drop(['accn', 'fy', 'fp', 'form', 'frame'], axis=1)

        years = sorted(df['year'].unique())
        first_year = min(years)
        years = years[1:]
        df = df[df['year'] > first_year]
        df = df.sort_values(by=['end'])
        df = df.reset_index(drop=True)
        print(df)
        indexes_to_update = []
        for year in years:
            ydf = df[df['year'] == year]
            if all(q in ydf['quarter'].values for q in ['Q1', 'Q2', 'Q3', 'Q4']) is False:
                try:
                    ind = ydf[ydf['quarter'].isna()].index[0]
                except IndexError:  # case when there is lacking quarter and there is not full year statement
                    ind = -1
                if ind >= 3:  # nie mozna odjac poprzednich kwartalow
                    indexes_to_update.append(ind)

        for i in indexes_to_update:
            start = df.iloc[i - 1]['end'] + datetime.timedelta(days=1)
            end = df.iloc[i]['end']
            filed = df.iloc[i]['filed']
            #not_summarizing_vals = [df.iloc[i][first_not_summarizing_indicator_column:last_not_summarizing_indicator_column][0]]   # zmienic po dodaniu kolejnych wskaznikow do not summarizing
            #not_summarizing_vals = list(df.iloc[i][first_not_summarizing_indicator_column:last_not_summarizing_indicator_column])

            year_value = np.array(df.iloc[i][indicator])
            prev_q1 = np.array(df.iloc[i - 1][indicator])
            prev_q2 = np.array(df.iloc[i - 2][indicator])
            prev_q3 = np.array(df.iloc[i - 3][indicator])

            #year_value = df.iloc[i]['val']
            #prev_q1 = df.iloc[i - 1]['val']
            #prev_q2 = df.iloc[i - 2]['val']
            #prev_q3 = df.iloc[i - 3]['val']
            lacking_quarter_val = year_value - prev_q1 - prev_q2 - prev_q3

            year = df.iloc[i]['year']
            prev_q = df.iloc[i - 1]['quarter']
            quarter = f'Q{int(prev_q[-1]) + 1}'

            #new_row = [start, end, filed, year, quarter] + not_summarizing_vals + lacking_quarter_val
            new_row = [start, end, lacking_quarter_val, filed, year, quarter]
            print('xxx')
            print(df.head())
            df.iloc[i, :] = new_row

        df = df.sort_values(by=['end'])
        df = df.dropna().reset_index(drop=True)
        df = df.reindex(columns=base_columns + [indicator])
        print(df.tail(5))

        if total_df is None:

            total_df = df
        else:
            total_df = pd.merge(total_df, df, on=['start', 'end', 'filed', 'year', 'quarter'])

    print(total_df.tail(10))
    total_df.to_csv(f'{main_folder_path}metrics\\{ticker}_metrics.csv')

    plt.figure()
    plt.plot(total_df['end'], total_df[indicators[0]])
    plt.title(indicators[0])
    plt.show()

    plt.figure()
    plt.plot(total_df['end'], total_df[indicators[1]])
    plt.title(indicators[1])
    plt.show()

    #for t in timel:
    #    form = t['form']
    #    start = t['start']
    #    end = t['end']
    #    val = t['val']
    #    print(f'{form}: {start}-{end}: {val}')

        # 44161000000