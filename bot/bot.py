from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler,MessageHandler,Filters
import telegram
import requests, re, random, yaml, json, os, subprocess
import logging.config
import unittest
from selenium import webdriver
import time, os

#fmt = ("%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s")
fmt = ('%(asctime)s: %(threadName)s: %(name)s: %(levelname)s: %(message)s')

logging.basicConfig(
    format=fmt,
    level=logging.INFO,
#    filename='solar.log',
    datefmt='%H:%M:%S'
    )
logger = logging.getLogger('solarbot') 

rafael=177388057
lauro=67993868
solar_grupo=-660131018
administradores=[lauro]
usuarios_autorizados = [rafael,lauro,solar_grupo]

def credencial():
    file_name='.credential.json'
    full_file=os.path.abspath(os.path.join(file_name))
	with open(full_file) as jsonfile:
		parsed = json.load(jsonfile)
		servidor = parsed['informacoes']['db_host']
		usuario = parsed['informacoes']['db_user']
		senha = parsed['informacoes']['db_pass']
	return servidor,usuario,senha


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

        return EnergyToday.text,EnergyThisMonth.text

    def tearDown(self):
        self.browser.quit()


def hoymiles(link,usuario,senha):
    main = sistemasolar()
    EnergyToday,EnergyThisMonth = main.testsolar(link,usuario,senha)
    main.tearDown()
    return EnergyToday,EnergyThisMonth
    
def mount_dict(first_name,username,chat_id,tipo,text,is_bot):
    dicionario = {
        "USER": first_name, 
        "USERNAME": username, 
        "ID": chat_id, 
        "TYPE": tipo, 
        "MESSAGE": text,
        "BOT": is_bot
        }
    json_dumps = json.dumps(dicionario, sort_keys=True, indent=4)
    json_loads = json.loads(json_dumps)
    return json_dumps

def check_variavel(update, context):
    try:
        user_id = update._effective_user.id
        first_name = update._effective_user.first_name
        username = update._effective_user.username
        chat_id = update.message.chat.id
        text = update.message.text
        is_bot = update._effective_user.is_bot
    except:
        user_id = update._effective_user.id
        first_name = update._effective_user.first_name
        username = update._effective_user.username        
        chat_id = update.callback_query.message.chat.id
        text = update.callback_query.message.text
        is_bot = update._effective_user.is_bot

    return user_id,first_name,username,chat_id,text,is_bot  

def frase_aleatoria(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)    
    arquivo = "arquivos/frases.yaml"
    d1 = yaml_loader(arquivo)
    d2 = json.dumps(d1)
    d3 = json.loads(d2)
    frase = random.choice(d3['frases'])
    TIPO='falha de autenticação'
    logger.info("USER: {} \n USERNAME: {} ID: {} TYPE: {} MESSAGE: {} BOT: {}".format(first_name,username,chat_id,TIPO,text,is_bot))
    return frase

def valida_usuario(update, context, id_usuario):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)

    try:
        admins = context.bot.get_chat_administrators(chat_id)
        for i in admins:
            id_admin=i['user']['id']
            nome_admin=i['user']['first_name']
            username_admin=i['user']['username']
            bot_admin=i['user']['is_bot']
            status_admin=i['status']
            TIPO='falha de autenticação'
            logger.info("USER: {} USERNAME: {} ID: {} TYPE: {} STATUS: {} BOT: {}".format(nome_admin,username_admin,id_admin,TIPO,status_admin,bot_admin))
            continue
    except:
        admins = 0
    
    if user_id not in usuarios_autorizados:
        if chat_id < 0:
            try:
                context.bot.kick_chat_member(chat_id, user_id)
                context.bot.sendMessage(chat_id=user_id, text='Você não deveria entrar nesse grupo :)')
                update.message.reply_text('Ele não deveria estar nesse grupo, ele não foi autorizado')
            except:
                context.bot.sendMessage(chat_id=chat_id, text='Não sou admin do grupo, estou triste com isso')

    if id_usuario in usuarios_autorizados:
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: usuário autenticado MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))
        return 0    
    else:
        resposta = frase_aleatoria(update, context)
        update.message.reply_text(resposta)
        if chat_id < 0:
            update.message.reply_text('Sou lindo demais para estar nesse grupo')
            context.bot.leave_chat(chat_id)
    return 1

