import sqlite3
import os
import sys
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
SYS_DB_PATH = os.path.join(BASE_DIR, "database")
SCRAPERS_PATH = os.path.join(BASE_DIR, "scrapers")

sys.path.append(SYS_DB_PATH)
sys.path.append(SCRAPERS_PATH)

from parsers_riguroso import extraer_direccion_rigurosa, geocodificar_direccion
from parsers import extraer_vehiculos, extraer_fallecidos, extraer_heridos

DB_PATH = os.path.join(BASE_DIR, "accidentes_monteria.db")

def enriquecimiento_memoria():
    print("==========================================================================")
    print(" PROCESAMIENTO RIGUROSO DE DIRECCIONES Y GEOCODIFICACIÓN EN MEMORIA ")
    print("==========================================================================")

    # 1. Leer los datos desde la DB y cerrar conexión de inmediato para liberar el lock
    conn = sqlite3.connect(DB_PATH, timeout=60)
    df = pd.read_sql_query("SELECT * FROM accidentes", conn)
    conn.close()

    print(f"Cargados {len(df)} registros para procesamiento riguroso de direcciones...")

    direcciones_esp = []
    barrios = []
    municipios = []
    latitudes = []
    longitudes = []
    precisiones = []
    vehiculos_list = []
    fallecidos_bool_list = []
    cant_fallecidos_list = []
    heridos_bool_list = []
    cant_heridos_list = []

    for idx, row in df.iterrows():
        titulo = str(row.get('titulo', ''))
        desc = str(row.get('descripcion_contexto', ''))
        texto_full = f"{titulo} {desc}".strip()

        # 1. Extracción rigurosa de dirección
        dir_esp, barrio, muni = extraer_direccion_rigurosa(titulo, desc)

        # 2. Geocodificación espacial GPS
        lat, lon, prec = geocodificar_direccion(dir_esp, barrio, muni)

        # 3. Recalcular vehículos y víctimas
        veh = extraer_vehiculos(texto_full)
        f_bool, f_cant = extraer_fallecidos(texto_full)
        h_bool, h_cant = extraer_heridos(texto_full)

        direcciones_esp.append(dir_esp)
        barrios.append(barrio)
        municipios.append(muni)
        latitudes.append(lat)
        longitudes.append(lon)
        precisiones.append(prec)
        vehiculos_list.append(veh)
        fallecidos_bool_list.append(1 if f_bool else 0)
        cant_fallecidos_list.append(f_cant)
        heridos_bool_list.append(1 if h_bool else 0)
        cant_heridos_list.append(h_cant)

    # Asignar columnas enriquecidas
    df['direccion_lugar'] = direcciones_esp
    df['direccion_especifica'] = direcciones_esp
    df['barrio_sector'] = barrios
    df['municipio'] = municipios
    df['latitud'] = latitudes
    df['longitud'] = longitudes
    df['precision_geo'] = precisiones
    df['vehiculos_involucrados'] = vehiculos_list
    df['fallecidos_bool'] = fallecidos_bool_list
    df['cantidad_fallecidos'] = cant_fallecidos_list
    df['heridos_bool'] = heridos_bool_list
    df['cantidad_heridos'] = cant_heridos_list

    # 2. Re-escribir tabla en SQLite y exportar CSVs
    conn2 = sqlite3.connect(DB_PATH, timeout=60)
    df.to_sql("accidentes", conn2, if_exists="replace", index=False)
    conn2.close()

    csv_local = os.path.join(BASE_DIR, "accidentes_extraidos_riguroso.csv")
    csv_gis = os.path.join(PROJECT_DIR, "bade_datos_accidentes", "accidentes_scraping_monteria.csv")

    df.to_csv(csv_local, index=False, encoding='utf-8-sig')
    df.to_csv(csv_gis, index=False, encoding='utf-8-sig')

    print(f"\n[OK] ENRIQUECIMIENTO FINALIZADO CON ÉXITO:")
    print(f"• Registros georreferenciados: {len(df)}")
    print(f"• Dataset Riguroso Local: {csv_local}")
    print(f"• Dataset Actualizado para GIS: {csv_gis}")

    print("\nActualizando mapa de calor e hiper-localización GIS...")
    import subprocess
    subprocess.run(["python", os.path.join(PROJECT_DIR, "mapa_GIS_Monteria", "procesar_y_cruzar_accidentes.py")])

if __name__ == "__main__":
    enriquecimiento_memoria()
