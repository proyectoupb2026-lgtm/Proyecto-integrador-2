import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

# Rutas globales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_ACCIDENTES = os.path.join(BASE_DIR, "accidentes_verificados_actualizados.csv")
GEOJSON_VIAL = os.path.join(BASE_DIR, "MAPAS_VECTORIALES_MONTERIA_OFFLINE", "2_GeoJSON_Web_GIS", "monteria_malla_vial.geojson")

def load_accidents_data():
    """Carga y limpia el dataset de accidentes."""
    if not os.path.exists(CSV_ACCIDENTES):
        return pd.DataFrame(columns=['latitud', 'longitud'])
    df = pd.read_csv(CSV_ACCIDENTES, dtype={'latitud': str, 'longitud': str})
    df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
    df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
    return df.dropna(subset=['latitud', 'longitud'])

def calculate_clusters(n_clusters):
    """Calcula clusters de accidentes para ubicar nodos de demanda y bases candidatas."""
    df = load_accidents_data()
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
