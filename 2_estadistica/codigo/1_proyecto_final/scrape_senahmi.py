import requests
from bs4 import BeautifulSoup
import re
import environ
import json
import polars as pl
from io import StringIO
from pathlib import Path
from dateutil.relativedelta import relativedelta
import datetime
from xlsxwriter import Workbook

urls={
    'senamhi_mapa':'https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/'

}
headers = {
    "Host": "www.senamhi.gob.pe",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Referer": "https://www.senamhi.gob.pe/?p=estaciones",
    "Cookie": "SRVNAME=s1",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "iframe",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=4"
}

with requests.Session() as session:
    response = session.get(urls['senamhi_mapa'], headers=headers)
    soup_mapa= BeautifulSoup(response.text, 'html.parser')
    name_estaciones=soup_mapa.find('script',{'type':'text/javascript'})
    match = re.search(r"var PruebaTest = (\[.*?\]);", name_estaciones.text, re.DOTALL)
    if match:
        estaciones_json = match.group(1)  # Extrae el JSON como string
        estaciones = json.loads(estaciones_json)  # Convierte a lista de diccionarios
        print(estaciones)  # Lista de diccionarios
    else:
        print("No se encontró la variable PruebaTest en el HTML.")
