from scraper.parser import get_page_count, get_listings, parse_listings
import pytest


def test_page_count(lisboa_ajuda_page1):
    assert get_page_count(lisboa_ajuda_page1) >= 1


def test_page_count_no_page(empty_page):
    with pytest.raises(ValueError):
        get_page_count(empty_page)


def test_get_listings(lisboa_ajuda_page1):
    container = get_listings(lisboa_ajuda_page1)
    assert container is not None


def test_get_listings_no_page(empty_page):
    with pytest.raises(ValueError):
        get_listings(empty_page)


def test_parse_listings(lisboa_ajuda_page1):
    container = get_listings(lisboa_ajuda_page1)
    listings = parse_listings(container, freguesia="ajuda")
    assert len(listings) >= 1
    assert listings[0].keys() == {"id", "price", "title", "detail", "tags", "freguesia"}
