from playwright.sync_api import sync_playwright
from time import sleep
import os, requests, json, sys
import logging.config


fmt = ('%(asctime)s: %(threadName)s: %(name)s: %(levelname)s: %(message)s')
#logging.basicConfig(format=fmt,level=logging.INFO,datefmt='%H:%M:%S')
logging.basicConfig(format=fmt,level=logging.DEBUG,datefmt='%H:%M:%S')
logger = logging.getLogger('hoymiles bot') 


def hoymiles(USER,SENHA):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        try:
            web_url='https://global.hoymiles.com/platform/login'
            page.goto(web_url)
        except Exception as e:
            logger.error("ERROR: Erro ao acessar pagina da: {} {}".format(web_url,e))
            sys.exit()

        page.locator('//*[@id="basic_username"]').fill(USER)
        page.locator('//*[@id="basic_password"]').fill(SENHA)
        sleep(2)
        page.locator(".submit").click()
        sleep(30)
        
        page.set_viewport_size({"width": 1920, "height": 1200})
        
        diretorio_corrente = os.path.abspath(os.getcwd())
        spath=diretorio_corrente + '/' + 'photos/'
        page.screenshot(path=spath + 'screenshot'+hoymiles_user+'.png')

        energy_today_selector = 'p.energy:nth-child(2) > span:nth-child(1)'
        page.wait_for_selector(energy_today_selector);
        energy_today_selector_texto = page.inner_text(energy_today_selector)
        logger.info("Energy Today: {} Wh".format(energy_today_selector_texto))
        sleep(2)

        energy_this_month_selector = '.stats > div:nth-child(1) > p:nth-child(2) > span:nth-child(1)'
        page.wait_for_selector(energy_this_month_selector);
        energy_this_month_selector_texto = page.inner_text(energy_this_month_selector)
        logger.info("Energy This Month: {} Wh".format(energy_this_month_selector_texto))
        sleep(2)

        energy_this_year_selector = 'div.item:nth-child(2) > p:nth-child(2) > span:nth-child(1)'
        page.wait_for_selector(energy_this_year_selector);
        energy_this_year_selector_texto = page.inner_text(energy_this_year_selector)
        logger.info("Energy This Year: {} MWh".format(energy_this_year_selector_texto))
        sleep(2)

        lifetime_energy_selector = 'div.item:nth-child(3) > p:nth-child(2) > span:nth-child(1)'
        page.wait_for_selector(lifetime_energy_selector);
        lifetime_energy_selector_texto = page.inner_text(lifetime_energy_selector)
        logger.info("Lifetime Energy: {} MWh".format(lifetime_energy_selector_texto))
        sleep(2)

        browser.close()
        return energy_today_selector_texto,energy_this_month_selector_texto,energy_this_year_selector_texto,lifetime_energy_selector_texto


def telegram_bot_sendphoto(TOKEN,CHAT_ID,caption=None):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

        diretorio_corrente = os.path.abspath(os.getcwd())
        spath=diretorio_corrente + '/' + 'photos/'
        photo_path = spath + 'screenshot' + hoymiles_user + '.png'

        logger.debug("DEBUG: Show variaveis photo_path: {} url: {}".format(photo_path,url))

        files = {'photo': open(photo_path, 'rb')}
        data = {'chat_id': CHAT_ID, 'caption': caption}

        try:
            response = requests.post(url, files=files, data=data)

        except Exception as e:
            logger.error("ERROR ao acessar a API do Telegram: {}".format(e))
            sys.exit()

        logger.info("SUCCESS: Foto enviada http_code: {}".format(response.status_code,))

    except Exception as e:
        logger.error("ERROR: Foto nao enviada http_code: {} {}".format(response.status_code,e))
        sys.exit()


def telegram_bot_sendtext(TOKEN,CHAT_ID,bot_message,USER,debug,caption=None):
    bot_token = TOKEN
    bot_chatID = CHAT_ID

    send_url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    logger.debug("DEBUG: Show variaveis send_url: {}".format(send_url))

    response = requests.get(send_url)
    resposta = response.content.decode('UTF-8')
    resposta = json.loads(resposta)

    logger.debug("DEBUG: Show variaveis resposta: {}".format(resposta))

    error_code = resposta['ok']

    if error_code:
        logger.info("SUCCESS: GRUPO: {} USER: {} MESSAGE: {}".format(bot_chatID,USER,bot_message,))
        return response.json()     
    else:
        logger.error("FAILED: GRUPO: {} USER: {} MESSAGE: {}".format(bot_chatID,USER,bot_message,))
        return 'Error'


def hoymiles_local(STATUS):

    logger.debug("DEBUG: Show variaveis STATUS: {} {}".format(STATUS,type(STATUS)))

    if STATUS.lower() == "true":
        url = "http://192.168.0.107/cm?cmnd=energyyesterday"
        response = requests.get(url)
        if response.status_code == 200:
            json_data = response.json()
            today_value = json_data["EnergyYesterday"]["Today"]
            yesterday_value = json_data["EnergyYesterday"]["Yesterday"]
            logger.info("INFO: Coleta do dia: {} Coleta do dia anterior: {}".format(today_value,yesterday_value))
            return today_value
        else:
            logger.error("FAILED: Coleta do dia: {} Coleta do dia anterior: {}".format(today_value,yesterday_value))
            today_value = 0
            return today_value
    else:
        logger.info("INFO: Coleta local desativada")
        today_value = 0
        return today_value


def main():
    energy_today,energy_this_month,energy_this_year,lifetime_energy = hoymiles(hoymiles_user,hoymiles_pass)
    coleta_local = hoymiles_local(status_coleta_local)
    
    coleta_total_de_hoje = coleta_local + float(energy_today)

    try:
        mensagem = ">>>> USINA " + hoymiles_user + " <<<<\nColeta de hoje: "+energy_today+" Wh"+"\nColeta do mes: "+energy_this_month+" Wh"+"\nColeta do ano: "+energy_this_year+" MWh"+"\nColeta da vida toda: "+lifetime_energy+" MWh"+"\nColeta Local: "+str(coleta_local)+" Wh"+"\n\nColeta total de hoje: "+str(coleta_total_de_hoje)
        
        telegram_bot_sendphoto(bot_token,bot_chatID)

        telegram_bot_sendtext(bot_token,bot_chatID,mensagem,hoymiles_user,debug)
        
        logger.info("INFO: Usina do usuario {} Coleta de hoje: {} Wh Coleta do mes: {} Wh Coleta do ano: {} MWh Coleta da vida toda: {} MWh Coleta Local: {} Wh Coleta total de hoje: {}".format(hoymiles_user,energy_today,energy_this_month,energy_this_year,lifetime_energy,coleta_local,coleta_total_de_hoje))

    except Exception as e:
        logger.error("ERROR: A construcao da mensagem deu errado: {}".format(e))
        sys.exit()


if __name__ == "__main__":

    versao="v3"
    logger.info("INIT: Coleta de energia do sistema solar <<<<<<<<<<< {}".format(versao))    

    hoymiles_user = os.environ['USUARIO']
    hoymiles_pass = os.environ['SENHA']
    bot_token = os.environ['TOKEN']
    bot_chatID = os.environ['CHAT_ID']
    status_coleta_local = os.environ['STATUS_COLETA_LOCAL']
    try:
        debug = os.environ['DEBUG']
    except:
        debug = 0

    logger.debug("DEBUG: Show variaveis {} {} {} {} {} {}".format(hoymiles_user,hoymiles_pass,bot_token,bot_chatID,debug,status_coleta_local))

    main()