def start(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, update.message.chat.id)
    if validacao == 0:
        botao01 = InlineKeyboardButton("Giba", callback_data='hoymiles_giba')
        botao02 = InlineKeyboardButton("Lauro", callback_data='hoymiles_lauro')
        botao03 = InlineKeyboardButton("Rafael", callback_data='hoymiles_rafael')
        buttons_list = [[botao01], [botao02], [botao03]]
        reply_markup = InlineKeyboardMarkup(buttons_list)
        update.message.reply_text('faça sua escolha', reply_markup=reply_markup)
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: start MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def button(update, context):
    query = update.callback_query

    if query.data == 'voltar':
        voltar(update,context)

#### Comandos do botão START    
    if query.data == 'hoymiles_giba':
        hoymiles_giba(update,context)
    if query.data == 'hoymiles_lauro':
        hoymiles_lauro(update,context)
    elif query.data == 'hoymiles_rafael':
        hoymiles_rafael(update,context)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def yaml_loader(arquivo):
    with open(arquivo,"r") as stream:
        try:
            data = yaml.load(stream,Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)
    return data

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url
    
def frases(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        arquivo = "arquivos/frases.yaml"
        d1 = yaml_loader(arquivo)
        d2 = json.dumps(d1)
        d3 = json.loads(d2)
        frase = random.choice(d3['frases'])
        update.message.reply_text(frase)
    logger.info("USER: {} USERNAME: {} ID: {} TYPE: comando frases MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def frases_amor(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        arquivo = "arquivos/frases_amor.yaml"
        d1 = yaml_loader(arquivo)
        d2 = json.dumps(d1)
        d3 = json.loads(d2)
        frase = random.choice(d3['frases'])
        context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
        context.bot.send_message(chat_id=update.message.chat_id, text=frase)
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: comando frases_amor MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def help(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        update.message.reply_text("Use /start para que eu mostre os menus.")
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: help MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def bop(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        url = get_url()
        context.bot.send_photo(chat_id=chat_id, photo=url)
    logger.info("USER: {} USERNAME: {} ID: {} TYPE: comando bop MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))


def echo(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        chat_id = update.message.chat_id
        MsgRecebida = update.message.text.lower()
        if 'bom dia' in MsgRecebida or 'boa tarde' in MsgRecebida or 'boa noite' in MsgRecebida:
            if chat_id == lauro:
                context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                context.bot.sendMessage(chat_id=chat_id, text="*Oi lauro, voce falou?* "+first_name, parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                arquivo = "arquivos/bomdia.yaml"
                d1 = yaml_loader(arquivo)
                d2 = json.dumps(d1)
                d3 = json.loads(d2)
                i = random.randint(0,len(d3['frases']))
                context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                context.bot.sendMessage(chat_id=chat_id, text=random.choice(d3['frases'])+' '+first_name)
        
        if "muito inteligente" in MsgRecebida:
            arquivo = "arquivos/frases_inteligentes.yaml"
            d1 = yaml_loader(arquivo)
            d2 = json.dumps(d1)
            d3 = json.loads(d2)
            i = random.randint(0,len(d3['frases']))
            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            context.bot.sendMessage(chat_id=chat_id, text=random.choice(d3['frases'])+' '+first_name)

        if "magali" in MsgRecebida:
            arquivo = "arquivos/magali.yaml"
            d1 = yaml_loader(arquivo)
            d2 = json.dumps(d1)
            d3 = json.loads(d2)
            i = random.randint(0,len(d3['frases']))
            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            context.bot.sendMessage(chat_id=chat_id, text=random.choice(d3['frases'])+' '+first_name)

        if "coisa de dev" in MsgRecebida:
          arquivo = "arquivos/dev.yaml"
          d1 = yaml_loader(arquivo)
          frase = random.choice(d1['frases_informatica']['frase01'])+random.choice(d1['frases_informatica']['frase02'])+random.choice(d1['frases_informatica']['frase03'])+random.choice(d1['frases_informatica']['frase04'])
          context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)
          context.bot.sendMessage(chat_id=update.message.chat_id, text=frase)
    
        if "besteira" in MsgRecebida:
          arquivo = "arquivos/lero.yaml"
          d1 = yaml_loader(arquivo)
          frase = random.choice(d1['lero_lero']['lero01'])+random.choice(d1['lero_lero']['lero02'])+random.choice(d1['lero_lero']['lero03'])+random.choice(d1['lero_lero']['lero04'])
          context.bot.sendMessage(chat_id=update.message.chat_id, text=frase)
          context.bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

        if "e ae" in MsgRecebida or "tudo bem" in MsgRecebida:
            if chat_id == lauro:
                context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                context.bot.sendMessage(chat_id=chat_id, text="Oi lauro, voce falou? "+first_name)
            else:
                arquivo = "arquivos/frases_amor.yaml"
                d1 = yaml_loader(arquivo)
                d2 = json.dumps(d1)
                d3 = json.loads(d2)
                i = random.randint(0,len(d3['frases']))
                context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
                context.bot.sendMessage(chat_id=chat_id, text=random.choice(d3['frases'])+' '+first_name)

        logger.info("USER: {} USERNAME: {} ID: {} TYPE: echo mensagem MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))


def hoymiles_lauro(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        usuario = ''
        senha = ''
        link = ''
        EnergyToday,EnergyThisMonth = hoymiles(link,usuario,senha)
        text = 'Total de energia de hoje: '+EnergyToday+' Total de energia do mes: '+EnergyThisMonth
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        context.bot.sendMessage(chat_id=chat_id, text=text)
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: teste MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def hoymiles_rafael(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        cfg = yaml.safe_load(open(.credential.yaml))
        usuario = cfg['username']
        senha = cfg['senha']
        link = cfg['link']
        EnergyToday,EnergyThisMonth = hoymiles(link,usuario,senha)
        text = 'Total de energia de hoje: '+EnergyToday+' Total de energia do mes: '+EnergyThisMonth
        context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        context.bot.sendMessage(chat_id=chat_id, text=text)
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: teste MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def hoymiles_giba(update, context):
    user_id,first_name,username,chat_id,text,is_bot = check_variavel(update, context)
    validacao = valida_usuario(update, context, chat_id)
    if validacao == 0:
        if chat_id in administradores:
            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            context.bot.sendMessage(chat_id=chat_id, text="*bold* _italic_ `fixed width font` [link](http://google.com).", parse_mode=telegram.ParseMode.MARKDOWN)
        else:
            context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
            context.bot.sendMessage(chat_id=chat_id, text="oi? o que queres?")
        logger.info("USER: {} USERNAME: {} ID: {} TYPE: teste MESSAGE: {} BOT: {}".format(first_name,username,chat_id,text,is_bot))

def main():
    #@laurobmb
    TOKEN='1146948596:AAFxLoSSPIVOqZo-39o6UiLK9sMGlmWu4TA'
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))

#### Comandos COMUNS
    updater.dispatcher.add_handler(CommandHandler('help', help))    #OK
    updater.dispatcher.add_handler(CommandHandler('frases',frases)) #OK
    updater.dispatcher.add_handler(CommandHandler('frases_amor',frases_amor))   #OK
    updater.dispatcher.add_handler(CommandHandler('bop',bop))   #OK
    updater.dispatcher.add_handler(CommandHandler('hoymiles_giba',hoymiles_giba))   #OK
    updater.dispatcher.add_handler(CommandHandler('hoymiles_rafael',hoymiles_rafael))   #OK
    updater.dispatcher.add_handler(CommandHandler('hoymiles_lauro',hoymiles_lauro))   #OK
#### Conmandos de RESPOSTAS
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
