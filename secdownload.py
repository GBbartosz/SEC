import requests
import numpy as np
import pandas as pd
import datetime

from matplotlib import pyplot as plt

# class with parameters for each indicator
# divide by 10000000


class Indicators:
    def __init__(self):
        self.summarizing_indicators = ['Revenues', 'NetIncomeLoss']
        self.not_summarizing_indicators = ['WeightedAverageNumberOfDilutedSharesOutstanding']

        self.units_dict = {'Revenues': 'USD',
                           'NetIncomeLoss': 'USD',
                           'WeightedAverageNumberOfDilutedSharesOutstanding': 'shares'}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators


class IndicatorType:
    def __init__(self, name):
        self.indicators = Indicators()
        self.name = name

        if self.name in self.indicators.summarizing_indicators:
            self.summarizing = True
        elif self.name in self.indicators.not_summarizing_indicators:
            self.summarizing = False

        self.units = self.indicators.units_dict[self.name]


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


def get_df(myfacts, myind_class):

    def get_quarter(x):
        return x[-2:] if pd.isna(x) is False and 'Q' in x else None

    def eliminate_first_year(mydf2):
        # first year has to be deleted due to lacking quarters
        myyears2 = sorted(mydf2['year'].unique())
        myfirst_year = min(myyears2)
        myyears2 = myyears2[1:]
        mydf2 = mydf2[mydf2['year'] > myfirst_year]
        mydf2 = mydf2.sort_values(by=['end'])
        mydf2 = mydf2.reset_index(drop=True)
        return mydf2, myyears2, myfirst_year

    mydf = pd.DataFrame(myfacts['facts']['us-gaap'][myind_class.name]['units'][myind_class.units])
    mydf = mydf.rename(columns={'val': myind_class.name})
    print(mydf)
    #mydf['start'] = pd.to_datetime(mydf['start'])
    mydf['end'] = pd.to_datetime(mydf['end'])
    mydf = mydf.dropna(subset='frame')  # drop rows with null in frame
    mydf['year'] = mydf['end'].dt.year
    mydf['quarter'] = mydf['frame'].apply(get_quarter)
    mydf = mydf.drop(['accn', 'fy', 'fp', 'form', 'frame'], axis=1)
    mydf, myyears, first_year = eliminate_first_year(mydf)
    return mydf, myyears


def find_indexes_with_full_year_data(mydf, myyears):
    myindexes_to_update = []
    for year in myyears:
        ydf = mydf[mydf['year'] == year]
        if all(q in ydf['quarter'].values for q in ['Q1', 'Q2', 'Q3', 'Q4']) is False:
            try:
                ind = ydf[ydf['quarter'].isna()].index[0]
            except IndexError:  # case when there is lacking quarter and there is not full year statement
                ind = -1
            if ind >= 3:  # nie mozna odjac poprzednich kwartalow
                myindexes_to_update.append(ind)
    return myindexes_to_update


def convert_full_years_data_to_quarter_data(mydf, myindexes_to_update, myindclass):
    for i in myindexes_to_update:
        start = mydf.iloc[i - 1]['end'] + datetime.timedelta(days=1)
        end = mydf.iloc[i]['end']
        filed = mydf.iloc[i]['filed']

        if myindclass.summarizing:
            year_value = mydf.iloc[i][indicator]
            prev_q1 = mydf.iloc[i - 1][indicator]
            prev_q2 = mydf.iloc[i - 2][indicator]
            prev_q3 = mydf.iloc[i - 3][indicator]
            val = year_value - prev_q1 - prev_q2 - prev_q3
        else:
            val = df.iloc[i][indicator]

        year = mydf.iloc[i]['year']
        prev_q = mydf.iloc[i - 1]['quarter']
        quarter = f'Q{int(prev_q[-1]) + 1}'

        new_row = [start, end, val, filed, year, quarter]
        mydf.iloc[i, :] = new_row
    return mydf


pandas_df_display_options()
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
headers = {'User-Agent': 'bartosz.grygalewicz@gmail.com'}
tickers_df = download_tickers_df(headers)
# tickers_df.to_excel(f'{main_folder_path}tickers.xlsx')

tickers_df = tickers_df[tickers_df['ticker'] == 'NVDA']
for i in tickers_df.index[[0]]:
    cik = tickers_df['cik_str'][i]
    ticker = tickers_df['ticker'][i]
    company_name = tickers_df['title'][i]
    print(f'{ticker}: {cik}')
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    print(facts['facts']['us-gaap']['WeightedAverageNumberOfDilutedSharesOutstanding'])
    #base_columns = ['start', 'end', 'filed', 'year', 'quarter']
    base_columns = ['end', 'filed', 'year', 'quarter']
    indicators = Indicators()
    total_df = None
    #for indicator in indicators.indicators:
    for indicator in ['WeightedAverageNumberOfDilutedSharesOutstanding']:
        ind_class = IndicatorType(indicator)
        df, years = get_df(facts, ind_class)
        print(df)
        indexes_to_update = find_indexes_with_full_year_data(df, years)
        df = convert_full_years_data_to_quarter_data(df, indexes_to_update, ind_class)
        df = df.sort_values(by=['end']).dropna().reset_index(drop=True).reindex(columns=base_columns + [ind_class.name])

        if total_df is None:
            total_df = df
        else:
            #total_df = pd.merge(total_df, df, on=['start', 'end', 'filed', 'year', 'quarter'])
            total_df = pd.merge(total_df, df, on=['end', 'filed', 'year', 'quarter'])

    print(total_df.tail(10))
    total_df.to_csv(f'{main_folder_path}metrics\\{ticker}_metrics.csv')


