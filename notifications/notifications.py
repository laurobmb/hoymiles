import requests
import logging.config
from selenium import webdriver
import time, os

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

        ##### pagina de manutenção
        time.sleep(3)
        python_button = self.browser.find_elements_by_xpath(
            '/html/body/div[2]/div/div[2]/div/div[2]/div[3]/div/button')[0]
        python_button.click()
        time.sleep(3)
        ##### pagina de manutenção

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

        return EnergyToday.text,EnergyThisMonth.text

    def tearDown(self):
        self.browser.quit()


def hoymiles(link,usuario,senha):
    main = sistemasolar()
    EnergyToday,EnergyThisMonth = main.testsolar(link,usuario,senha)
    main.tearDown()
    return EnergyToday,EnergyThisMonth

def telegram_bot_sendtext(TOKEN,CHAT_ID,bot_message,USER):
    bot_token = TOKEN
    bot_chatID = CHAT_ID
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
    try:
        response = requests.get(send_text)
        logger.info("GRUPO: {} USER: {} MESSAGE: {} SUCCESS".format(bot_chatID,USER,bot_message,))
    except:
        logger.info("GRUPO: {} USER: {} MESSAGE: {} Failed".format(bot_chatID,USER,bot_message,))

    return response.json()

if __name__ == '__main__':
    bot_token = os.environ['TOKEN']
    bot_chatID = os.environ['CHAT_ID']
    link = os.environ['LINK']
    usuario = os.environ['USUARIO']
    senha = os.environ['SENHA']
    EnergyToday,EnergyThisMonth = hoymiles(link,usuario,senha)
    text = usuario+': Total de energia de hoje: '+EnergyToday+' Total de energia do mes: '+EnergyThisMonth
    telegram_bot_sendtext(bot_token,bot_chatID,text,usuario)
