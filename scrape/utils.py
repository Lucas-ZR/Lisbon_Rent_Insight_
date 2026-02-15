import undetected_chromedriver as uc
from bs4 import BeautifulSoup

import random
from time import sleep
from math import ceil


def get_page_count(raw_html):
    #input raw_html, return int with number of pages containing listings
    
    soup = BeautifulSoup(raw_html, "html.parser")
    elements = soup.find_all(class_="breadcrumb-navigation-element-info")
    listing_count = min([int(el.text.replace(".","")) for el in elements])
    pages = ceil(listing_count / 30)
    return pages


def make_page_urls(pages, freguesia_url):
    #input, number of pages containing litings and full url -> f"{BASE_URL}/{LISBON_MUNICIPALITY}/{LISBON_FREGUESUAS[0]}/" returns list of urls
    urls = [freguesia_url]
    for page in range(2, pages+1):
        page_url = f"{freguesia_url}pagina-{page}"
        urls.append(page_url)   

    return urls


def get_listings(raw_html):
    #input raw_html, return BeautifulSoup object with all the items
    soup = BeautifulSoup(raw_html, "html.parser")
    container = soup.find(class_="items-container")
    return container


def get_all_listings(urls,driver):
    listings_list = []
    for url in urls:

        #if first url, it is already loaded in the driver no need to load again, first url always ends on literal /
        if url[-1] != "/":
            driver.get(url)
            sleep(random.randint(7,15))

        raw_html = driver.page_source

        listings = get_listings(raw_html)   

        listings_list.append(listings)  
        
          


def filter_html(soup):
    articles = soup.find_all("article", attrs={"data-element-id": True})

    listings = []

    for art in articles:
        
        announcement_id = art["data-element-id"]
        announcement_price = art.find("span", class_="item-price h2-simulated").get_text(strip=True)
        announcement_title = art.find("a", class_="item-link")["title"]
        announcement_extra = art.find("div", class_="item-detail-char").find_all("span", class_="item-detail")

        listings.append({
            "id" : announcement_id,
            "price" : announcement_price,
            "title" : announcement_title,
            "extra" : announcement_extra
            })
    
    return listings
