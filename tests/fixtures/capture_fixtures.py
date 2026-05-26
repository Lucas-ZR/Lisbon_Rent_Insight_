# needs to run from root!
from pathlib import Path

from scraper.browser import setup_driver, get_page

FIXTURES_DIR = Path(__file__).parent / "test" / "fixtures"

URLS = {
    "lisboa_ajuda_page1.html": "https://www.idealista.pt/arrendar-casas/lisboa/ajuda/",
    "lisboa_ajuda_pagina2.html": "https://www.idealista.pt/arrendar-casas/lisboa/ajuda/pagina-2",
}


def main():
    driver = setup_driver()

    for filename, url in URLS.items():
        page = get_page(driver, url)
        (FIXTURES_DIR / filename).write_text(page, encoding="utf-8")

    # empty page
    (FIXTURES_DIR / "empty.html").write_text(
        "<html><body></body></html>", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
