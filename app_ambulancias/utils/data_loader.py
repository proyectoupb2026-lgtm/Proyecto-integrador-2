import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

# Rutas globales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_ACCIDENTES = os.path.join(BASE_DIR, "bade_datos_accidentes", "accidentes_verificados_actualizados.csv")
if not os.path.exists(CSV_ACCIDENTES):
    CSV_ACCIDENTES = os.path.join(BASE_DIR, "accidentes_verificados_actualizados.csv")
GEOJSON_VIAL = os.path.join(BASE_DIR, "MAPAS_VECTORIALES_MONTERIA_OFFLINE", "2_GeoJSON_Web_GIS", "monteria_malla_vial.geojson")

EXCEL_NODOS = os.path.join(BASE_DIR, "Nodos_y_Candidatos_Monteria.xlsx")
if not os.path.exists(EXCEL_NODOS):
    EXCEL_NODOS = os.path.join(BASE_DIR, "Nodos_y_Candidatos_Monteria_v2.xlsx")

def load_candidatos():
    """Carga los sitios candidatos (hospitales/clínicas) de Montería."""
    if os.path.exists(EXCEL_NODOS):
        return pd.read_excel(EXCEL_NODOS, sheet_name='Sitios_Candidatos')
    return pd.DataFrame()

def load_zonas_demanda():
    """Carga las 13 zonas calientes de demanda urbana de Montería."""
    if os.path.exists(EXCEL_NODOS):
        return pd.read_excel(EXCEL_NODOS, sheet_name='Zonas_Calientes_Demanda')
    return pd.DataFrame()

def load_accidents_data(solo_monteria=True, excluir_centroide=False):
    """Carga y limpia el dataset de accidentes, filtrando estrictamente por Montería."""
    if not os.path.exists(CSV_ACCIDENTES):
        return pd.DataFrame(columns=['latitud', 'longitud'])
    df = pd.read_csv(CSV_ACCIDENTES, dtype={'latitud': str, 'longitud': str})
    df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
    df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
    df = df.dropna(subset=['latitud', 'longitud'])
    
    if solo_monteria and 'municipio' in df.columns:
        df = df[df['municipio'] == 'Montería']
        
    if excluir_centroide:
        df = df[~((df['latitud'] == 8.7508) & (df['longitud'] == -75.8814))]
        
    return df

def calculate_clusters(n_clusters):
    """Obtiene las coordenadas de los nodos de demanda de Montería."""
    df_zonas = load_zonas_demanda()
    if not df_zonas.empty and len(df_zonas) >= n_clusters:
        return df_zonas[['lat', 'lon']].values.tolist()[:n_clusters]
        
    # Fallback si no está el Excel
    df = load_accidents_data(solo_monteria=True, excluir_centroide=True)
    coords = df[['latitud', 'longitud']].values
    if len(coords) < n_clusters or n_clusters < 1:
        return []
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(coords)
    return kmeans.cluster_centers_.tolist()

def generate_t_ij(node_coords, base_coords, speed_kmh=30.0):
    """Calcula matriz de tiempos (minutos) euclidianos."""
    t_ij = []
    for nc in node_coords:
        row = []
        for bc in base_coords:
            # Distancia aproximada en grados a km
            dist_km = (((nc[0]-bc[0])*111)**2 + ((nc[1]-bc[1])*88)**2)**0.5
            row.append(dist_km / speed_kmh * 60.0)
        t_ij.append(row)
    return t_ij
