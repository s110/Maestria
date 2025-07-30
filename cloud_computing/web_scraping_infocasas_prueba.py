import random
import httpx
from bs4 import BeautifulSoup
import json
import polars as pl
import time
import pprint
url='https://www.infocasas.com.pe/gran-oportunidad-de-inversion-en-carabayllo/192545003'

client = httpx.Client()

response = client.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/138.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',})

beautiful_soup = BeautifulSoup(response.text, 'html.parser')

script_tag = beautiful_soup.find('script',type="application/ld+json")

data = json.loads(script_tag.string)

apollo_state=data["object"]["geo"]