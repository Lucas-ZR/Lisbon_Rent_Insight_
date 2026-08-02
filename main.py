import time

import logging


from scraper.browser import setup_driver, smart_get_page
from scraper.parser import get_page_count, get_listings, parse_listings
from scraper.urls import make_page_urls, get_freguesia, make_base_urls
from db.database import DatabaseManager

from selenium.common.exceptions import TimeoutException

from config import Settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s %(funcName)s — %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("scrape.log")],
)

logger = logging.getLogger(__name__)


def scrape_url(driver, url, retries=3):
    for attempt in range(retries):
        try:
            page = smart_get_page(driver, url, wait=None)
            page_count = get_page_count(page)
            listings = get_listings(page)
            return listings, page_count
        except (ValueError, TimeoutException) as exc:
            logger.warning(
                "attempt %d/%d failed for %s: %s", attempt + 1, retries, url, exc
            )
            time.sleep(3 * (1 + attempt))

    logger.error("giving up on %s", url)
    return None, None


def process(bs4_listings, parent_url, url, db, page_count=None):
    logger.info("processing %s", url)

    status = "failure"

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
    logger.info("Initializing run")

    # vars
    settings = Settings()

    with DatabaseManager(
        settings.database_name, settings.schema_name, settings.motherduck_token
    ) as db:
        db.init_schema()

        # setup driver and urls
        driver = setup_driver(
            driver_version=150,
            use_proxy=True,
            proxy_username=settings.proxy_username,
            password=settings.password,
            domain_name=settings.domain_name,
            port=settings.port,
        )
        parent_urls = make_base_urls()
        already_scraped = db.get_already_scraped()

        for url in parent_urls:
            if url in already_scraped:
                # if already scraped, reuse page_count, skip re-scraping
                page_count = already_scraped[url]
                logger.info("skipping %s", url)
            else:
                parent_url_listings, page_count = scrape_url(driver, url)
                process(parent_url_listings, url, url, db, page_count)

            if page_count:
                child_urls = make_page_urls(page_count, url)

                for child_url in child_urls:  # always build child_urls and checks, a bit inneficient but simple enough
                    if child_url in already_scraped:
                        logger.info("skipping %s", child_url)
                        continue

                    child_url_listings, _ = scrape_url(driver, child_url)
                    process(child_url_listings, url, child_url, db)
        logger.info("Run finished")


if __name__ == "__main__":
    main()
