
def make_page_urls(pages, freguesia_url):
    # input, number of pages containing litings and full url -> f"{BASE_URL}/{LISBON_MUNICIPALITY}/{LISBON_FREGUESUAS[0]}/" returns list of urls
    urls = [freguesia_url]
    for page in range(2, pages + 1):
        page_url = f"{freguesia_url}pagina-{page}"
        urls.append(page_url)

    return urls


def get_freguesia(url):
    return url.split('/')[5]