"""Locators for newauction pages. Locators of the same page belong to same class."""

from selenium.webdriver.common.by import By


class LoginPageLocators:
    """The class for auth page locators: https://newauction.com.ua/auth ."""
    LOGIN = (By.XPATH, './/input[@name="email_or_login"]')
    PASSWD = (By.XPATH, './/input[@name="password"]')
    AUTH_BUTTON = (By.XPATH, './/input[@id="auth_btn"]')


class NewOfferPageLocators:
    """The class for new offer page locators: https://newauction.com.ua/new_offer ."""
    TITLE = (By.XPATH, './/input[@id="Title"]')

    CATEGORY_ANTIQUES_COLLECTIBLES = (
        By.XPATH, './/ul[@id="sellFormSelectFirst"]/li[text()="Антиквариат и Коллекционирование"]')
    CATEGORY_PHILATELY = (By.XPATH, './/ul[@id="sellFormSelectSecond"]/li[text()="Филателия"]')

    STAMPS_TYPE_MNH = (By.XPATH, './/select[@id="param_2063"]/option[text()="негашеная"]')

    IMAGE_BUTTON = (By.XPATH, ".//input[@type='file']")
    UPLOADED_IMAGE = (By.XPATH, './/li[@class="uploaded_image photo_item" and @data-num="1"]')

    SALE_TYPE_SIMPLE_AUC = (By.XPATH, './/select[@id="SaleType"]/option[text()="Простой аукцион"]')
    QUANTITY = (By.XPATH, './/input[@id="Quantity"]')
    STARTING_PRICE = (By.XPATH, './/input[@id="StartingPrice"]')
    DURATION_7_DAYS = (By.XPATH, './/select[@id="duration"]/option[text()="7"]')
    RELISTING_MODE_OFF = (By.XPATH, './/select[@name="relisting_mode"]/option[text()="не перевыставлять"]')

    DELIVERY_PAY_BUYER = (By.XPATH, './/select[@id="WhoPaysForDelivery"]/option[text()="покупатель"]')
    REGION_KH = (By.XPATH, './/select[@id="Region"]/option[text()="Харьковская"]')
    LOCATION = (By.XPATH, './/input[@id="FreeLocation"]')
    TRANSACTION_TYPE_PREPAYMENT = (By.XPATH, './/input[@id="checkbox_46349334968669_0"]')
    PAYMENT_METHOD_BANK_TRANSFER = (By.XPATH, './/input[@id="checkbox_46349334961738_1"]')
    DELIVERY_METHOD_UKR_POSTOFFICE = (By.XPATH, './/input[@id="checkbox_46349334954144_2"]')
    DELIVERY_IN_CITY_PRICE = (By.XPATH, './/input[@id="deliverymethod_price_2_deliveryincity"]')
    DELIVERY_IN_COUNTRY_PRICE = (By.XPATH, './/input[@id="deliverymethod_price_2_deliveryincountry"]')
    DELIVERY_IN_WORLD_PRICE = (By.XPATH, './/input[@id="deliverymethod_price_2_deliveryinworld"]')

    AUC_START_IN_FUTURE = (By.XPATH, './/input[@name="start" and @value="1"]')
    CLOSE_CALENDAR_BUTTON = (
        By.XPATH, './/button[@class="ui-datepicker-close ui-state-default ui-priority-primary ui-corner-all"]')
    AUC_START_DATA = (By.XPATH, './/input[@id="future_start"]')

    DESCRIPTION_IFRAME = (By.XPATH, './/iframe[@id="offerdesceditarea_ifr"]')
    DESCRIPTION_IFRAME_CURSOR = (By.ID, "tinymce")
    CREATION_BUTTON = (By.XPATH, './/input[@id="submit-btn" and @type="button"]')
    CREATION_STATUS = (By.XPATH, './/div[@class="alert-msg-main text-center"]')
    NEW_LOT_URL = (By.XPATH, './/div[@class="link"]/a')
