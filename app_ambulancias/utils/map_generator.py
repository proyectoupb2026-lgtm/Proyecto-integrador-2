import folium
from folium.plugins import HeatMap
import os
import pandas as pd
from utils.data_loader import GEOJSON_VIAL, CSV_ACCIDENTES

def create_folium_map(allocation, num_bases, centros):
    m = folium.Map(location=[8.7508, -75.8814], zoom_start=13, tiles='OpenStreetMap')
    
    # Capa 0: Red Vial Offline
    if os.path.exists(GEOJSON_VIAL):
        vial_layer = folium.FeatureGroup(name='🗺️ Red Vial (Offline)', show=False)
        folium.GeoJson(
            GEOJSON_VIAL,
            style_function=lambda x: {'color': '#4a90d9', 'weight': 1.0, 'opacity': 0.4}
        ).add_to(vial_layer)
        vial_layer.add_to(m)

    # Capa 1: Mapa de Calor
    if os.path.exists(CSV_ACCIDENTES):
        df = pd.read_csv(CSV_ACCIDENTES, dtype={'latitud': str, 'longitud': str})
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df_valid = df.dropna(subset=['latitud', 'longitud'])
        heat_data = [[r['latitud'], r['longitud']] for _, r in df_valid.iterrows()]
        
        heat_layer = folium.FeatureGroup(name='🔥 Alta Accidentalidad', show=True)
        HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(heat_layer)
        heat_layer.add_to(m)

        # Capa 1.5: Puntos Radiales (Frecuencia de Siniestros)
        points_layer = folium.FeatureGroup(name='📍 Puntos de Siniestros (Radial)', show=True)
        df_grouped = df_valid.groupby(['latitud', 'longitud']).size().reset_index(name='frecuencia')
        
        for _, row in df_grouped.iterrows():
            freq = row['frecuencia']
            # Escalar el radio del círculo según la cantidad de accidentes (frecuencia)
            r = 4 + (freq * 2.5) 
            folium.CircleMarker(
                location=[row['latitud'], row['longitud']],
                radius=r,
                color='#ef4444',
                weight=1,
                fill=True,
                fill_color='#ef4444',
                fill_opacity=0.6,
                popup=f"<strong>Frecuencia:</strong> {freq} accidente(s) registrados aquí"
            ).add_to(points_layer)
        points_layer.add_to(m)

    # Capa 2: Bases Candidatas
    hosp_layer = folium.FeatureGroup(name='🏥 Bases Candidatas', show=True)
    for j in range(num_bases):
        if j < len(centros):
            coord = centros[j]
            folium.CircleMarker(
                location=coord, radius=10,
                color='#FFA500', fill=True, fill_color='#FFA500', fill_opacity=0.7,
                popup=f"Base Candidata {j}"
            ).add_to(hosp_layer)
    hosp_layer.add_to(m)

    # Capa 3: Ambulancias
    amb_layer = folium.FeatureGroup(name='🚑 Ambulancias Asignadas', show=True)
    for j in range(num_bases):
        cant = allocation.get(j, 0)
        if cant > 0 and j < len(centros):
            coord = centros[j]
            folium.Marker(
                location=coord,
                popup=f"Base {j}: {cant} ambulancias",
                icon=folium.Icon(color='green', icon='plus-sign')
            ).add_to(amb_layer)
    amb_layer.add_to(m)

    folium.LayerControl(position='topright').add_to(m)
    return m
