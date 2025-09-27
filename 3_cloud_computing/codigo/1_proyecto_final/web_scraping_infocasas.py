import random
import httpx
from bs4 import BeautifulSoup
import json
import time

class ScraperInfoCasas:
    def __init__(self,headers: dict, base_url: str, pages_scraped: int=50):
        self.info_dict = None
        self.pagination_info = None
        self.headers = headers
        self.base_url = base_url
        self.client=httpx.Client()
        self.buildings_list=[]
        self.total_possible_pages=None
        self.pages_scraped=pages_scraped

    def fetch_first_page(self):
        """
        Obtiene el HTML de la primera página, lo parsea y extrae los datos JSON.
        """
        try:
            url=f'{self.base_url}/venta'
            response = self.client.get(url,headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')

            if not script_tag:
                print(f"Advertencia: No se encontró la etiqueta '__NEXT_DATA__' en la página.")
                return None

            data = json.loads(script_tag.string)
            apollo_state = data['props']['pageProps']['apolloState']
            self.info_dict = {key: value for key, value in apollo_state.items() if "Filter:" in key}
            #search_key = [key for key in apollo_state['ROOT_QUERY'] if key.startswith('searchFast')][0]
            search_key=next((key for key in apollo_state.get('ROOT_QUERY', {}) if key.startswith('searchFast')), None)
            if not search_key:
                print(f"Advertencia: No se pudo encontrar la clave 'searchFast' en la página 1.")
                return None
            self.pagination_info = apollo_state['ROOT_QUERY'][search_key]['paginatorInfo']
            self.total_possible_pages = self.pagination_info.get('lastPage', 1)
            if self.total_possible_pages<self.pages_scraped:
                self.pages_scraped=self.total_possible_pages
                print('El número solicitado de páginas es mayor al número total en el sitio. Limitando al numero disponible.')
            buildings_page_list = apollo_state['ROOT_QUERY'][search_key]['data']
            return buildings_page_list

        except httpx.RequestError as e:
            print(f"Error de red en la página: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Error de JSON en la página.")
            return None
        except Exception as e:
            print(f"Ocurrió un error inesperado en la página: {e}")
            return None


    def fetch_and_parse_page(self,page_number: int):
        """
        Obtiene el HTML de una página específica, lo parsea y extrae los datos JSON.
        """

        url = f"{self.base_url}/venta/pagina{page_number}"
        print(f"\n--- Obteniendo datos de la página {page_number}: {url} ---")

        try:
            response = self.client.get(url,headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')

            if not script_tag:
                print(f"Advertencia: No se encontró la etiqueta '__NEXT_DATA__' en la página {page_number}.")
                return None

            data = json.loads(script_tag.string)
            apollo_state = data['props']['pageProps']['apolloState']
            #search_key = [key for key in apollo_state['ROOT_QUERY'] if key.startswith('searchFast')][0]
            search_key=next((key for key in apollo_state.get('ROOT_QUERY', {}) if key.startswith('searchFast')), None)
            if not search_key:
                print(f"Advertencia: No se pudo encontrar la clave 'searchFast' en la página {page_number}.")
                return None
            buildings_page_list = apollo_state['ROOT_QUERY'][search_key]['data']
            return buildings_page_list

        except httpx.RequestError as e:
            print(f"Error de red en la página {page_number}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Error de JSON en la página {page_number}.")
            return None
        except Exception as e:
            print(f"Ocurrió un error inesperado en la página {page_number}: {e}")
            return None

    def scrape_geo_info(self, house_link: str):
        try:
            url = self.base_url + house_link
            response = self.client.get(url, headers=self.headers)
            response.raise_for_status()  # Lanza una excepción para errores HTTP (4xx o 5xx)

            beautiful_soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = beautiful_soup.find('script', type="application/ld+json")

            if not script_tag:
                print(f"Advertencia: No se encontró la etiqueta ld+json en {url}")
                return None  # O retorna un diccionario vacío: {}

            data = json.loads(script_tag.string)
            # Es más seguro usar .get() para evitar KeyErrors
            geo_data = data.get("object", {}).get("geo")
            return geo_data
        except httpx.RequestError as e:
            print(f"Error de red al obtener detalles de {house_link}: {e}")
            return None
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Error al parsear datos de {house_link}: {e}")
            return None


    def run(self):
        self.buildings_list.extend(self.fetch_first_page())
        for i in range(2,self.pages_scraped+1):
            time.sleep(random.uniform(4, 10))
            self.buildings_list.extend(self.fetch_and_parse_page(i))

        for item in self.buildings_list:
            item_link = item['link']
            geo_info = self.scrape_geo_info(item_link)
            if geo_info:  # Solo actualiza si obtuviste datos
                item.update(geo=geo_info)
            time.sleep(random.uniform(3, 5))  # Un poco más legible para un rango

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/138.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    pages_scraped=5
    scraper=ScraperInfoCasas(headers=headers,base_url='https://www.infocasas.com.pe',pages_scraped=pages_scraped)
    scraper.run()