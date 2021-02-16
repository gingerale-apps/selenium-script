"""
Script for creating lots in the auction https://newauction.com.ua.
Python 3.7 and selenium are used.

DB MySQL contains two tables:
- newauction: lots information
    (columns: id, title, category, subcategory, image, action - selected/not selected lot for creation),
- start_date: auction start time (columns: id, year, month, day, hour, minute).

Actions:
1. Connect to DB:
    - takes information about selected lots,
    - takes auction start time.
2. Login on https://newauction.com.ua.
3. Create lots. Auction start time increases by one minute from second lot.
4. Create file with links on created lots.
"""

from tempfile import NamedTemporaryFile
from datetime import datetime, timedelta
import os
import requests
import MySQLdb
import MySQLdb.cursors
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from constants import *
from errors import DatabaseError, CreationError
from locators import LoginPageLocators, NewOfferPageLocators


def auction():
    """
    Main function, controls database connection and webdriver, collect information
    from databases, create new offers, create file with urls of created lots.

    :return: None
    """
    database = MySQLdb.connect(
        host=HOST, user=USER_DB, passwd=PWD_DB, db=NAME_DB, cursorclass=MySQLdb.cursors.DictCursor, charset=CHARSET)
    cursor = database.cursor()

    convert_date = get_date_from_db(cursor)
    lots = get_lots_from_db(cursor)
    driver = login()

    lots_url = []
    for index, lot in enumerate(lots):
        lot_id = lot['id']
        lots_url.append(create_new_offer(driver, lot, convert_date + timedelta(minutes=index)))
        print(f'Lot number {index + 1} (database id={lot_id}) was successfully created')

        change_lot_status_in_db(database, cursor, lot_id)

    url_file_path = os.path.join(os.getcwd(), 'lots_url.txt')
    with open(url_file_path, 'w') as url_file:
        for url in lots_url:
            url_file.write(url + '\n')

    print(f'File with URLs was successfully created {url_file_path}')

    database.close()
    driver.close()


def get_date_from_db(cursor):
    """Get auction start time from database and convert it to the view - 2021-05-12 23:58:00.

    :param cursor: database cursor
    :type cursor: <class 'MySQLdb.cursors.DictCursor'>

    :raises DatabaseError: if auction start time has been passed

    :rtype: <class 'datetime.datetime'>
    :return: auction start time, e.g. 2021-05-12 23:58:00
    """
    cursor.execute("""SELECT * FROM start_date WHERE id=1""")
    date = cursor.fetchone()
    convert_date = datetime(date['year'], date['month'], date['day'], date['hour'], date['minute'])

    if convert_date < datetime.now():
        raise DatabaseError('Auction start time has been passed!')

    print(f'Start date is {convert_date}')
    return convert_date


def get_lots_from_db(cursor):
    """Get information about selected lots from database.

    :param cursor: database cursor
    :type cursor: <class 'MySQLdb.cursors.DictCursor'>

    :raises DatabaseError: if there are no selected lots for creation in database

    :rtype: tuple of dicts
    :return: lots, e.g. ({'id': 5, 'title': '', 'category': '', 'subcategory': '', 'image': '5.jpg', 'action': 1},
                        {...}, ...)
    """
    cursor.execute("""SELECT * FROM newauction WHERE action=1""")
    lots = cursor.fetchall()

    if not lots:
        raise DatabaseError('You have no selected lots for creation!')

    print(f'{len(lots)} lots to go.')
    return lots


def login():
    """Starts selenium webdriver in Chrome, login on website and return webdriver.

    :rtype: <class 'selenium.webdriver.chrome.webdriver.WebDriver'>
    :return: webdriver selenium
    """
    driver = webdriver.Chrome(os.getcwd() + '/chromedriver')
    driver.get('https://newauction.com.ua/auth')
    driver.find_element(*LoginPageLocators.LOGIN).send_keys(USER_AU)
    driver.find_element(*LoginPageLocators.PASSWD).send_keys(PWD_AU)
    driver.find_element(*LoginPageLocators.AUTH_BUTTON).click()

    print('You are logged on https://newauction.com.ua')
    return driver


