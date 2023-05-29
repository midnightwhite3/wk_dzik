from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions as exc

from pyautogui import press
from time import sleep
import sys

import settings


# TODO: implement webdriver wait to all funcs (generic implementation), with timeout included
# TODO: if the price ios too low, chart layout is different /
# check for the price in the chart to be high enough, add more items/more valuable item

# set up the driver
options = Options()
# options.headless = True
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), \
                           options=options)

action = ActionChains(driver)
wait = WebDriverWait(driver, 10)


def timeout(s=settings.TIMEOUT_s, n=settings.TIMEOUT_n):
    """Decorator calls target function TIMEOUT_n-1 times then exits the program due
    to timeout limit. Timeout limit = (n-1)*s.

    PARAMETERS:
    s = seconds to sleep between iterations.
    n = number of iterations.
    """
    def decorator(func):
        def inner(*args, **kwargs):
            for i in range(n):
                if i == n: sys.exit("Timeout. Exiting.")
                try:
                    func(*args, **kwargs)
                except Exception as error:
                    sleep(s)
                    print(error)
                    continue
                else:
                    break
        return inner
    return decorator


def main_page():
    """Go to the main page (wkdzik.pl)."""
    driver.get('https://wkdzik.pl')


@timeout()
def accept_cookies():
    """Cookies pop up when main page loads, blocking all other actions. Accept it."""
    agree = driver.find_element(By.CSS_SELECTOR, 'button.btn-red:nth-child(1)')
    agree.click()


@timeout()
def login(mail=settings.CREDENTIALS['EMAIL'], \
          password=settings.CREDENTIALS['PASSWORD']):
    """Login to your account. Credentials are set in settings.py."""
    driver.find_element(By.CSS_SELECTOR, 'a.login').click()    # login
    driver.find_element(By.NAME, 'mail').send_keys(mail)
    driver.find_element(By.NAME, 'pass').send_keys(password)
    press('enter')


def go_to_chart():
    """Goes to the basket page URL."""
    driver.get("https://wkdzik.pl/basket")
    # driver.find_element(By.CLASS_NAME, 'count').click()


def read_codes(codes_path=settings.CODES_PATH_ALL) -> list:
    """Opens codes_path.txt file and returns a complete list of discount codes.
    
    codes_path - path to txt file.
    """
    # codes = [line.rstrip() for line in open(codes_path, 'r')] # is it closing the file?
    with open(codes_path, 'r') as f:
        codes = [line.rstrip() for line in f]
    return codes


@timeout()
def enter_code(code):
    """Looks for discount code field and puts the code in."""
    # wait.until(EC.presence_of_element_located((By.NAME, "Wpisz kod rabatowy")))
    input = driver.find_element(By.NAME, "Wpisz kod rabatowy")
    driver.find_element(By.CLASS_NAME, 'el-input-group__append').click() # neccesary to be able to send keys
    input.send_keys(code)


@timeout()
def activate_code():
    """Activates sent discount code. Clicks on activate button."""
    driver.find_element(By.CLASS_NAME, "el-input-group__append").click()

timeout()
def remove_code():
    """ *** code removes itself after activation try.
    Removes previously sent discount code, making room to try another.
    Clicks on remove button.
    """
    driver.find_element(By.XPATH, '//*[@id="app"]/form/div[3]/div[2]/div/div/button/i').click()
    # el.click()


def empty_chart() -> bool:
    """Boolean return wheter chart has an item or not."""
    f = driver.find_element(By.CLASS_NAME, "alert-info").text
    if f.lower() == "twój koszyk jest pusty.":
        return True
    else:
        return False


@timeout()
def pick_category(id='headlink25'):
    """Picks one of the shop's categories. Accesories by default,
    since they dont have sizes or wariants to pick.
    
    id - string representation of category id written in html.
    """
    driver.find_element(By.ID, id).click()


@timeout()
def pick_item():
    """Picks an item from previously selected category."""
    items = driver.find_elements(By.CLASS_NAME, 'products')
    items[0].click()


@timeout()
def close_modal():
    """Closes order confirmation pop up (modal)."""
    driver.find_element(By.CLASS_NAME, 'modal-close').click()


@timeout()
def add_to_chart():
    """Adds item to chart."""
    try:
        driver.find_element(By.LINK_TEXT, 'Do koszyka').click()
    except exc.NoSuchElementException:
        driver.find_element(By.CLASS_NAME, 'addtobasket').click()


@timeout()
def proceed_to_chart():
    pass


@timeout()
def is_code_input() -> bool:
    if "Aktywuj" in driver.page_source:
        return True
    return False


@timeout()
def code_input(code: str):
    element = driver.find_element(By.NAME, "Wpisz kod rabatowy")
    element.send_keys(code)


@timeout()
def show_code_input():
    element = driver.find_element(By.CLASS_NAME, "checkbox-wrap")
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "checkbox-wrap")))
    element.click()


# @timeout()
# def try_code(code: str):
#     input = driver.find_element(By.NAME, "promocode")
#     wait.until(EC.visibility_of_element_located((By.NAME, "promocode")))
#     input.send_keys(str(code))
#     confirm = driver.find_element(By.XPATH, '//*[@id="cart-options"]/div[3]/div[1]/div/span[4]/button')
#     confirm.click()


def try_code(code):
    enter_code(code)
    activate_code()


def is_valid():
    # if 
    pass

# zmienic rabat % str na int zeby uzytkownik mogl wybrac od jakiego progu rabaty chcce zapisywac?
# sprawdzic czy szybciej poszukac w page.source % rabatu czy przekalkulowac
def try_codes(discount=15, print_info=True, save_to_file=False):
    codes = read_codes(settings.CODES_PATH_ALL)
    coupon15 = []
    coupon20 = []
    for code in codes:
        try_code(code)
        # if f'Rabat {str(discount)}%' in driver.page_source:
        if 'Rabat 15%' in driver.page_source:
            if print_info:
                print(f'Znaleziono kod o wartości 15%! {code}')
            coupon15.append(code)
            remove_code()
        elif 'Rabat 20%' in driver.page_source:
            if print_info:
                print(f'Znaleziono kod o wartości 20%! {code}')
            coupon20.append(code)
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
    pick_category()
    pick_item()
    add_to_chart()
    close_modal()
go_to_chart()
enter_code("78ed2233cb")
activate_code()
remove_code()
# try_codes()

# try_codes()
