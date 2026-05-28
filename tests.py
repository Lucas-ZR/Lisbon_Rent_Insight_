from scraper.browser import setup_driver, get_page, smart_get_page


driver = setup_driver()


url = "https://www.idealista.pt/comprar-casas/lisboa/ajuda/"
page = smart_get_page(driver, url)

print(page)
