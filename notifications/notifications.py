import requests
import logging.config
from selenium import webdriver
import time, os, json

fmt = ('%(asctime)s: %(threadName)s: %(name)s: %(levelname)s: %(message)s')

logging.basicConfig(
    format=fmt,
    level=logging.INFO,
    datefmt='%H:%M:%S'
    )
logger = logging.getLogger('solarbot') 


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
        self.browser.execute_script("arguments[0].click();", python_button)
        time.sleep(10)

        EnergyToday = self.browser.find_elements_by_xpath(
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[1]/b")[0]
        
        EnergyThisMonth = self.browser.find_elements_by_xpath(
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[2]/b")[0]

        EnergyThisYear = self.browser.find_elements_by_xpath(
            "/html/body/section/section/main/div/div/div/div/div/div/div/div/div/div[2]/div/div/div[1]/div[1]/div[2]/div/div[2]/div/ul/li[3]/b")[0]

        return EnergyToday.text,EnergyThisMonth.text,EnergyThisYear.text

    def tearDown(self):
        self.browser.quit()


def hoymiles(link,usuario,senha):
    main = sistemasolar()
    EnergyToday,EnergyThisMonth,EnergyThisYear = main.testsolar(link,usuario,senha)
    main.tearDown()
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
        #{"ok":false,"error_code":401,"description":"Unauthorized"}
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
