import undetected_chromedriver as uc
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def setup_driver():
    return uc.Chrome(version_main=147)


def get_page(driver, url):
    driver.get(url)
    time.sleep(5)  # wait for JS to render
    return driver.page_source

def smart_get_page(driver, url, timeout=10):
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "article[data-element-id]")
        )
    )
    page = driver.page_source
    driver.get("about:blank")
    return page