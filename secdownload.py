import requests
import numpy as np
import pandas as pd
import datetime

from indicator import Indicators
from functions import TickerType

from matplotlib import pyplot as plt


class IndicatorType:
    def __init__(self, name, currency):
        self.indicators = Indicators(currency)
        self.name = name

        if self.name in self.indicators.summarizing_indicators:
            self.summarizing = True
        elif self.name in self.indicators.not_summarizing_indicators:
            self.summarizing = False

        self.units = self.indicators.units_dict[self.name]


def print_metric_information(myind_class, myfacts, n):
    if n == 0:
        print(myfacts['facts']['us-gaap'][myind_class.name])


def get_df(myfacts, myind_class, myindicators, tict):

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

    #print(myind_class.units)
    #print(tict.get_facts_key())
    #print(myind_class.name)
    #print(myfacts['facts'][tict.get_facts_key()].keys())
    try:
        mydf = pd.DataFrame(myfacts['facts'][tict.get_facts_key()][myind_class.name]['units'][myind_class.units])
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
    #print(mydf)
    mydf = mydf.drop(['accn', 'fy', 'fp', 'form', 'frame'], axis=1)
    mydf, myyears, first_year = eliminate_first_year(mydf)
    return mydf, myyears


def find_indexes_with_full_year_data(mydf, myyears):

    def count_distinct_previous_quarters():
        previous_quarters = mydf['quarter'].iloc[ind-3:ind].tolist()  # znajduje 3 poprzednie kwartaly wedlug indeksu w tablicy
        previous_quarters_without_none = list(filter(None, previous_quarters))
        count_of_distinct_quarters = len(set(previous_quarters_without_none))  # liczy czy sa rozne (jesli któregoś brakuje i przejdzie do poprzedniego roku rozliczeniowego, index nie zostanie dodany
        return count_of_distinct_quarters

    myindexes_to_update = []
    for year in myyears:
        ydf = mydf[mydf['year'] == year]
        if all(q in ydf['quarter'].values for q in ['Q1', 'Q2', 'Q3', 'Q4']) is False:
            try:
                ind = ydf[ydf['quarter'].isna()].index[0]
            except IndexError:  # case when there is lacking quarter and there is not full year statement
                ind = -1
            count_of_distinct_quarters = count_distinct_previous_quarters()
            if ind >= 3 and count_of_distinct_quarters > 2:  # wymagane min 3 kwartaly aby moc od calego roku odjac 3 poprzednie kwartaly; wymagae 3 rozne poprzednie kwartaly aby odjac poprawne okresy od pelnego roku
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


def download_metrics(tict, ticker, cik, main_folder_path, headers, n):

    tict.name = ticker
    currency_key = tict.get_units_key()
    facts = requests.get(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json', headers=headers).json()
    base_columns = ['end', 'year', 'quarter']
    indicators = Indicators()
    total_df = None
    for indicator in indicators.indicators:
    #for indicator in [indicators.indicators[0]]:
        #print(indicator)
        ind_class = IndicatorType(indicator, currency_key)
        df, years = get_df(facts, ind_class, indicators, tict)
        #print(df)
        if df is None:  # case when ticker doesn't have this indicator
            continue
        print_metric_information(ind_class, facts, n)
        indexes_to_update = find_indexes_with_full_year_data(df, years)
        df = convert_full_years_data_to_quarter_data(df, indexes_to_update, ind_class)
        df = df.sort_values(by=['end']).dropna().reset_index(drop=True).reindex(columns=base_columns + [ind_class.name])
        #print(df)

        if total_df is None:
            total_df = df
        else:
            total_df = pd.merge(total_df, df, how='outer', on=['end', 'year', 'quarter'])

    print(f'valid metrics {indicators.valid_indicators}')
    total_df[indicators.valid_indicators] = total_df[indicators.valid_indicators] / 1000000
    #print(total_df)
    total_df.to_csv(f'{main_folder_path}metrics\\{ticker}_metrics.csv', index=False)
