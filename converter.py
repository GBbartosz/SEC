import pandas as pd

# in converter folder path create file with name {ticker}_metrics_raw.csv
# use desing raw file
# copy data from macrotrends (newest dates up)
# copy release date (end) and period end (end_period) from investing.com
# leave year and quarter empty
# change ticker below
# run script


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
    elif '.' in x:
        x = float(x) * 1000
    else:
        x = float(x)
    return x


def convert_date_to_polish_date(x):
    # if value was downloaded using financial statement reader
    # there is normal date format 01.12.2024 instead of gru.24
    if len(x) == 10:
        return month_num_to_pl_name_dict[x[3:5]] + '.' + x[-2:]
    else:
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
                 'paź': 10,
                 'pa?': 10,
                 'lis': 11,
                 'gru': 12}

month_num_str_to_quarter_dict = {'01': 1,
                                 '02': 1,
                                 '03': 1,
                                 '04': 2,
                                 '05': 2,
                                 '06': 2,
                                 '07': 3,
                                 '08': 3,
                                 '09': 3,
                                 '10': 4,
                                 '11': 4,
                                 '12': 4}

month_num_to_pl_name_dict = {'01': 'sty',
                             '02': 'lut',
                             '03': 'mar',
                             '04': 'kwi',
                             '05': 'maj',
                             '06': 'cze',
                             '07': 'lip',
                             '08': 'sie',
                             '09': 'wrz',
                             '10': 'paz',
                             '11': 'lis',
                             '12': 'gru'}


main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2025\\'
converter_folder_path = f'{main_folder_path}converter_to_2025\\converted_raw_files\\'
metrics_folder_path = f'{main_folder_path}metrics\\'
tickers_df = pd.read_excel(f'{main_folder_path}tickers_data.xlsx')

for ticker in tickers_df['ticker']:
    file_name = f'{ticker}_metrics_raw.csv'

    try:
        file_name = f'{converter_folder_path}{file_name}'
        df = pd.read_csv(file_name, sep=',')
        print(ticker)
        print(df.tail())
    except FileNotFoundError:
        continue

    for c in df.columns:
        if 'Unnamed' in c:
            df = df.drop(c, axis=1)

    # end
    df['end'] = pd.to_datetime(df['end'])
    df['end'] = df['end'] + pd.Timedelta(days=1)  # wyniki podawane po zamknięciu sesji

    # year, quarter
    df['quarter'] = df['end_period'].apply(lambda x: month_num_str_to_quarter_dict[x.split('-')[1]])
    df['year'] = df['end_period'].str[:4]

    # Indicators
    df = df[['end', 'year', 'quarter', 'Revenue', 'NetIncome', 'Shares']]
    df = df.sort_values(by='end').reset_index(drop=True)

    print(df.tail())
    df.to_csv(f'{metrics_folder_path}{ticker}_metrics.csv', index=False)
    print()
    print()
