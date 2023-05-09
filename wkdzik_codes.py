from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions as exc
from pyautogui import press
from time import sleep

import settings

# set up the driver
options = Options()
# options.headless = True
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), \
                           options=options)

def main_page():
    """Go to the main page (wkdzik.pl)."""
    driver.get('https://wkdzik.pl')


def accept_cookies():
    """Cookies pop up when main page loads, blocking all other actions. Accept it."""
    agree = driver.find_element(By.CSS_SELECTOR, 'button.btn-red:nth-child(1)')
    agree.click()


def login(mail=settings.CREDENTIALS['EMAIL'], \
          password=settings.CREDENTIALS['PASSWORD'], \
          sleep_for=settings.SLEEP_FOR):
    """Login to your account. Credentials are set in settings.py.
    
    sleep_for - change for how many seconds driver stops action.
    """
    driver.find_element(By.CSS_SELECTOR, 'a.login').click()    # login
    driver.find_element(By.NAME, 'mail').send_keys(mail)
    driver.find_element(By.NAME, 'pass').send_keys(password)
    sleep(sleep_for)
    press('enter')
    sleep(sleep_for)


def go_to_chart():
    """Finds the chart element and clicks on it."""
    driver.find_element(By.CLASS_NAME, 'count').click()
    sleep(settings.SLEEP_FOR)


def read_codes(codes_path=settings.CODES_PATH_ALL) -> list:
    """Opens codes_path.txt file and returns a complete list of discount codes.
    
    codes_path - path to txt file.
    """
    # codes = [line.rstrip() for line in open(codes_path, 'r')] # is it closing the file?
    with open(codes_path, 'r') as f:
        codes = [line.rstrip() for line in f]
    return codes


def enter_code(code, find_by=(By.NAME, 'Wpisz kod rabatowy')):
    """Looks for discount code fiels and puts the code in."""
    driver.find_element(find_by).send_keys(code)
    sleep(settings.SLEEP_FOR)


def activate_code(find_by=(By.CLASS_NAME, 'el-input-group__append')):
    """Activates sent discount code. Clicks on activate button."""
    driver.find_element(find_by).click()
    sleep(settings.SLEEP_FOR)


def remove_code(find_by=(By.CLASS_NAME, 'el-icon-delete')):
    """Removes previously sent discount code, making room to try another.
    Clicks on remove button.
    """
    driver.find_element(find_by).click()
    sleep(settings.SLEEP_FOR)


def empty_chart() -> bool:
    """Boolean return wheter chart has an item or not."""
    f = driver.find_element(By.CLASS_NAME, "alert-info").text
    if f.lower() == "twój koszyk jest pusty.":
        return True
    return False


def category(id='headlink25'):
    """Picks one of the shop's categories. Accesories by default,
    since they dont have sizes or wariants to pick.
    
    id - string representation of category id written in html.
    """
    driver.find_element(By.ID, id).click()


def pick_item():
    """Picks an item from previously selected category."""
    items = driver.find_elements(By.CLASS_NAME, 'products')
    items[0].click()


def close_modal():
    driver.find_element(By.CLASS_NAME, 'modal-close').click()


def add_to_chart():
    """Adds item to chart."""
    try:
        driver.find_element(By.LINK_TEXT, 'Do koszyka').click()
    except exc.NoSuchElementException:
        driver.find_element(By.CLASS_NAME, 'addtobasket').click()


def proceed_to_chart():
    pass


# zmienic rabat % str na int zeby uzytkownik mogl wybrac od jakiego progu rabaty chcce zapisywac?
def try_codes(print_info=True, save_to_file=False):
    codes = read_codes(settings.CODES_PATH_ALL)
    coupon15 = []
    coupon20 = []
    for code in codes:
        enter_code()
        activate_code()
        if 'Rabat 15%' in driver.page_source:
            if print_info == True:
                print(f'Znaleziono kod o wartości 15%! {code}')
            coupon15.append(code)
            remove_code()
        elif 'Rabat 20%' in driver.page_source:
            if print_info == True:
                print(f'Znaleziono kod o wartości 20%! {code}')
            coupon20.append(code)
            remove_code()
        else:
            remove_code()
    if coupon15:

        print(f'Znaleziono {len(coupon15)} kuponów o wartości 15%.')
        print(coupon15)
    if coupon20:
        print(f'Znaleziono {len(coupon20)} kuponów o wartości 20%.')
        print(coupon20)

# driver.find_element(By.ID, 'salesmanagoCloseButton').click()

#tests
main_page()
accept_cookies()
login()
go_to_chart()
if empty_chart():
    category()
    pick_item()
    add_to_chart()

# try_codes()

