from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from pyautogui import press
from time import sleep

import settings

# set up the driver
options = Options()
# options.headless = True
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), \
                           options=options)

def main_page(https='https://wkdzik.pl'):
    """Go to to main page. Since program is designed to check codes
    for a specific page, it goes to wkdzik.pl by default.
    """
    driver.get(https)


def accept_cookies():
    """Cookies pop up when main page loads, blocking all other actions. Accept it."""
    agree = driver.find_element(By.CSS_SELECTOR, 'button.btn-red:nth-child(1)')
    agree.click()


def login(mail=settings.CREDENTIALS['EMAIL'], \
          password=settings.CREDENTIALS['PASSWORD'], \
          sleep_for=1):
    """Login to your account. Credentials are set in settings.py."""
    driver.find_element(By.CSS_SELECTOR, 'a.login').click()    # login
    driver.find_element(By.NAME, 'mail').send_keys(mail)
    driver.find_element(By.NAME, 'pass').send_keys(password)
    sleep(sleep_for)
    press('enter')
    sleep(sleep_for)


def go_to_chart():
    """Finds the chart element and opens it."""
    chart = driver.find_element(By.CLASS_NAME, 'count')
    chart.click()
    sleep(2)


def get_codes(txt: str):
    """Get current codes from txt file as a list, strip code str from new lines"""
    codes = [line.rstrip() for line in open(txt, 'r')]
    return codes


# major refactor incoming!!
def try_codes():
    codes = get_codes(settings.CODES_TXT)
    coupon15 = []   # list for 15%
    coupon20 = []   # list for 20%
    for code in codes:
        # try every code
        driver.find_element(By.NAME, 'Wpisz kod rabatowy').send_keys(code)
        driver.find_element(By.CLASS_NAME, 'el-input-group__append').click()
        sleep(3)
        # if code gives less than 15%, delete it and continue
        if ('Rabat 10%' or 'Rabat 5%') in driver.page_source:
            driver.find_element(By.CLASS_NAME, 'el-icon-delete').click()
            sleep(1)
        # add 15% code to a list, delete and continue
        elif 'Rabat 15%' in driver.page_source:
            print(f'Znaleziono kod o wartości 15%! {code}')
            coupon15.append(code)
            driver.find_element(By.CLASS_NAME, 'el-icon-delete').click()
            sleep(1)
        # add 20%% code to a list, delete and continue
        elif 'Rabat 20%' in driver.page_source:
            print(f'Znaleziono kod o wartości 20%! {code}')
            coupon20.append(code)
            driver.find_element(By.CLASS_NAME, 'el-icon-delete').click()
            sleep(1)
    if coupon15:
        print(f'Znaleziono {len(coupon15)} kuponów o wartości 15%.')
        print(coupon15)
    if coupon20:
        print(f'Znaleziono {len(coupon20)} kuponów o wartości 20%.')
        print(coupon20)

# driver.find_element(By.ID, 'salesmanagoCloseButton').click()

main_page()
accept_cookies()
login()
go_to_chart()
