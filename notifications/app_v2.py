import os
import sys
import logging
import requests
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# --- Constantes ---
HOYMILES_LOGIN_URL = 'https://global.hoymiles.com/platform/login'
TELEGRAM_API_URL = "https://api.telegram.org/bot"
# Seletores de dados
ENERGY_TODAY_SELECTOR = 'p.energy:nth-child(2) > span:nth-child(1)'
ENERGY_MONTH_SELECTOR = '.stats > div:nth-child(1) > p:nth-child(2) > span:nth-child(1)'
ENERGY_YEAR_SELECTOR = 'div.item:nth-child(2) > p:nth-child(2) > span:nth-child(1)'
LIFETIME_ENERGY_SELECTOR = 'div.item:nth-child(3) > p:nth-child(2) > span:nth-child(1)'
# Seletores das seções que queremos fotografar
OVERVIEW_SELECTOR = '#overview'
CHART_SELECTOR = '#history_chart'
# Seletores do resumo (tooltip) - Lembre de ajustar se necessário
POWER_CIRCLE_SELECTOR = 'div.ant-col-12 > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)'
SUMMARY_TOOLTIP_SELECTOR = '.ant-popover-inner-content'

# --- Configuração do Logging ---
logging.basicConfig(format='%(asctime)s: %(name)s: %(levelname)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logger = logging.getLogger('hoymiles_bot')


# A assinatura da função agora inclui o caminho para o screenshot do gráfico
def get_hoymiles_data(user, password, full_screenshot_path, overview_screenshot_path, chart_screenshot_path, summary_screenshot_path):
    logger.info("Iniciando coleta de dados da Hoymiles.")
    with sync_playwright() as p:
        # Recomendo deixar headless=True para rodar no servidor, e False apenas para depurar
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(HOYMILES_LOGIN_URL, timeout=60000)
            
            # --- SELETORES CORRIGIDOS ---
            logger.info("Preenchendo formulário de login...")
            page.locator('input[id="basic_username"]').fill(user)
            page.locator('input[id="basic_password"]').fill(password)
            page.locator('button[type="submit"]').click()

            logger.info("Login realizado. Aguardando dashboard...")
            page.wait_for_selector(ENERGY_TODAY_SELECTOR, timeout=90000)

            start_time = time.time()
            while True:
                today_energy_text = page.locator(ENERGY_TODAY_SELECTOR).inner_text()
                if today_energy_text.strip() not in ("0", "0.00"):
                    logger.info(f"Valor de hoje atualizado para: {today_energy_text}.")
                    break
                if time.time() - start_time > 90:
                    logger.warning("Timeout: Valor de hoje permaneceu '0'.")
                    break
                time.sleep(1)

            logger.info("Aguardando 10 segundos para a estabilização final da página...")
            time.sleep(10)

            logger.info("Capturando screenshots e dados finais.")

            # Captura da seção "Overview"
            try:
                logger.info("Localizando e capturando a seção 'Overview'...")
                page.locator(OVERVIEW_SELECTOR).screenshot(path=overview_screenshot_path)
                logger.info(f"Screenshot da seção 'Overview' salvo em: {overview_screenshot_path}")
            except Exception as e:
                logger.error(f"Não foi possível capturar a seção 'Overview': {e}")
                overview_screenshot_path = None

            # Captura do gráfico
            try:
                logger.info("Localizando e capturando o gráfico de geração...")
                page.locator(CHART_SELECTOR).screenshot(path=chart_screenshot_path)
                logger.info(f"Screenshot do gráfico salvo em: {chart_screenshot_path}")
            except Exception as e:
                logger.error(f"Não foi possível capturar o gráfico: {e}")
                chart_screenshot_path = None

            # Captura do resumo (tooltip)
            try:
                logger.info("Ativando e capturando o resumo (tooltip)...")
                page.locator(POWER_CIRCLE_SELECTOR).hover()
                time.sleep(1)
                page.locator(SUMMARY_TOOLTIP_SELECTOR).screenshot(path=summary_screenshot_path)
                logger.info(f"Screenshot do resumo salvo em: {summary_screenshot_path}")
            except Exception as e:
                logger.error(f"Não foi possível capturar o resumo (tooltip): {e}")
                summary_screenshot_path = None

            # Captura da página inteira
            page.screenshot(path=full_screenshot_path, full_page=True)
            logger.info(f"Screenshot da página inteira salvo em: {full_screenshot_path}")

            data = { "today": page.locator(ENERGY_TODAY_SELECTOR).inner_text(), "month": page.locator(ENERGY_MONTH_SELECTOR).inner_text(), "year": page.locator(ENERGY_YEAR_SELECTOR).inner_text(), "lifetime": page.locator(LIFETIME_ENERGY_SELECTOR).inner_text() }
            logger.info(f"Dados extraídos com sucesso: {data}")

            return data, full_screenshot_path, overview_screenshot_path, chart_screenshot_path, summary_screenshot_path
        except Exception as e:
            logger.error(f"Erro inesperado na coleta: {e}")
            caminho_erro = full_screenshot_path.parent / f"erro_geral_{user}.png"
            page.screenshot(path=caminho_erro, full_page=True)
            return None, None, None, None, None
        finally:
            browser.close()


def send_telegram_media_group(token, chat_id, photo_paths, caption=None):
    # Sem alterações
    logger.info(f"Enviando grupo de {len(photo_paths)} mídias para o Telegram...")
    url = f"{TELEGRAM_API_URL}{token}/sendMediaGroup"
    media, files = [], {}
    valid_photo_paths = [path for path in photo_paths if path and Path(path).exists()]
    if not valid_photo_paths:
        logger.error("Nenhuma imagem válida encontrada para enviar.")
        return
    for i, photo_path in enumerate(valid_photo_paths):
        attach_name = f"photo{i}"
        media_item = {'type': 'photo', 'media': f'attach://{attach_name}'}
        if i == 0 and caption:
            media_item['caption'] = caption
        media.append(media_item)
        files[attach_name] = open(photo_path, 'rb')
    try:
        response = requests.post(url, data={'chat_id': chat_id, 'media': json.dumps(media)}, files=files, timeout=45)
        response.raise_for_status()
        logger.info("Grupo de mídias enviado com sucesso.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao enviar grupo de mídias para o Telegram: {e}")
        logger.error(f"Resposta da API: {response.text if 'response' in locals() else 'N/A'}")
    finally:
        for f in files.values():
            f.close()


def get_local_data(status, url):
    # Sem alterações
    if not status: return 0.0
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return float(response.json()["EnergyYesterday"]["Today"])
    except Exception: return 0.0


def main():
    # Sem alterações
    hoymiles_user = os.environ.get('HOYMILES_USER')
    hoymiles_pass = os.environ.get('HOYMILES_PASS')
    bot_token = os.environ.get('TELEGRAM_TOKEN')
    bot_chatID = os.environ.get('TELEGRAM_CHAT_ID')
    status_coleta_local = os.environ.get('STATUS_COLETA_LOCAL', 'false').lower() == 'true'
    url_coleta_local = os.environ.get('URL_COLETA_LOCAL', 'http://192.168.0.107/cm?cmnd=energyyesterday')

    if not all([hoymiles_user, hoymiles_pass, bot_token, bot_chatID]):
        logger.critical("Variáveis de ambiente essenciais não definidas!")
        sys.exit(1)

    photo_dir = Path.cwd() / "photos"
    photo_dir.mkdir(exist_ok=True)
    full_screenshot_path = photo_dir / f"full_screenshot_{hoymiles_user}.png"
    overview_screenshot_path = photo_dir / f"overview_screenshot_{hoymiles_user}.png"
    chart_screenshot_path = photo_dir / f"chart_screenshot_{hoymiles_user}.png"
    summary_screenshot_path = photo_dir / f"summary_screenshot_{hoymiles_user}.png"

    hoymiles_data, captured_full, captured_overview, captured_chart, captured_summary = get_hoymiles_data(hoymiles_user, hoymiles_pass, full_screenshot_path, overview_screenshot_path, chart_screenshot_path, summary_screenshot_path)

    if not hoymiles_data:
        logger.error("Não foi possível obter dados da Hoymiles. Abortando.")
        sys.exit(1)

    coleta_local_wh = get_local_data(status_coleta_local, url_coleta_local)

    try:
        coleta_total_hoje_wh = float(hoymiles_data['today']) + coleta_local_wh
    except (ValueError, TypeError):
        coleta_total_hoje_wh = coleta_local_wh

    mensagem = (
        f"☀️ Relatório Diário - Usina {hoymiles_user} ☀️\n\n"
        f"⚡ Hoje: {hoymiles_data['today']} kWh\n"
        f"📅 Este Mês: {hoymiles_data['month']} kWh\n"
        f"🗓️ Este Ano: {hoymiles_data['year']} MWh\n"
        f"🗓️ Total do sistema: {hoymiles_data['lifetime']} MWh\n"
        f"🔌 Coleta Local: {coleta_local_wh:.2f} Wh\n"
        f"----------------------------------\n"
        f"📊 Total de hoje: {coleta_total_hoje_wh:.2f} Wh"
    )

    caminhos_das_fotos = [captured_full, captured_overview, captured_chart, captured_summary]
    send_telegram_media_group(bot_token, bot_chatID, caminhos_das_fotos, caption=mensagem)


if __name__ == "__main__":
    logger.info("<<<<<<<<<<< INICIANDO BOT DE COLETA DE ENERGIA v11.1 (correção de login) >>>>>>>>>>>")
    main()
    logger.info("<<<<<<<<<<< EXECUÇÃO FINALIZADA >>>>>>>>>>>")