import pandas as pd

# in converter folder path create file with name {ticker}_metrics_raw.csv
# use desing raw file
# copy data from macrotrends (newest dates up)
# copy release date (end) and period end (end_period) from investing.com
# leave year and quarter empty
# change ticker below
# run script


tickers = ['AAPL',
            'ADBE',
            'ALB',
            'AMZN',
            'AVGO',
            'BABA',
            'BIDU',
            'CMG',
            'COST',
            'CRM',
            'DELL',
            'F',
            'GOOGL',
            'HD',
            'HPQ',
            'JNJ',
            'KO',
            'LLY',
            'MA',
            'MCD',
            'META',
            'MP',
            'MSFT',
            'NFLX',
            'NVDA',
            'NVO',
            'PEP',
            'PYPL',
            'SBUX',
            'SHAK',
            'TSLA',
            'V',
            'WEN',
            'WMT',
            'YUM']
#tickers = ['HD']

pd.reset_option('display.max_rows')
pd.reset_option('display.max_columns')
pd.reset_option('display.width')
pd.reset_option('display.float_format')
pd.reset_option('display.max_colwidth')

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 40)
pd.set_option('display.width', 400)


def convert_number(x):
    x = str(x)
    if ',' in x:
        x = float(x.replace(',', '.')) * 1000
    else:
        x = float(x)
    return x

eng_month_dict = {'Jan': '01',
                  'Feb': '02',
                  'Mar': '03',
                  'Apr': '04',
                  'May': '05',
                  'Jun': '06',
                  'Jul': '07',
                  'Aug': '08',
                  'Sep': '09',
                  'Oct': '10',
                  'Nov': '11',
                  'Dec': '12'}

pl_month_dict = {'sty': 1,
                 'lut': 2,
                 'mar': 3,
                 'kwi': 4,
                 'maj': 5,
                 'cze': 6,
                 'lip': 7,
                 'sie': 8,
                 'wrz': 9,
                 'paz': 10,
                 'lis': 11,
                 'gru': 12}

pl_month_quarter_dict = {'sty': 1,
                         'lut': 1,
                         'mar': 1,
                         'kwi': 2,
                         'maj': 2,
                         'cze': 2,
                         'lip': 3,
                         'sie': 3,
                         'wrz': 3,
                         'paz': 4,
                         'pa?': 4,
                         'lis': 4,
                         'gru': 4}

for ticker in tickers:
    print(ticker)

    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    converter_folder_path = f'{main_folder_path}converter\\'
    file_name = f'{ticker}_metrics_raw.csv'

    df = pd.read_csv(f'{converter_folder_path}{file_name}', sep=';')
    print(df.head())

    for c in df.columns:
        if 'Unnamed' in c:
            df = df.drop(c, axis=1)

    # end
    df[['month', 'day', 'year']] = df['end'].str.split(' ', expand=True)
    df['day'] = df['day'].str.replace(',', '')
    df['month'] = df['month'].map(eng_month_dict)
    df['end'] = df['year'] + '-' + df['month'] + '-' + df['day']
    df['end'] = pd.to_datetime(df['end'])
    df['end'] = df['end'] + pd.Timedelta(days=1)  # wyniki podawane po zamknięciu sesji

    # year, quarter
    df[['end_period_month', 'end_period_year']] = df['end_period'].str.split('.', expand=True)
    df['quarter'] = df['end_period_month'].map(pl_month_quarter_dict).astype(int)
    df['year'] = ('20' + df['end_period_year']).astype(int)

    #
    df['Revenue'] = df['Revenue'].str.replace('$', '').apply(lambda x: convert_number(x)).round(0)
    df['NetIncome'] = df['NetIncome'].str.replace('$', '').apply(lambda x: convert_number(x)).round(0)
    df['Shares'] = df['Shares'].apply(lambda x: convert_number(x)).round(0)

    df = df[['end', 'year', 'quarter', 'Revenue', 'NetIncome', 'Shares']]
    df = df.sort_values(by='end').reset_index(drop=True)

    print(df.tail())
    df.to_csv(f'{converter_folder_path}{ticker}_metrics.csv', index=False)
    print()
    print()
