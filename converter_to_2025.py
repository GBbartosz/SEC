import pandas as pd
import os


def format_end(x):
    m, d, y = x.split(' ')
    d = d.replace(',', '').zfill(2)
    m = ang_month_to_str_num_dict[m]
    return f'{y}-{m}-{d}'


def format_numbers(x):
    x = str(x)
    if ',' in x:
        x = round(float(x.replace('$', '').replace(',', '.')) * 1000, 0)
    elif '.' in x:
        x = round(float(x.replace('$', '')) * 1000, 0)
    else:
        minus_character = '-' if '-' in x else ''
        x = round(float(minus_character + '0.' + x.replace('$', '').replace('-', '').zfill(3)) * 1000, 0)
    return x


ang_month_to_str_num_dict = {'Jan': '01',
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

pl_month_to_str_num_dict = {'sty': '01',
                            'lut': '02',
                            'mar': '03',
                            'kwi': '04',
                            'maj': '05',
                            'cze': '06',
                            'lip': '07',
                            'sie': '08',
                            'wrz': '09',
                            'paz': '10',
                            'paź': '10',
                            'pa?': '10',
                            'lis': '11',
                            'gru': '12'}

folder_path = 'C:\\Users\\barto\\Desktop\\SEC2025\\converter_to_2025'
files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

for file in files:
    print(file)
    path = folder_path + '\\' + file
    df = pd.read_csv(path, sep=';')

    df['end'] = pd.to_datetime(df['end'].apply(format_end))

    df['end_period'] = df['end_period'].apply(lambda x: '20' + x[-2:] + '-' + pl_month_to_str_num_dict[x[:3]] + '-01' if x[:3] in pl_month_to_str_num_dict.keys() else x)
    df['end_period'] = pd.to_datetime(df['end_period'].apply(lambda x: x[-4:] + '-' + x[3:5] + '-' + x[:2] if '.' in x else x))

    for col in ['Revenue', 'NetIncome', 'Shares']:
        df[col] = df[col].apply(format_numbers)

    df.to_csv(path, index=False)
