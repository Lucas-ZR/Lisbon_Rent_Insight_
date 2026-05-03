from bs4 import BeautifulSoup

import random
from math import ceil


def get_page_count(raw_html):
    # input raw_html, return int with number of pages containing listings

    soup = BeautifulSoup(raw_html, "html.parser")
    elements = soup.find_all(class_="breadcrumb-navigation-element-info")
    listing_count = min([int(el.text.replace(".", "")) for el in elements])
    pages = ceil(listing_count / 30)
    return pages


def make_page_urls(pages, freguesia_url):
    # input, number of pages containing litings and full url -> f"{BASE_URL}/{LISBON_MUNICIPALITY}/{LISBON_FREGUESUAS[0]}/" returns list of urls
    urls = [freguesia_url]
    for page in range(2, pages + 1):
        page_url = f"{freguesia_url}pagina-{page}"
        urls.append(page_url)

    return urls


def get_listings(raw_html):

    soup = BeatifulSoup(raw_html, "html.parser")

    has_articles = len(soup.find_all("article", attrs={"data-element-id": True})) > 0
    has_detail = soup.find("span", class_="item-detail") is not None

    if not (has_articles and has_detail):
        raise ValueError("Invalid page)")

    return soup.find(class_="items-container")


def get_listings(raw_html):
    # input raw_html, return BeautifulSoup object with all the items, and scrape_status
    soup = BeautifulSoup(raw_html, "html.parser")
    container = soup.find(class_="items-container")

    validation_status = validate_page(soup)
    return container, validation_status


def _validate_page(soup):
    # every listing is a "data-element-id article" which contains "item-detail class" checking both to determine if valid page
    has_articles = len(soup.find_all("article", attrs={"data-element-id": True})) > 0
    has_detail = soup.find("span", class_="item-detail") is not None
    return has_articles and has_detail


def filter_html(soup, freguesia):
    articles = soup.find_all("article", attrs={"data-element-id": True})

    listings = []

    for art in articles:
        announcement_id = art["data-element-id"]
        announcement_price = art.find(
            "span", class_="item-price h2-simulated"
        ).get_text(strip=True)
        announcement_title = art.find("a", class_="item-link")["title"]
        announcement_extra = [
            span.get_text(strip=True)
            for span in art.find("div", class_="item-detail-char").find_all(
                "span", class_="item-detail"
            )
        ]

        listings.append(
            {
                "id": announcement_id,
                "price": announcement_price,
                "title": announcement_title,
                "extra": announcement_extra,
                "freguesia": freguesia,
            }
        )

    return listings


def get_freguesia(url):
    return url.split("/")[5]
