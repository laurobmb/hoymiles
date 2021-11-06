#!/usr/bin/env python3

import unittest
from selenium import webdriver
import time, os

class sistemasolar():
    def __init__(self):
        self.profile = webdriver.ChromeOptions()
        self.profile.add_argument('ignore-certificate-errors')
        self.profile.add_argument('--headless')
        self.profile.add_argument('--no-sandbox')
        self.profile.add_argument('--disable-dev-shm-usage')
        chrome_driver_binary = "chromedriver"
        self.browser = webdriver.Chrome(chrome_driver_binary,options=self.profile)
        
    def testsolar(self,LINK,USER,PASSWORD):
        self.browser.get(LINK)
        python_button = self.browser.find_elements_by_xpath('//*[@id="name"]')[0]
        python_button.click()
        python_button.send_keys(USER)
        time.sleep(1)    
        python_button = self.browser.find_elements_by_xpath('//*[@id="password"]')[0]
        python_button.click()
        python_button.send_keys(PASSWORD)
        python_button = self.browser.find_elements_by_xpath(
                '/html/body/div[1]/div[2]/div[3]/form/div[3]/div/div/span/button')[0]
        python_button.click()
        time.sleep(10)

        EnergyToday = self.browser.find_elements_by_xpath(
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div[1]/div/div/div[2]/div/div[2]/ul/li[2]/b")[0]

        EnergyThisMonth = self.browser.find_elements_by_xpath(
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div[1]/div/div/div[2]/div/div[2]/ul/li[3]/b")[0]

        return EnergyToday,EnergyThisMonth

    def tearDown(self):
        self.browser.quit()

if __name__ == '__main__':
    link = os.environ['link']
    usuario = os.environ['usuario']
    senha = os.environ['senha']
    main = sistemasolar()
    EnergyToday,EnergyThisMonth = main.testsolar(link,usuario,senha)
    print('Total de energia de hoje:',EnergyToday.text)
    print('Total de energia do mes:',EnergyThisMonth.text)
    main.tearDown()

