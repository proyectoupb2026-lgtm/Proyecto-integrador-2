import folium
from folium.plugins import HeatMap
import os
import pandas as pd

try:
    from utils.data_loader import GEOJSON_VIAL, load_accidents_data, load_zonas_demanda, load_candidatos
except ModuleNotFoundError:
    from app_ambulancias.utils.data_loader import GEOJSON_VIAL, load_accidents_data, load_zonas_demanda, load_candidatos

def create_folium_map(allocation, num_bases, centros, active_routes=None, pending_lat=None, pending_lon=None, df_cand=None):
    m = folium.Map(location=[8.7508, -75.8814], zoom_start=13, tiles='OpenStreetMap')
    # Capa 0: Red Vial Offline de Montería (DESACTIVADO POR RENDIMIENTO)
    # Cargar este GeoJSON en HTML pesa varios MB y colapsa el navegador
    # if os.path.exists(GEOJSON_VIAL):
    #     ...

    # Capa 1: Siniestros Reales Georreferenciados (Montería Urbano)
    df_valid = load_accidents_data(solo_monteria=True, excluir_centroide=True)
    if not df_valid.empty:
        heat_data = [[r['latitud'], r['longitud']] for _, r in df_valid.iterrows()]
        heat_layer = folium.FeatureGroup(name='Mapa de Calor Siniestros (Montería)', show=True)
        HeatMap(heat_data, radius=18, blur=22, max_zoom=14).add_to(heat_layer)
        heat_layer.add_to(m)

        # Capa de puntos individuales (DESACTIVADA POR RENDIMIENTO)
        # points_layer = folium.FeatureGroup(name='📍 Puntos de Siniestros Geocodificados', show=False)
        # ...

    # Capa 2: Zonas Calientes de Demanda (Nodos I - Conocimiento Local + Validación)
    df_zonas = load_zonas_demanda()
    if not df_zonas.empty:
        zonas_layer = folium.FeatureGroup(name='Zonas Calientes de Demanda (Nodos I)', show=True)
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

    # Capa 3: Bases Candidatas (Hospitales / Clínicas J + Puntos Estratégicos)
    if df_cand is None:
        df_cand = load_candidatos()
        
    hosp_layer = folium.FeatureGroup(name='Bases Candidatas (Hospitales J)', show=True)
    
    if not df_cand.empty:
        for idx, h in df_cand.iterrows():
            if idx < num_bases:
                is_estrategico = "Estratégico" in str(h.get('nombre', ''))
                icon_color = '#a855f7' if is_estrategico else '#3b82f6' # Purple or Blue
                icon_type = 'star' if is_estrategico else 'h-square'
                
                # Custom circular marker (smaller and cleaner than the default pin)
                html_base = f"""
                <div style="background-color: white; border: 2px solid {icon_color}; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                    <i class="fa fa-{icon_type}" style="color: {icon_color}; font-size: 12px; margin: auto;"></i>
                </div>
                """
                
                folium.Marker(
                    location=[h['lat'], h['lon']],
                    popup=folium.Popup(f"<b>Base {idx}: {h['nombre']}</b><br>{h.get('direccion', '')}", max_width=250),
                    icon=folium.DivIcon(html=html_base, icon_size=(24, 24), icon_anchor=(12, 12))
                ).add_to(hosp_layer)
    else:
        for j in range(num_bases):
            if j < len(centros):
                folium.CircleMarker(
                    location=centros[j], radius=8,
                    color='#3b82f6', fill=True, fill_color='#3b82f6', fill_opacity=0.8,
                    popup=f"Base Candidata {j}"
                ).add_to(hosp_layer)
    hosp_layer.add_to(m)

    # Capa 4: Ambulancias Asignadas por el Modelo MILP
    amb_layer = folium.FeatureGroup(name='Ambulancias Asignadas (Óptimas)', show=True)
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
                
            # Icono A1 desplazado hacia la esquina superior derecha para no solapar la base
            html_icon = f"""
            <div style="background-color: #16a34a; color: white; border-radius: 12px; padding: 2px 6px; font-weight: bold; font-family: sans-serif; font-size: 11px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); text-align: center; display: inline-block; white-space: nowrap;">
                A{j+1}
            </div>
            """
            folium.Marker(
                location=coord,
                popup=folium.Popup(f"<b>Asignación Óptima MILP</b><br>{h_name}<br>Flota asignada: <b>{cant} ambulancia(s)</b>", max_width=250),
                icon=folium.DivIcon(html=html_icon, icon_size=(30, 20), icon_anchor=(-8, 25))
            ).add_to(amb_layer)
    amb_layer.add_to(m)

    # Capa 5: Ruta Real de Despacho Activa (Simulador en Vivo)
    if active_routes:
        route_layer = folium.FeatureGroup(name='Rutas de Despacho en Vivo', show=True)
        from folium.plugins import AntPath
        
        all_lats = []
        all_lons = []
        
        for route_info in active_routes:
            if 'path_coords' in route_info:
                path = route_info['path_coords']
                
                # Trazar línea de ruta animada sobre la red vial (simula movimiento)
                AntPath(
                    locations=path,
                    color='#0284c7',  # Azul para destacar
                    pulse_color='#bae6fd', # Pulso claro
                    weight=5,
                    opacity=0.9,
                    delay=800, # Velocidad de la animación
                    dash_array=[10, 20],
                    tooltip=f"Ruta de Despacho: {route_info.get('distance_km', 0)} km ({route_info.get('travel_time_min', 0)} min)"
                ).add_to(route_layer)
                
                all_lats.extend([c[0] for c in path])
                all_lons.extend([c[1] for c in path])
                
                # Marcador de la Emergencia (Punto rojo sólido y limpio)
                dest_coord = path[-1]
                html_dest = f"""
                <div style="background-color: #ef4444; border: 3px solid white; width: 16px; height: 16px; border-radius: 50%; box-shadow: 0 0 6px rgba(239,68,68,0.8);"></div>
                """
                folium.Marker(
                    location=dest_coord,
                    popup=folium.Popup(
                        f"<b>LUGAR DE LA EMERGENCIA</b><br>"
                        f"<b>Zona:</b> {route_info.get('zone_name')}<br>"
                        f"<b>Tiempo Resp:</b> {route_info.get('travel_time_min')} min<br>"
                        f"<b>Distancia:</b> {route_info.get('distance_km')} km",
                        max_width=250
                    ),
                    icon=folium.DivIcon(html=html_dest, icon_size=(16, 16), icon_anchor=(8, 8))
                ).add_to(route_layer)
                
                # Marcador de Salida de la Ambulancia (desplazado hacia abajo para no tapar la base)
                current_coord = route_info.get('current_pos', path[0])
                status = route_info.get('status', 'EN RUTA')
                bg_color = "#0284c7" if status == "En Camino" else "#16a34a"
                progress_pct = int(route_info.get('progress', 0) * 100)
                
                html_amb = f"""
                <div style="background-color: {bg_color}; color: white; border-radius: 12px; padding: 2px 6px; font-weight: bold; font-family: sans-serif; font-size: 10px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); text-align: center; display: inline-block; white-space: nowrap;">
                    {status}
                </div>
                """
                folium.Marker(
                    location=current_coord,
                    popup=folium.Popup(
                        f"<b>ESTADO: {status}</b><br>"
                        f"<b>Base Originaria:</b> {route_info.get('hospital_name')}<br>"
                        f"<b>Progreso:</b> {progress_pct}%",
                        max_width=250
                    ),
                    icon=folium.DivIcon(html=html_amb, icon_size=(75, 20), icon_anchor=(37, -5))
                ).add_to(route_layer)
                
        # Auto-Centrar el mapa para enfocar el recorrido de TODAS las ambulancias
        if all_lats and all_lons:
            m.fit_bounds([[min(all_lats), min(all_lons)], [max(all_lats), max(all_lons)]])
            
        route_layer.add_to(m)

    # Marcador de Punto Seleccionado (Pendiente por Despachar)
    if pending_lat is not None and pending_lon is not None:
        html_pending = """
        <div style="background-color: #f59e0b; color: white; border-radius: 4px; padding: 2px 4px; font-weight: bold; font-family: sans-serif; font-size: 12px; border: 1px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3); text-align: center; white-space: nowrap;">
            Punto Seleccionado
        </div>
        """
        folium.Marker(
            location=[pending_lat, pending_lon],
            tooltip="Punto objetivo pendiente de despacho",
            icon=folium.DivIcon(html=html_pending, icon_anchor=(35, 10))
        ).add_to(m)

    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    return m
