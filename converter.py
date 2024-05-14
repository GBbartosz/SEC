import pandas as pd

# in converter folder path create file with name {ticker}_metrics_raw.csv
# use desing raw file
# copy data from macrotrends (newest dates up)
# leave year and quarter empty
# change ticker below
# run script

ticker = 'META'
main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
converter_folder_path = f'{main_folder_path}converter\\'
file_name = f'{ticker}_metrics_raw.csv'

df = pd.read_csv(f'{converter_folder_path}{file_name}', sep=';')
print(df.head())

df['end'] = pd.to_datetime(df['end'])
df['year'] = df['end'].dt.year
df['quarter'] = df['end'].dt.quarter

df['Revenue'] = df['Revenue'].str.replace('$', '').str.replace(',', '').astype(float)
df['NetIncome'] = df['NetIncome'].str.replace('$', '').str.replace(',', '').astype(float)
df['Shares'] = df['Shares'].str.replace(',', '').astype(float)
df = df.iloc[::-1]

print(df.head())
df.to_csv(f'{converter_folder_path}{ticker}_metrics.csv', index=False)
