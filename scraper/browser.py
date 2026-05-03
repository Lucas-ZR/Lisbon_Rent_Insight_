import undetected_chromedriver as uc
import time


def setup_driver():
    return uc.Chrome(version_main=147)


def get_page(driver, url):
    driver.get(url)
    time.sleep(5)  # wait for JS to render
    return driver.page_source