def create_new_offer(driver, lot, start_date):
    """Open page for creation new offer, fill the form fields and return new lot url.

    :param driver: webdriver selenium
    :type driver: <class 'selenium.webdriver.chrome.webdriver.WebDriver'>

    :param lot: lot info, e.g. {'id': 5, 'title': '', 'category': '', 'subcategory': '', 'image': '', 'action': 1}
    :type lot: dict

    :param start_date: auction start time, e.g. 2021-05-12 23:58:00
    :type start_date: <class 'datetime.datetime'>

    :raises CreationError: if there is no success text after clicking the create button

    :rtype: str
    :return: new lot url
    """
    driver.get('https://newauction.com.ua/new_offer')

    wait_element(driver, NewOfferPageLocators.TITLE).send_keys(lot['title'].strip())
    wait_element(driver, NewOfferPageLocators.CATEGORY_ANTIQUES_COLLECTIBLES).click()
    wait_element(driver, NewOfferPageLocators.CATEGORY_PHILATELY).click()
    wait_element(driver, (By.XPATH, f".//ul[@id='sellFormSelectThird']/li[text()='{lot['category'].strip()}']")).click()

    if lot['subcategory']:
        wait_element(driver,
                     (By.XPATH, f".//ul[@id='sellFormSelectThird']/li[text()='{lot['subcategory'].strip()}']")).click()

    wait_element(driver, NewOfferPageLocators.STAMPS_TYPE_MNH).click()

    with NamedTemporaryFile(suffix='.jpg', prefix='image_', dir=os.getcwd()) as img:
        img.write(requests.get(REMOTE_PATH + lot['image'].strip()).content)

        driver.find_element(*NewOfferPageLocators.IMAGE_BUTTON).send_keys(img.name)
        wait_element(driver, NewOfferPageLocators.UPLOADED_IMAGE, method=ec.element_to_be_clickable)

    driver.find_element(*NewOfferPageLocators.SALE_TYPE_SIMPLE_AUC).click()
    driver.find_element(*NewOfferPageLocators.QUANTITY).send_keys(Keys.BACKSPACE, 1)
    wait_element(driver, NewOfferPageLocators.STARTING_PRICE).send_keys(Keys.BACKSPACE, 1)
    driver.find_element(*NewOfferPageLocators.DURATION_7_DAYS).click()
    driver.find_element(*NewOfferPageLocators.RELISTING_MODE_OFF).click()
    driver.find_element(*NewOfferPageLocators.DELIVERY_PAY_BUYER).click()
    driver.find_element(*NewOfferPageLocators.REGION_KH).click()
    driver.find_element(*NewOfferPageLocators.LOCATION).send_keys('Харьков')
    driver.find_element(*NewOfferPageLocators.TRANSACTION_TYPE_PREPAYMENT).click()
    driver.find_element(*NewOfferPageLocators.PAYMENT_METHOD_BANK_TRANSFER).click()
    driver.find_element(*NewOfferPageLocators.DELIVERY_METHOD_UKR_POSTOFFICE).click()

    wait_element(driver, NewOfferPageLocators.DELIVERY_IN_CITY_PRICE).send_keys(18)
    driver.find_element(*NewOfferPageLocators.DELIVERY_IN_COUNTRY_PRICE).send_keys(18)
    driver.find_element(*NewOfferPageLocators.DELIVERY_IN_WORLD_PRICE).send_keys(120)

    driver.find_element(*NewOfferPageLocators.AUC_START_IN_FUTURE).click()
    wait_element(driver, NewOfferPageLocators.CLOSE_CALENDAR_BUTTON).click()
    driver.execute_script("$('#future_start').attr('type', 'text');")
    driver.execute_script("$('#future_start').val('');")
    wait_element(driver, NewOfferPageLocators.AUC_START_DATA).send_keys(start_date.strftime("%d.%m.%Y %H:%M:%S"))

    driver.switch_to.frame(driver.find_element(*NewOfferPageLocators.DESCRIPTION_IFRAME))
    driver.find_element(*NewOfferPageLocators.DESCRIPTION_IFRAME_CURSOR).click()
    driver.find_element(*NewOfferPageLocators.DESCRIPTION_IFRAME_CURSOR).send_keys(
        'MNH \nОПЛАТА НА КАРТУ ПРИВАТА \nЗАКАЗНОЕ ПИСЬМО ПО УКРАИНЕ ПО ТАРИФУ УКРПОЧТЫ')
    driver.switch_to.default_content()

    driver.find_element(*NewOfferPageLocators.CREATION_BUTTON).click()
    wait_element(driver, NewOfferPageLocators.CREATION_STATUS)

    try:
        WebDriverWait(driver, 15).until(ec.text_to_be_present_in_element(
            NewOfferPageLocators.CREATION_STATUS, 'Поздравляем! Ваш лот создан и будет активирован:'))
    except TimeoutException:
        raise CreationError('Lot not created.')

    return driver.find_element(*NewOfferPageLocators.NEW_LOT_URL).text


def wait_element(driver, locator, method=ec.visibility_of_element_located, wait_time=15):
    """Changes parameters wait of element.

    :param driver: webdriver selenium
    :type driver: <class 'selenium.webdriver.chrome.webdriver.WebDriver'>

    :param locator: xpath locator for element
    :type locator: tuple

    :param method: method from selenium expected_condition.py will used for checking element
    :type method: <class 'type'>

    :param wait_time: how many seconds we will wait
    :type wait_time: int

    :rtype: bool|exception
    :return: True|TimeoutException
    """
    return WebDriverWait(driver, wait_time).until(method(locator), message=f"Can't find element: {locator}")


def change_lot_status_in_db(database, cursor, lot_id):
    """Change lot action in DB from 1 to 0 after creation.

    :param db: database connection
    :type db: object <class 'MySQLdb.connections.Connection'>

    :param cursor: database cursor
    :type cursor: <class 'MySQLdb.cursors.DictCursor'>

    :param lot_id: lot id in database
    :type lot_id: int

    :return: None
    """
    cursor.execute(f"""UPDATE newauction SET action=0 WHERE id={lot_id}""")
    database.commit()

    print(f'Database id={lot_id} column "action" was updated from 1 to 0.')


if __name__ == '__main__':
    auction()
