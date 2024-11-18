from selenium import webdriver
import time


ticker = 'META'

driver = webdriver.Chrome()

links = ['https://www.macrotrends.net/stocks/charts/{ticker}/meta-platforms/revenue',
         'https://www.macrotrends.net/stocks/charts/{ticker}/meta-platforms/shares-outstanding']

for t in list(range(1, 5)):
    driver.get()
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get()

time.sleep(180)
