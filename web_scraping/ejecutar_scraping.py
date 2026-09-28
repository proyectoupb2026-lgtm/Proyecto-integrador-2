import os
import sys
import sqlite3
import pandas as pd

# Rutas del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
SYS_DB_PATH = os.path.join(BASE_DIR, "database")
SCRAPERS_PATH = os.path.join(BASE_DIR, "scrapers")

sys.path.append(SYS_DB_PATH)
sys.path.append(SCRAPERS_PATH)

from init_db import init_database, DB_PATH
from news_scraper import NewsScraperEngine

def main():
    print("==========================================================================")
    print(" SISTEMA DE WEB SCRAPING - ACCIDENTES DE TRÁNSITO MONTERÍA & CÓRDOBA ")
    print("==========================================================================")
    
    # 1. Inicializar Esquema de Base de Datos SQLite
    print("\n[Paso 1/3] Verificando e inicializando base de datos SQLite...")
    init_database(DB_PATH)
    
    # 2. Ejecutar Rastreo de Scraper
    print("\n[Paso 2/3] Ejecutando rastreador de noticias (El Meridiano, El Propio, Chica Noticias, etc.)...")
    engine = NewsScraperEngine(db_path=DB_PATH)
    nuevos = engine.ejecutar_rastreo_completo()
    
    # 3. Exportar resultados actualizados a CSV para integrar con el módulo GIS
    print("\n[Paso 3/3] Exportando datos extraídos para módulo GIS y análisis...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM accidentes ORDER BY fecha_accidente DESC", conn)
    conn.close()
    
    csv_local = os.path.join(BASE_DIR, "accidentes_extraidos.csv")
    csv_gis = os.path.join(PROJECT_DIR, "bade_datos_accidentes", "accidentes_scraping_monteria.csv")
    
    df.to_csv(csv_local, index=False, encoding='utf-8-sig')
    df.to_csv(csv_gis, index=False, encoding='utf-8-sig')
    
    print(f"[OK] Exportación completada en: {csv_local}")
    print(f"[OK] Exportación copiada a carpeta GIS: {csv_gis}")
    print(f"\n==========================================================================")
    print(f" PROCESO COMPLETADO: {len(df)} noticias de accidentes registradas en la DB.")
    print("==========================================================================")

if __name__ == "__main__":
    main()
