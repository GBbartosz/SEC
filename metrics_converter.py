import pandas as pd


ticker = 'V'  # input ticker

main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
converter_file_path = f'{main_folder_path}converter\\{ticker}_metrics_raw.xlsx'

raw_df = pd.read_excel(converter_file_path)
print(raw_df)




