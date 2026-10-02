import folium
from folium.plugins import HeatMap
import os
import pandas as pd
try:
    from utils.data_loader import GEOJSON_VIAL, load_accidents_data, load_zonas_demanda, load_candidatos
except ModuleNotFoundError:
    from app_ambulancias.utils.data_loader import GEOJSON_VIAL, load_accidents_data, load_zonas_demanda, load_candidatos

def create_folium_map(allocation, num_bases, centros):
    m = folium.Map(location=[8.7508, -75.8814], zoom_start=13, tiles='OpenStreetMap')
    
    # Capa 0: Red Vial Offline de Montería
    if os.path.exists(GEOJSON_VIAL):
        vial_layer = folium.FeatureGroup(name='🗺️ Red Vial Montería (Offline)', show=False)
        folium.GeoJson(
            GEOJSON_VIAL,
            style_function=lambda x: {'color': '#4a90d9', 'weight': 1.0, 'opacity': 0.4}
        ).add_to(vial_layer)
        vial_layer.add_to(m)

    # Capa 1: Siniestros Reales Georreferenciados (Montería Urbano)
    df_valid = load_accidents_data(solo_monteria=True, excluir_centroide=True)
    if not df_valid.empty:
        heat_data = [[r['latitud'], r['longitud']] for _, r in df_valid.iterrows()]
        heat_layer = folium.FeatureGroup(name='🔥 Mapa de Calor Siniestros (Montería)', show=True)
        HeatMap(heat_data, radius=18, blur=22, max_zoom=14).add_to(heat_layer)
        heat_layer.add_to(m)

        points_layer = folium.FeatureGroup(name='📍 Puntos de Siniestros Geocodificados', show=True)
        df_grouped = df_valid.groupby(['latitud', 'longitud']).size().reset_index(name='frecuencia')
        
        for _, row in df_grouped.iterrows():
            freq = row['frecuencia']
            r = 5 + (freq * 2.5)
            folium.CircleMarker(
                location=[row['latitud'], row['longitud']],
                radius=r,
                color='#ef4444',
                weight=1.5,
                fill=True,
                fill_color='#ef4444',
                fill_opacity=0.7,
                popup=f"<strong>Siniestros Registrados:</strong> {freq}<br>Lat: {row['latitud']:.4f}, Lon: {row['longitud']:.4f}"
            ).add_to(points_layer)
        points_layer.add_to(m)

    # Capa 2: Zonas Calientes de Demanda (Nodos I - Conocimiento Local + Validación)
    df_zonas = load_zonas_demanda()
    if not df_zonas.empty:
        zonas_layer = folium.FeatureGroup(name='🎯 Zonas Calientes de Demanda (Nodos I)', show=True)
        for _, z in df_zonas.iterrows():
            folium.CircleMarker(
                location=[z['lat'], z['lon']],
                radius=9,
                color='#d97706',
                weight=2,
                fill=True,
                fill_color='#f59e0b',
                fill_opacity=0.85,
                popup=folium.Popup(
                    f"<b>{z['id_zona']}: {z['barrio_zona']}</b><br>"
                    f"<i>Sector:</i> {z['sector_general']}<br>"
                    f"<b>Accidentes reales asignados:</b> {z['accidentes_reales_asignados']}<br>"
                    f"<small>{z['justificacion_validacion']}</small>",
                    max_width=280
                )
            ).add_to(zonas_layer)
        zonas_layer.add_to(m)

    # Capa 3: Bases Candidatas (Hospitales / Clínicas J)
    df_cand = load_candidatos()
    hosp_layer = folium.FeatureGroup(name='🏥 Bases Candidatas (Hospitales J)', show=True)
    
    if not df_cand.empty:
        for idx, h in df_cand.iterrows():
            if idx < num_bases:
                folium.Marker(
                    location=[h['lat'], h['lon']],
                    popup=folium.Popup(f"<b>Base {idx}: {h['nombre']}</b><br>{h['direccion']}", max_width=250),
                    icon=folium.Icon(color='blue', icon='plus', prefix='fa')
                ).add_to(hosp_layer)
    else:
        for j in range(num_bases):
            if j < len(centros):
                folium.CircleMarker(
                    location=centros[j], radius=10,
                    color='#FFA500', fill=True, fill_color='#FFA500', fill_opacity=0.7,
                    popup=f"Base Candidata {j}"
                ).add_to(hosp_layer)
    hosp_layer.add_to(m)

    # Capa 4: Ambulancias Asignadas por el Modelo MILP
    amb_layer = folium.FeatureGroup(name='🚑 Ambulancias Asignadas (Óptimas)', show=True)
    for j in range(num_bases):
        cant = allocation.get(j, 0)
        if cant > 0:
            if not df_cand.empty and j < len(df_cand):
                coord = [df_cand.iloc[j]['lat'], df_cand.iloc[j]['lon']]
                h_name = df_cand.iloc[j]['nombre']
            elif j < len(centros):
                coord = centros[j]
                h_name = f"Base {j}"
            else:
                continue
                
            folium.Marker(
                location=coord,
                popup=folium.Popup(f"<b>🚑 Asignación Óptima</b><br>{h_name}<br>Flota asignada: <b>{cant} ambulancia(s)</b>", max_width=250),
                icon=folium.Icon(color='green', icon='ambulance', prefix='fa')
            ).add_to(amb_layer)
    amb_layer.add_to(m)

    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    return m
