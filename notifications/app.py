from playwright.sync_api import sync_playwright
from time import sleep
import os, requests, json
import logging.config

fmt = ('%(asctime)s: %(threadName)s: %(name)s: %(levelname)s: %(message)s')
logging.basicConfig(format=fmt,level=logging.INFO,datefmt='%H:%M:%S')
logger = logging.getLogger('hoymiles bot') 

def hoymiles(USER,SENHA):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto('https://global.hoymiles.com/platform/login')
        
        page.locator('//*[@id="name"]').fill(USER)
        page.locator('//*[@id="password"]').fill(SENHA)
        sleep(2)
        page.locator(".submit_button").click()
        sleep(20)
        page.screenshot(path='screenshot.png')

        energy_today_selector = 'li.sx-white-space:nth-child(1) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(energy_today_selector);
        energy_today_selector_texto = page.inner_text(energy_today_selector)
        logger.info("Energy Today: {} Wh".format(energy_today_selector_texto))
        sleep(2)

        energy_this_month_selector = 'li.sx-white-space:nth-child(2) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(energy_this_month_selector);
        energy_this_month_selector_texto = page.inner_text(energy_this_month_selector)
        logger.info("Energy This Month: {} Wh".format(energy_this_month_selector_texto))
        sleep(2)

        energy_this_year_selector = 'li.sx-white-space:nth-child(3) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(energy_this_year_selector);
        energy_this_year_selector_texto = page.inner_text(energy_this_year_selector)
        logger.info("Energy This Year: {} MWh".format(energy_this_year_selector_texto))
        sleep(2)

        lifetime_energy_selector = 'li.sx-white-space:nth-child(4) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(lifetime_energy_selector);
        lifetime_energy_selector_texto = page.inner_text(lifetime_energy_selector)
        logger.info("Lifetime Energy: {} MWh".format(lifetime_energy_selector_texto))
        sleep(2)

        browser.close()
        return energy_today_selector_texto,energy_this_month_selector_texto,energy_this_year_selector_texto,lifetime_energy_selector_texto

def telegram_bot_sendphoto(TOKEN,CHAT_ID,caption=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
        photo_path = './screenshot.png'
        files = {'photo': open(photo_path, 'rb')}
        data = {'chat_id': CHAT_ID, 'caption': caption}
        response = requests.post(url, files=files, data=data)
        logger.info("SUCCESS: Foto enviada http_code: {}".format(response.status_code,))
    except:
        logger.info("ERROR: Foto nao enviada http_code: {}".format(response.status_code,))

def telegram_bot_sendtext(TOKEN,CHAT_ID,bot_message,USER,DEBUG,caption=None):
    bot_token = TOKEN
    bot_chatID = CHAT_ID

    send_url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    if DEBUG == 1:
        print(send_url)

    response = requests.get(send_url)
    resposta = response.content.decode('UTF-8')
    resposta = json.loads(resposta)

    if DEBUG == 1:
        print(resposta)

    error_code = resposta['ok']

    if error_code:
        logger.info("SUCCESS: GRUPO: {} USER: {} MESSAGE: {}".format(bot_chatID,USER,bot_message,))
        return response.json()     
    else:
        logger.info("FAILED: GRUPO: {} USER: {} MESSAGE: {}".format(bot_chatID,USER,bot_message,))
        return 'Error'

def hoymiles_local():
    url = "http://192.168.0.107/cm?cmnd=energyyesterday"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        today_value = json_data["EnergyYesterday"]["Today"]
        yesterday_value = json_data["EnergyYesterday"]["Yesterday"]
        logger.info("INFO: Coleta do dia: {} Coleta do dia anterior: {}".format(today_value,yesterday_value))
        return today_value
    else:
        logger.info("FAILED: Coleta do dia: {} Coleta do dia anterior: {}".format(today_value,yesterday_value))
        today_value = 0
        return today_value
    
def main():
    energy_today,energy_this_month,energy_this_year,lifetime_energy = hoymiles(hoymiles_user,hoymiles_pass)
    coleta_local = hoymiles_local()

    if coleta_local == 1:
        coleta_total_de_hoje = coleta_local + float(energy_today)
    else:
        coleta_total_de_hoje = 0

    mensagem = "Coleta de hoje: "+energy_today+" Wh"+"\nColeta do mes: "+energy_this_month+" Wh"+"\nColeta do ano: "+energy_this_year+" MWh"+"\nColeta da vida toda: "+lifetime_energy+" MWh"+"\nColeta Local: "+str(coleta_local)+" Wh"+"\n\nColeta total de hoje: "+str(coleta_total_de_hoje)

    telegram_bot_sendphoto(bot_token,bot_chatID)
    
    telegram_bot_sendtext(bot_token,bot_chatID,mensagem,hoymiles_user,debug)

if __name__ == "__main__":

    hoymiles_user = os.environ['USUARIO']
    hoymiles_pass = os.environ['SENHA']
    bot_token = os.environ['TOKEN']
    bot_chatID = os.environ['CHAT_ID']
    debug = os.environ['DEBUG']
    coleta_local = os.environ['COLETA_LOCAL']

    main()
