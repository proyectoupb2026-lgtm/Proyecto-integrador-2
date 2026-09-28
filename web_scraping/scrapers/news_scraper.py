import requests
from bs4 import BeautifulSoup
import time
import logging
import sqlite3
import urllib.parse
from datetime import datetime, timedelta
import os
import sys

# Importar parsers locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parsers import (
    hash_accidente, extraer_vehiculos, extraer_fallecidos,
    extraer_heridos, extraer_direccion_lugar, parsear_fecha_espanol
)

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("web_scraping/scraping_activity.log", encoding="utf-8")
    ]
)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
}

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "accidentes_monteria.db")

class NewsScraperEngine:
    def __init__(self, db_path=DB_PATH, delay_seconds=1.5):
        self.db_path = db_path
        self.delay_seconds = delay_seconds
        
    def _fetch_url(self, url, retries=3):
        """Descarga el contenido HTML respetando rate limiting y manejando reintentos."""
        time.sleep(self.delay_seconds)
        for attempt in range(1, retries + 1):
            try:
                response = requests.get(url, headers=HEADERS, timeout=12)
                if response.status_code == 200:
                    return response.text
                else:
                    logging.warning(f"Respuesta HTTP {response.status_code} al solicitar {url}")
            except Exception as e:
                logging.error(f"Intento {attempt}/{retries} fallido para {url}: {e}")
                time.sleep(2)
        return None

    def _insertar_accidente(self, data):
        """Inserta la noticia extraída en la base de datos controlando duplicados."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO accidentes (
                hash_duplicados, titulo, fuente, url, fecha_publicacion,
                fecha_accidente, direccion_lugar, vehiculos_involucrados,
                fallecidos_bool, cantidad_fallecidos, heridos_bool, cantidad_heridos,
                descripcion_contexto
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['hash_duplicados'], data['titulo'], data['fuente'], data['url'],
                data['fecha_publicacion'], data['fecha_accidente'], data['direccion_lugar'],
                data['vehiculos_involucrados'], data['fallecidos_bool'], data['cantidad_fallecidos'],
                data['heridos_bool'], data['cantidad_heridos'], data['descripcion_contexto']
            ))
            conn.commit()
            logging.info(f"✔ NOTICIA GUARDADA: [{data['fuente']}] {data['titulo'][:50]}... | Lugar: {data['direccion_lugar']}")
            return True
        except sqlite3.IntegrityError:
            logging.debug(f"Accidente omitido por duplicado (Hash/URL ya registrado): {data['url']}")
            return False
        except Exception as e:
            logging.error(f"Error al insertar en DB: {e}")
            return False
        finally:
            conn.close()

    def scrape_google_news_rss(self, query="accidente de transito Monteria Cordoba"):
        """Scraper resiliente vía RSS de Google News para noticias históricas y recientes de Montería/Córdoba."""
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=es-419&gl=CO&ceid=CO:es-419"
        
        logging.info(f"Iniciando scraping vía RSS Google News para: '{query}'")
        html_content = self._fetch_url(rss_url)
        if not html_content:
            return 0

        soup = BeautifulSoup(html_content, 'xml')
        items = soup.find_all('item')
        logging.info(f"Items encontrados en RSS para '{query}': {len(items)}")

        registrados = 0
        for item in items:
            titulo = item.title.text if item.title else "Sin Título"
            link = item.link.text if item.link else ""
            pub_date = item.pubDate.text if item.pubDate else ""
            desc = item.description.text if item.description else titulo
            fuente_tag = item.find('source')
            fuente_nombre = fuente_tag.text if fuente_tag else "Portal de Noticias Local"

            fecha_formatted = parsear_fecha_espanol(pub_date)
            hash_id = hash_accidente(titulo, fecha_formatted)

            # Extracción NLP
            texto_completo = f"{titulo} {desc}"
            fallecido_bool, cant_fallecidos = extraer_fallecidos(texto_completo)
            herido_bool, cant_heridos = extraer_heridos(texto_completo)
            vehiculos = extraer_vehiculos(texto_completo)
            lugar = extraer_direccion_lugar(texto_completo)

            data = {
                'hash_duplicados': hash_id,
                'titulo': titulo,
                'fuente': fuente_nombre,
                'url': link,
                'fecha_publicacion': fecha_formatted,
                'fecha_accidente': fecha_formatted,
                'direccion_lugar': lugar,
                'vehiculos_involucrados': vehiculos,
                'fallecidos_bool': 1 if fallecido_bool else 0,
                'cantidad_fallecidos': cant_fallecidos,
                'heridos_bool': 1 if herido_bool else 0,
                'cantidad_heridos': cant_heridos,
                'descripcion_contexto': BeautifulSoup(desc, "html.parser").get_text()[:500]
            }

            if self._insertar_accidente(data):
                registrados += 1

        return registrados

    def ejecutar_rastreo_completo(self):
        """Ejecuta búsquedas combinadas para cubrir El Meridiano, El Propio, Chica Noticias y portales regionales."""
        busquedas = [
            "accidente transito Monteria",
            "accidente choques muertos Monteria Cordoba",
            "accidente motocicleta Cereté Monteria",
            "accidente avenida circunvalar Monteria",
            "accidente El Meridiano Cordoba",
            "accidente Chica Noticias Monteria",
            "accidente El Propio Cordoba"
        ]
        
        total_nuevos = 0
        for query in busquedas:
            total_nuevos += self.scrape_google_news_rss(query)
            time.sleep(2)
            
        logging.info(f"=== RASTREO FINALIZADO: {total_nuevos} nuevos accidentes registrados ===")
        return total_nuevos

if __name__ == "__main__":
    scraper = NewsScraperEngine()
    scraper.ejecutar_rastreo_completo()
