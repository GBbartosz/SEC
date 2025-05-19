import csv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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


def download_data(myticker, name):
    options = Options()
    options.add_argument("--incognito")

    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)

    # navigating from main page to ticker's revenue
    main_page_link = 'https://www.macrotrends.net/'
    driver.get(main_page_link)
    input_element = driver.find_element(By.CLASS_NAME, 'js-typeahead')
    input_element.send_keys(name)
    time.sleep(1.5)
    input_element.send_keys(Keys.ARROW_DOWN + Keys.ENTER)

    # getting links
    revenue_link = driver.current_url
    ticker_link = revenue_link[:-7]
    time.sleep(0.5)

    # click accept all button
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept all')]"))
        )
        accept_button.click()
    except Exception as e:
        print("Accept button not found or couldn't be clicked:", e)

    # scraping revenue data
    data = get_data_from_table(driver)
    revenue_df = prepare_df(data)

    # scraping net income data
    net_income_link = ticker_link + 'net-income'
    driver.get(net_income_link)
    time.sleep(0.5)
    data = get_data_from_table(driver)
    net_income_df = prepare_df(data)

    # shares outstanding
    shares_outstanding_link = ticker_link + 'shares-outstanding'
    driver.get(shares_outstanding_link)
    time.sleep(0.5)
    data = get_data_from_table(driver)
    shares_outstanding_df = prepare_df(data)

    # joining data
    df = revenue_df.merge(net_income_df, on='date', how='inner')
    df = df.merge(shares_outstanding_df, on='date', how='inner')
    df.columns = ['date', 'Revenue', 'NetIncome', 'Shares']
    df[['Revenue', 'NetIncome', 'Shares']] = df[['Revenue', 'NetIncome', 'Shares']].map(prepare_string_to_float)
    #df = df.astype({'Revenue': 'float', 'NetIncome': 'float', 'Shares': 'float'})
    print(df)

    # Preparing for excel
    df['end'] = None
    df['end_period'] = None
    df['year'] = None
    df['quarter'] = None
    df['empty1'] = None
    df['empty2'] = None
    df['empty3'] = None
    df = df[['end', 'end_period', 'year', 'quarter', 'empty1', 'empty2', 'empty3', 'date', 'Revenue', 'NetIncome', 'Shares']]

    # saving to csv
    main_folder_path = 'C:\\Users\\barto\\Desktop\\SEC2024\\'
    raw_data_file_path = f'{main_folder_path}converter\\{myticker}_metrics_raw.xlsx'
    df.to_excel(raw_data_file_path, index=False)
    driver.quit()
    return df


def print_results(myticker):
    path = f'C:\\Users\\barto\\Desktop\\SEC2024\\converter\\{myticker}_metrics_raw.xlsx'
    df = pd.read_excel(path)
    df['date'] = pd.to_datetime(df['date'])

    fig, axs = plt.subplots(nrows=3, ncols=1, figsize=(14, 10))
    i = 0
    for c in ['Revenue', 'NetIncome', 'Shares']:
        sns.lineplot(data=df, x='date', y=c, marker='o', ax=axs[i])
        i += 1
    plt.show()


def download_data_0(myticker):
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    google_link = 'https://www.investing.com//'
    driver.get(google_link)
    time.sleep(7)
    input_element = driver.find_element(By.CLASS_NAME, 'mainSearch_input-wrapper__hWkM3 ')
    input_element.send_keys(myticker)
    time.sleep(1)
    input_element.send_keys(Keys.ENTER)
    time.sleep(1)
    investing_link = driver.find_element(By.CLASS_NAME, 'srp')
    time.sleep(5)
    driver.quit()



#ticker = 'AGRO'
#name = 'Adecoagro'
#ddf = download_data(ticker, name)
#ddf = download_data_0(ticker)
#print_results(ticker)

#'AVD': 'American Vanguard',
#'EBAY': 'eBay',
#'FNF': 'Fidelity',
#'HSY': 'Hershey'
#'KLAC': 'KLA Tencor',
#'MU': 'Micron',
stock_dict = {

              }
for ticker, name in stock_dict.items():
    print(f'{ticker} - {name}')
    ddf = download_data(ticker, name)

