from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import polars as pl


with sync_playwright() as playwright:
    n_pages = 10  # numero de paginas a scrapear
    htmls=[]
    print('Playwright initialized')
    # Usamos headless=False para ver la ventana del navegador.
    # Para producción, cambiar a headless=True.
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    try:
        print('Scraping started')
        page.goto("https://urbania.pe/buscar/venta-de-propiedades-en-lima?sort=most_visit",timeout=30000)
        print('Page opened, waiting for page to load')
        time.sleep(5)
        print('Scraping html')
        html = page.content()
        bs4 = BeautifulSoup(html, 'html.parser')

        print('Html obtained')
        # for i in range(n_pages):
        #
        browser.close()

    except Exception as e:
        print('Exception occured with Playwright: ',e)
        browser.close()