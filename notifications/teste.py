from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get('https://nikkei225jp.com/data/karauri.php')
sleep(5)
html = driver.page_source.encode('utf-8')
driver.close()

df_list = pd.read_html(html, header=0)
print(df_list[3].head())
