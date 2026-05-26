from time import sleep


proxy = f"http://{PROXY_USERNAME}:{PASSWORD}@{DOMAIN_NAME}:{PORT}"

import json, tempfile
from urllib.parse import urlparse
import undetected_chromedriver as uc

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
options.add_argument("--blink-settings=imagesEnabled=false")  # save on bandwidth
driver = uc.Chrome(options=options, version_main=147)
sleep(5)

driver.get("https://www.idealista.pt/comprar-casas/lisboa/ajuda/")
sleep(10)

# driver.get("https://www.idealista.pt/comprar-casas/lisboa/ajuda/pagina-2")


# sleep(10)
