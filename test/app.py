#!/usr/bin/env python3

from selenium import webdriver
import time, os, unittest

class sistemasolar(unittest.TestCase):

    def setUp(self):
        self.profile = webdriver.ChromeOptions()
        self.profile.add_argument('ignore-certificate-errors')
        chrome_driver_binary = "/usr/local/bin/chromedriver"
        self.browser = webdriver.Chrome(chrome_driver_binary,options=self.profile)
        
    def testsolar(self):
        usuario = os.environ['usuario']
        senha = os.environ['senha']
        link = os.environ['link']
        self.browser.get(link)
        self.assertIn('S-Miles Cloud - Hoymiles Power Electronics Inc.', self.browser.title)
        time.sleep(1)    
        python_button = self.browser.find_elements_by_xpath('//*[@id="name"]')[0]
        python_button.click()
        python_button.send_keys(usuario)
        time.sleep(1)    
        python_button = self.browser.find_elements_by_xpath('//*[@id="password"]')[0]
        python_button.click()
        python_button.send_keys(senha)
        python_button = self.browser.find_elements_by_xpath(
                '/html/body/div[1]/div[2]/div[3]/form/div[3]/div/div/span/button')[0]
        python_button.click()
        time.sleep(10)    

        EnergyToday = self.browser.find_elements_by_xpath(
            #"/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div[1]/div/div/div[2]/div/div[2]/ul/li[2]/b")[0]
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[1]/b")[0]
        print('Total de energia de hoje:',EnergyToday.text)

        EnergyThisMonth = self.browser.find_elements_by_xpath(
            #"/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div[1]/div[1]/div/div/div[2]/div/div[2]/ul/li[3]/b")[0]
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[2]/b")[0]
        print('Total de energia do mes:',EnergyThisMonth.text)

        EnergyThisYear = self.browser.find_elements_by_xpath(
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[3]/b")[0]
        print('Total de energia do ano:',EnergyThisYear.text)

        return EnergyToday,EnergyThisMonth,EnergyThisYear

    def tearDown(self):
        self.browser.quit()

if __name__ == '__main__':
    unittest.main(verbosity=3)

