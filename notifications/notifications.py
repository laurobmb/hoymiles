#!/usr/bin/env python3


import requests
import time
import json
import os
import logging.config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options as FirefoxOptions


fmt = ('%(asctime)s: %(threadName)s: %(name)s: %(levelname)s: %(message)s')

logging.basicConfig(
    format=fmt,
    level=logging.INFO,
    datefmt='%H:%M:%S'
    )
logger = logging.getLogger('solarbot') 


class sistemasolar():
    def __init__(self):
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument('ignore-certificate-errors')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Firefox(options=options)
        self.vars = {}
  
    def teardown_method(self):
      self.driver.quit()
  
    def login(self,LINK,USUARIO,SENHA):
        self.driver.get(LINK)
        self.driver.set_window_size(1000, 1000)
        self.driver.find_element(By.ID, "name").click()
        self.driver.find_element(By.ID, "name").send_keys(USUARIO)
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys(SENHA)
        self.driver.find_element(By.CSS_SELECTOR, ".submit_button").click()
        time.sleep(50)

        EnergyToday = self.driver.find_element(By.XPATH,"/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[1]/span[2]")
        
        EnergyThisMonth = self.driver.find_element(By.XPATH,"/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[2]/span[2]")

        EnergyThisYear = self.driver.find_element(By.XPATH,"/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[3]/span[2]")

        print(EnergyToday.text,EnergyThisMonth.text,EnergyThisYear.text)
        return EnergyToday.text,EnergyThisMonth.text,EnergyThisYear.text


def hoymiles(link,usuario,senha):
    main = sistemasolar()
    EnergyToday,EnergyThisMonth,EnergyThisYear = main.login(link,usuario,senha)
    main.teardown_method()
    logger.info("SUCCESS: TODAY: {} MONTH: {} YEAR: {}".format(EnergyToday,EnergyThisMonth,EnergyThisYear,))
    return EnergyToday,EnergyThisMonth,EnergyThisYear


def telegram_bot_sendtext(TOKEN,CHAT_ID,bot_message,USER,DEBUG):
    bot_token = TOKEN
    bot_chatID = CHAT_ID
    send_url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    if DEBUG == '1':
        print(send_url)
    response = requests.get(send_url)
    resposta = response.content.decode('UTF-8')
    resposta = json.loads(resposta)
    if DEBUG == '1':
        print(resposta)
    error_code = resposta['ok']
    if error_code:
        logger.info("SUCCESS: GRUPO: {} USER: {} MESSAGE: {}".format(bot_chatID,USER,bot_message,))
        return response.json()     
    else:
        logger.info("FAILED: GRUPO: {} USER: {} MESSAGE: {}".format(bot_chatID,USER,bot_message,))
        return 'Error'


if __name__ == '__main__':
    bot_token = os.environ['TOKEN']
    bot_chatID = os.environ['CHAT_ID']
    link = os.environ['LINK']
    usuario = os.environ['USUARIO']
    senha = os.environ['SENHA']
    DEBUG = os.environ['DEBUG']

    if DEBUG == '1':
        print('TOKEN ->',bot_token)
        print('CHAT_ID->',bot_chatID)
        print('LINK->',link)
        print('USUARIO->',usuario)
        print('SENHA->',senha)
        print('DEBUG->',DEBUG)

    EnergyToday,EnergyThisMonth,EnergyThisYear = hoymiles(link,usuario,senha)

    if DEBUG == '1':
        print(EnergyToday,EnergyThisMonth,EnergyThisYear)

    text = 'Dados de '+usuario+':\nHoje: '+EnergyToday+'\nMes: '+EnergyThisMonth+'\nAno: '+EnergyThisYear

    if DEBUG == '1':
        print(text)

    try:
        telegram_bot_sendtext(bot_token,bot_chatID,text,usuario,DEBUG)
    except:
        print("Erro ao enviar msg -> ")
