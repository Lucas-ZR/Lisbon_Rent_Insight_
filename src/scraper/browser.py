import undetected_chromedriver as uc
import time
import random
import json, tempfile
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def setup_driver(
    driver_version=None,
    use_proxy=None,
    PROXY_USERNAME=None,
    PASSWORD=None,
    DOMAIN_NAME=None,
    PORT=None,
):
    if use_proxy:
        proxy = f"http://{PROXY_USERNAME}:{PASSWORD}@{DOMAIN_NAME}:{PORT}"

        p = urlparse(proxy)

        ext = tempfile.mkdtemp()
        json.dump(
            {
                "name": "p",
                "version": "1",
                "manifest_version": 3,
                "permissions": ["proxy", "webRequest", "webRequestAuthProvider"],
                "host_permissions": ["<all_urls>"],
                "background": {"service_worker": "bg.js"},
            },
            open(f"{ext}/manifest.json", "w"),
        )
        open(f"{ext}/bg.js", "w").write(f"""
        chrome.proxy.settings.set({{value:{{mode:"fixed_servers",rules:{{singleProxy:{{scheme:"http",host:"{p.hostname}",port:{p.port}}}}}}},scope:"regular"}});
        chrome.webRequest.onAuthRequired.addListener(
        () => ({{authCredentials:{{username:"{p.username}",password:"{p.password}"}}}}),
        {{urls:["<all_urls>"]}}, ["blocking"]);
        """)

        options = uc.ChromeOptions()
        options.add_argument(f"--load-extension={ext}")
        options.add_argument(
            "--blink-settings=imagesEnabled=false"
        )  # save on bandwidth
        driver = uc.Chrome(options=options, version_main=driver_version)
    else:
        driver = uc.Chrome(version_main=driver_version)
    return driver


def get_page(driver, url):
    driver.get(url)
    time.sleep(5)  # wait for JS to render
    return driver.page_source


def smart_get_page(driver, url, wait=None, timeout=10):
    driver.get(url)
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "article[data-element-id]")
        )
    )
    page = driver.page_source
    driver.execute_cdp_cmd("Page.stopLoading", {})

    if wait:
        time.sleep(random.uniform(5, 20))
    return page
