from scraper.browser import setup_driver, get_page 
from scraper.parser import get_page_count, get_listings, parse_listings
from scraper.urls import make_page_urls, get_freguesia
#from scraper.db import insert_listings

import time

#to do make it support loaded page
def scrape_url(driver, url, retries=3):
    for attempt in range(retries):
        try:
            raw_html = get_page(driver, url)
            return get_listings(raw_html)
        except ValueError:
            time.sleep(3 * (1+attempt))
    return None


def process(bs4_listings, url):
    if bs4_listings:
        listings_list = parse_listings(bs4_listings, get_freguesia(url))
        #write to db success L2 and raw

    else:
        print("ss")
        #write failure


def main():
    url = "https://www.idealista.pt/arrendar-casas/lisboa/ajuda/"
    
    driver = setup_driver()
    failed_urls = []

    #discovery
    page = get_page(driver, url)
    page_count = get_page_count(page)
    urls = make_page_urls(page_count, url)

    #scraping
    listings = scrape_url(#pass page here)
    process(listings, url) #processing first url straight away to not refetch

    for url in urls[1:]:
        listings = scrape_url(driver,url)
        process(listings, url)

if __name__ == "__main__":
    main()

