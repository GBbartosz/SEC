import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


def get_data_from_table(mydriver):
    tables = mydriver.find_elements(By.CLASS_NAME, 'historical_data_table')
    table = tables[1]
    rows = table.find_elements(By.TAG_NAME, "tr")
    mydata = []
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")  # Use 'th' for header rows if necessary
        row_data = [cell.text for cell in cells]
        mydata.append(row_data)
    return mydata


def prepare_df(mydata):
    mydf = pd.DataFrame(mydata)
    mydf.columns = ['date', 'value']
    mydf = mydf.replace('', None)
    mydf = mydf.dropna(subset='value').reset_index(drop=True)
    return mydf


def prepare_string_to_float(x):
    x = x.replace('$', '').replace(',', '.')
    if '.' in x:
        pass
    elif '-' in x:
        x = '-0.' + x[1:]
    else:
        x = '0.' + x
    return x


def download_data(ticker):
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # navigating from main page to ticker's revenue
    main_page_link = 'https://www.macrotrends.net/'
    driver.get(main_page_link)
    input_element = driver.find_element(By.CLASS_NAME, 'js-typeahead')
    input_element.send_keys(ticker)
    time.sleep(1)
    input_element.send_keys(Keys.ARROW_DOWN + Keys.ENTER)

    # getting links
    revenue_link = driver.current_url
    ticker_link = revenue_link[:-7]

    # scraping revenue data
    data = get_data_from_table(driver)
    revenue_df = prepare_df(data)

    # scraping net income data
    net_income_link = ticker_link + 'net-income'
    driver.get(net_income_link)
    data = get_data_from_table(driver)
    net_income_df = prepare_df(data)

    # shares outstanding
    shares_outstanding_link = ticker_link + 'shares-outstanding'
    driver.get(shares_outstanding_link)
    data = get_data_from_table(driver)
    shares_outstanding_df = prepare_df(data)

    # joining data
    df = revenue_df.merge(net_income_df, on='date', how='inner')
    df = df.merge(shares_outstanding_df, on='date', how='inner')
    df.columns = ['date', 'Revenue', 'NetIncome', 'Shares']
    df[['Revenue', 'NetIncome', 'Shares']] = df[['Revenue', 'NetIncome', 'Shares']].map(prepare_string_to_float)
    df = df.astype({'Revenue': 'float', 'NetIncome': 'float', 'Shares': 'float'})
    print(df)

    # saving to csv
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    raw_data_file_path = f'{main_folder_path}converter\\{ticker}_metrics_raw.csv'
    df.to_csv(raw_data_file_path, index=False)
    driver.quit()
    return df


def print_results(df):
    path = 'C:\\Users\\barto\\Desktop\\SEC2024\\converter\\META_metrics_raw.csv'
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])

    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(14, 10))
    i = 0
    for c in df.columns[1:]:
        sns.lineplot(data=df, x='date', y=c, marker='o', ax=axs[i])
        i += 1
    plt.show()


def download_data_0(ticker):
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    investing_link = ''
    driver.get(investing_link)


ticker = 'META'
ddf = download_data(ticker)
print_results(ddf)
