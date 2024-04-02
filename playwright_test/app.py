from playwright.sync_api import sync_playwright
from time import sleep
import os

def main(USER,SENHA):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto('https://global.hoymiles.com/platform/login')
        
        page.locator('//*[@id="name"]').fill(USER)
        page.locator('//*[@id="password"]').fill(SENHA)
        sleep(2)
        page.locator(".submit_button").click()
        sleep(15)
        page.screenshot(path='screenshot.png')

        energy_today_selector = 'li.sx-white-space:nth-child(1) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(energy_today_selector);
        energy_today_selector_texto = page.inner_text(energy_today_selector)
        print('Energy Today:', energy_today_selector_texto,'Wh')
        sleep(2)

        energy_this_month_selector = 'li.sx-white-space:nth-child(2) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(energy_this_month_selector);
        energy_this_month_selector_texto = page.inner_text(energy_this_month_selector)
        print('Energy This Month:', energy_this_month_selector_texto,'Wh')
        sleep(2)

        energy_this_year_selector = 'li.sx-white-space:nth-child(3) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(energy_this_year_selector);
        energy_this_year_selector_texto = page.inner_text(energy_this_year_selector)
        print('Energy This Year:', energy_this_year_selector_texto,'MWh')
        sleep(2)

        lifetime_energy_selector = 'li.sx-white-space:nth-child(4) > span:nth-child(3) > b:nth-child(1)'
        page.wait_for_selector(lifetime_energy_selector);
        lifetime_energy_selector_texto = page.inner_text(lifetime_energy_selector)
        print('Lifetime Energy:', lifetime_energy_selector_texto,'MWh')
        sleep(2)

        browser.close()
        return energy_today_selector_texto,energy_this_month_selector_texto,energy_this_year_selector_texto,lifetime_energy_selector_texto


if __name__ == "__main__":

    hoymiles_user = os.environ['USUARIO']
    hoymiles_pass = os.environ['SENHA']

    energy_today,energy_this_month,energy_this_year,lifetime_energy = main(hoymiles_user,hoymiles_pass)
    print(energy_today,energy_this_month,energy_this_year,lifetime_energy)


        

