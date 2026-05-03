from bs4 import BeautifulSoup

import random
from math import ceil


def get_page_count(raw_html):
    # input raw_html, return int with number of pages containing listings

    soup = BeautifulSoup(raw_html, "html.parser")
    elements = soup.find_all(class_="breadcrumb-navigation-element-info")
    if not elements:
        raise ValueError("No pagination element")

    listing_count = min([int(el.text.replace(".", "")) for el in elements])

    return ceil(listing_count / 30)


def get_listings(raw_html):

    soup = BeautifulSoup(raw_html, "html.parser")

    # every listing is a "data-element-id article" which contains "item-detail class" checking both to determine if valid page
    has_articles = len(soup.find_all("article", attrs={"data-element-id": True})) > 0
    has_detail = soup.find("span", class_="item-detail") is not None

    if not (has_articles and has_detail):
        raise ValueError("Invalid page)")

    return soup.find(class_="items-container")


def parse_listings(soup, freguesia):
    articles = soup.find_all("article", attrs={"data-element-id": True})

    listings = []

    for art in articles:
        listing_id = art["data-element-id"]
        price = art.find("span", class_="item-price h2-simulated").get_text(strip=True)
        title = art.find("a", class_="item-link")["title"]
        extra = [
            span.get_text(strip=True)
            for span in art.find("div", class_="item-detail-char").find_all(
                "span", class_="item-detail"
            )
        ]

        listings.append(
            {
                "id": listing_id,
                "price": price,
                "title": title,
                "extra": extra,
                "freguesia": freguesia,
            }
        )

    return listings
