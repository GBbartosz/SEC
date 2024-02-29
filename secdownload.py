import requests
import numpy as np
import pandas as pd
import datetime


from matplotlib import pyplot as plt

# class with parameters for each indicator
# divide by 10000000


class Indicators:
    def __init__(self):
        self.summarizing_indicators = ['Revenues', 'SalesRevenueNet', 'NetIncomeLoss']
        self.not_summarizing_indicators = []

        self.units_dict = {'Revenues': 'USD',
                           'SalesRevenueNet': 'USD',
                           'NetIncomeLoss': 'USD'}

        self.indicators = self.summarizing_indicators + self.not_summarizing_indicators
        self.valid_indicators = []


class IndicatorType:
    def __init__(self, name):
        self.indicators = Indicators()
        self.name = name

        if self.name in self.indicators.summarizing_indicators:
            self.summarizing = True
        elif self.name in self.indicators.not_summarizing_indicators:
            self.summarizing = False

        self.units = self.indicators.units_dict[self.name]


def print_metric_information(myind_class, myfacts, n):
    if n == 0:
        print(myfacts['facts']['us-gaap'][myind_class.name])


def get_df(myfacts, myind_class, myindicators):

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

    try:
        mydf = pd.DataFrame(myfacts['facts']['us-gaap'][myind_class.name]['units'][myind_class.units])
        myindicators.valid_indicators.append(myind_class.name)
    except KeyError:
        mydf = None
        myyears = None
        return mydf, myyears
    mydf = mydf.rename(columns={'val': myind_class.name})
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
            year_value = mydf.iloc[i][myindclass.name]
            prev_q1 = mydf.iloc[i - 1][myindclass.name]
            prev_q2 = mydf.iloc[i - 2][myindclass.name]
            prev_q3 = mydf.iloc[i - 3][myindclass.name]
            val = year_value - prev_q1 - prev_q2 - prev_q3
        else:
            val = mydf.iloc[i][myindclass.name]

        year = mydf.iloc[i]['year']
        prev_q = mydf.iloc[i - 1]['quarter']
        quarter = f'Q{int(prev_q[-1]) + 1}'

        new_row = [start, end, val, filed, year, quarter]
        mydf.iloc[i, :] = new_row
    return mydf


def download_metrics(ticker, cik, main_folder_path, headers, n):
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    base_columns = ['end', 'filed', 'year', 'quarter']
    indicators = Indicators()
    total_df = None
    for indicator in indicators.indicators:
        ind_class = IndicatorType(indicator)
        df, years = get_df(facts, ind_class, indicators)
        if df is None:  # case when ticker doesn't have this indicator
            continue
        print_metric_information(ind_class, facts, n)
        indexes_to_update = find_indexes_with_full_year_data(df, years)
        df = convert_full_years_data_to_quarter_data(df, indexes_to_update, ind_class)
        df = df.sort_values(by=['end']).dropna().reset_index(drop=True).reindex(columns=base_columns + [ind_class.name])

        if total_df is None:
            total_df = df
        else:
            total_df = pd.merge(total_df, df, on=['end', 'filed', 'year', 'quarter'])

    print(indicators.valid_indicators)
    total_df[indicators.valid_indicators] = total_df[indicators.valid_indicators] / 1000000

    total_df.to_csv(f'{main_folder_path}metrics\\{ticker}_metrics.csv', index=False)
