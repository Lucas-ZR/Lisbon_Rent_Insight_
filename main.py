from scraper.browser import setup_driver, get_page
from scraper.parser import get_page_count, get_listings, parse_listings
from scraper.urls import make_page_urls, get_freguesia
from db.init import DatabaseManager

import time
import os
from dotenv import load_dotenv


def pagination_scrape_url(driver, url, retries=3):
    for attempt in range(retries):
        try:
            page = get_page(driver, url)
            page_count = get_page_count(page)
            listings = get_listings(page)
            return page_count, listings
        except ValueError:
            time.sleep(3 * (1 + attempt))
    return None, None


def scrape_url(driver, url, retries=3):
    for attempt in range(retries):
        try:
            page = get_page(driver, url)
            return get_listings(page)
        except ValueError:
            time.sleep(3 * (1 + attempt))
    return None


def process(bs4_listings, parent_url, url, db):
    status = "failure"

    if bs4_listings:
        listings_list = parse_listings(bs4_listings, get_freguesia(url))
        db.write_listings(listings_list)
        status = "success"

    db.write_job_state(
        parent_url=parent_url,
        url=url,
        status=status,
    )


def main():

    # setup db
    load_dotenv(".env.test")
    database_name = os.getenv("database_name")
    schema_name = os.getenv("schema_name")

    with DatabaseManager(database_name, schema_name) as db:
        db.init_schema()

        # setup driver and urls
        driver = setup_driver()
        url = "https://www.google.com/"

        # first URL
        page_count, page_1_listings = pagination_scrape_url(driver, url)
        process(page_1_listings, url, url, db)


"""
        if page_count:
            child_urls = make_page_urls(page_count, url)

        # scraping
        for url in urls[1:]:
            listings = scrape_url(driver, url)
            process(listings, url, child_url, db)
"""

if __name__ == "__main__":
    main()


# to do
# pick arrendado from tags add to extra
# support saving itself
