import sqlite3
import requests
from bs4 import BeautifulSoup
import os
import sys
import time
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scrapers"))

from parsers_riguroso import extraer_direccion_rigurosa, geocodificar_direccion
from parsers import extraer_vehiculos, extraer_fallecidos, extraer_heridos

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accidentes_monteria.db")
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def deep_scrape_and_enrich():
    print("==========================================================================")
    print(" PIPELINE DE EXTRACCIÓN RIGUROSA DE DIRECCIONES Y GEOCODIFICACIÓN (GIS) ")
    print("==========================================================================")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Añadir nuevas columnas rigurosas a la tabla si no existen
    columnas_nuevas = [
        ("direccion_especifica", "TEXT"),
        ("barrio_sector", "TEXT"),
        ("municipio", "TEXT"),
        ("latitud", "REAL"),
        ("longitud", "REAL"),
        ("precision_geo", "TEXT")
    ]

    for col, dtype in columnas_nuevas:
        try:
            cursor.execute(f"ALTER TABLE accidentes ADD COLUMN {col} {dtype};")
        except sqlite3.OperationalError:
            pass  # La columna ya existe

    conn.commit()

    # Obtener todas las noticias guardadas
    cursor.execute("SELECT id, titulo, url, descripcion_contexto FROM accidentes")
    registros = cursor.fetchall()
    print(f"Analizando {len(registros)} registros para extracción profunda de direcciones...")

    actualizados = 0
    for reg in registros:
        rec_id, titulo, url, desc_previa = reg
        
        cuerpo_texto = desc_previa or ""
        
        # Intento de extracción del cuerpo completo si la URL es válida
        if url and url.startswith("http"):
            try:
                res = requests.get(url, headers=HEADERS, timeout=5)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    paragraphs = soup.find_all('p')
                    cuerpo_extraido = " ".join([p.get_text() for p in paragraphs])
                    if len(cuerpo_extraido) > len(cuerpo_texto):
                        cuerpo_texto = cuerpo_extraido[:2000]
            except Exception:
                pass
                
        # 1. Extracción rigurosa de dirección
        dir_especifica, barrio, municipio = extraer_direccion_rigurosa(titulo, cuerpo_texto)
        
        # 2. Geocodificación a Latitud y Longitud GPS
        lat, lon, precision = geocodificar_direccion(dir_especifica, barrio, municipio)
        
        # 3. Recalcular vehículos y víctimas con el cuerpo extenso
        texto_full = f"{titulo} {cuerpo_texto}"
        vehiculos = extraer_vehiculos(texto_full)
        fallecido_bool, cant_fallecidos = extraer_fallecidos(texto_full)
        herido_bool, cant_heridos = extraer_heridos(texto_full)

        # Actualizar en la base de datos
        cursor.execute("""
        UPDATE accidentes SET
            direccion_lugar = ?,
            direccion_especifica = ?,
            barrio_sector = ?,
            municipio = ?,
            latitud = ?,
            longitud = ?,
            precision_geo = ?,
            vehiculos_involucrados = ?,
            fallecidos_bool = ?,
            cantidad_fallecidos = ?,
            heridos_bool = ?,
            cantidad_heridos = ?
        WHERE id = ?
        """, (
            dir_especifica, dir_especifica, barrio, municipio, lat, lon, precision,
            vehiculos, 1 if fallecido_bool else 0, cant_fallecidos,
            1 if herido_bool else 0, cant_heridos, rec_id
        ))
        
        actualizados += 1
        if actualizados % 50 == 0:
            print(f"Progreso: {actualizados}/{len(registros)} registros enriquecidos...")

    conn.commit()
    
    # Exportar datasets enriquecidos
    df_riguroso = pd.read_sql_query("SELECT * FROM accidentes ORDER BY fecha_accidente DESC", conn)
    conn.close()
    
    csv_local = os.path.join(BASE_DIR, "accidentes_extraidos_riguroso.csv")
    csv_gis = os.path.join(PROJECT_DIR, "bade_datos_accidentes", "accidentes_scraping_monteria.csv")
    
    df_riguroso.to_csv(csv_local, index=False, encoding='utf-8-sig')
    df_riguroso.to_csv(csv_gis, index=False, encoding='utf-8-sig')
    
    print(f"\n✔ EXTRACCIÓN Y GEOCODIFICACIÓN FINALIZADA:")
    print(f"• Registros Enriquecidos: {actualizados}")
    print(f"• Dataset Riguroso Guardado en: {csv_local}")
    print(f"• Dataset Actualizado para GIS en: {csv_gis}")
    
    # Ejecutar el script GIS para actualizar el Mapa Interactivo HTML
    print("\nActualizando mapa de calor e hiper-localización GIS...")
    os.system("python mapa_GIS_Monteria/procesar_y_cruzar_accidentes.py")

if __name__ == "__main__":
    deep_scrape_and_enrich()
