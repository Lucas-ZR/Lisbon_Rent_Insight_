import os
import time

from dotenv import load_dotenv

from scraper.browser import setup_driver, smart_get_page
from scraper.parser import get_page_count, get_listings, parse_listings
from scraper.urls import make_page_urls, get_freguesia, make_base_urls
from db.init import DatabaseManager

from selenium.common.exceptions import TimeoutException


def scrape_url(driver, url, retries=3):
    for attempt in range(retries):
        try:
            page = smart_get_page(driver, url, wait=None)
            page_count = get_page_count(page)
            listings = get_listings(page)
            return listings, page_count
        except (ValueError, TimeoutException):
            time.sleep(3 * (1 + attempt))
    return None, None


def process(bs4_listings, parent_url, url, db, page_count=None):
    status = "failure"
    print(f"Processing {url}")

    if bs4_listings:
        listings_list = parse_listings(bs4_listings, get_freguesia(url))
        db.write_listings(listings_list)
        status = "success"

    db.write_job_state(
        parent_url=parent_url,
        url=url,
        status=status,
        page_count=page_count,
    )


def main():
    # db
    load_dotenv(".env.test")
    database_name, schema_name = os.getenv("database_name"), os.getenv("schema_name")

    # proxy
    proxy_username, password, domain_name, port = (
        os.getenv("PROXY_USERNAME"),
        os.getenv("PASSWORD"),
        os.getenv("DOMAIN_NAME"),
        os.getenv("PORT"),
    )

    with DatabaseManager(database_name, schema_name) as db:
        db.init_schema()

        # setup driver and urls
        driver = setup_driver(
            driver_version=147,
            use_proxy=True,
            PROXY_USERNAME=proxy_username,
            PASSWORD=password,
            DOMAIN_NAME=domain_name,
            PORT=port,
        )
        parent_urls = make_base_urls()
        already_scraped = db.get_already_scraped()

        for url in parent_urls:
            if url in already_scraped:
                # if already scraped, reuse page_count, skip re-scraping
                page_count = already_scraped[url]
                print(f"Skipping {url}")
            else:
                parent_url_listings, page_count = scrape_url(driver, url)
                process(parent_url_listings, url, url, db, page_count)

            if page_count:
                child_urls = make_page_urls(page_count, url)

                for child_url in child_urls:  # always build child_urls and checks, a bit inneficient but simple enough
                    if child_url in already_scraped:
                        print(f"Skipping {child_url}")
                        continue

                    child_url_listings, _ = scrape_url(driver, child_url)
                    process(child_url_listings, url, child_url, db)


if __name__ == "__main__":
    main()
