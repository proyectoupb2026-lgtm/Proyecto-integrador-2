import os
import glob
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap, MarkerCluster

# Directorios del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "bade_datos_accidentes")
GIS_DIR = BASE_DIR

print("=== INICIANDO SISTEMA GIS DE CRUCE DE ACCIDENTES EN MONTERÍA Y CÓRDOBA ===")

# 1. Cargar Límites Vectoriales
monteria_geo_path = os.path.join(GIS_DIR, "monteria_boundary.geojson")
cordoba_geo_path = os.path.join(GIS_DIR, "cordoba_boundary.geojson")

monteria_gdf = gpd.read_file(monteria_geo_path) if os.path.exists(monteria_geo_path) else None
cordoba_gdf = gpd.read_file(cordoba_geo_path) if os.path.exists(cordoba_geo_path) else None

print(f"Límite de Montería cargado: {monteria_gdf is not None}")
print(f"Límite de Córdoba cargado: {cordoba_gdf is not None}")

# 2. Buscar archivos de datos de accidentes en bade_datos_accidentes
data_files = glob.glob(os.path.join(DATA_DIR, "*.*"))
print(f"Archivos encontrados en bade_datos_accidentes: {len(data_files)}")

df_accidents = None

if data_files:
    for f in data_files:
        ext = os.path.splitext(f)[1].lower()
        try:
            if ext in ['.csv', '.txt']:
                temp_df = pd.read_csv(f, encoding='utf-8-sig', on_bad_lines='skip')
            elif ext in ['.xlsx', '.xls']:
                temp_df = pd.read_excel(f)
            elif ext in ['.geojson', '.json', '.shp']:
                temp_gdf = gpd.read_file(f)
                temp_df = pd.DataFrame(temp_gdf)
            else:
                continue
            
            if df_accidents is None:
                df_accidents = temp_df
            else:
                df_accidents = pd.concat([df_accidents, temp_df], ignore_index=True)
            print(f"Cargado exitosamente: {os.path.basename(f)} ({len(temp_df)} registros)")
        except Exception as e:
            print(f"Error al leer {f}: {e}")

# Si aún no hay datos en el directorio, generamos una plantilla estructurada de demostración con distribución espacial real de Montería
if df_accidents is None or len(df_accidents) == 0:
    print("\n[AVISO] No se encontraron archivos de accidentes en 'bade_datos_accidentes/'.")
    print("Generando dataset sintético realista de incidentes en Montería para demostración del pipeline GIS...")
    
    import numpy as np
    np.random.seed(42)
    
    # Coordenadas centro de Montería
    lat_center, lon_center = 8.7508, -75.8814
    
    num_samples = 250
    lats = np.random.normal(lat_center, 0.025, num_samples)
    lons = np.random.normal(lon_center, 0.025, num_samples)
    
    tipos = np.random.choice(["Choque Vehicular", "Atropello Peatón", "Volcamiento", "Caída Ocupante"], size=num_samples, p=[0.55, 0.25, 0.12, 0.08])
    gravedad = np.random.choice(["Solo Daños", "Con Heridos", "Con Muertos"], size=num_samples, p=[0.60, 0.30, 0.10])
    muertos = [np.random.randint(1, 3) if g == "Con Muertos" else 0 for g in gravedad]
    heridos = [np.random.randint(1, 4) if g == "Con Heridos" else 0 for g in gravedad]
    
    df_accidents = pd.DataFrame({
        "id_accidente": range(1, num_samples + 1),
        "latitud": lats,
        "longitud": lons,
        "tipo_accidente": tipos,
        "gravedad": gravedad,
        "fallecidos": muertos,
        "heridos": heridos,
        "fecha": pd.date_range(start="2025-01-01", periods=num_samples, freq="12h").astype(str)
    })
    
    # Guardar plantilla de demostración en CSV para que el usuario pueda usarla de referencia
    sample_path = os.path.join(DATA_DIR, "plantilla_accidentes_monteria_ejemplo.csv")
    df_accidents.to_csv(sample_path, index=False, encoding='utf-8')
    print(f"Plantilla generada y guardada en: {sample_path}")

# 3. Detectar columnas de latitud y longitud
lat_col = next((c for c in df_accidents.columns if c.lower() in ['latitud', 'lat', 'latitude', 'y']), None)
lon_col = next((c for c in df_accidents.columns if c.lower() in ['longitud', 'lon', 'lng', 'longitude', 'x']), None)

if not lat_col or not lon_col:
    print(f"Columnas detectadas en el dataset: {list(df_accidents.columns)}")
    print("ERROR: No se detectaron automáticamente las columnas de Latitud y Longitud.")
else:
    print(f"Columnas espaciales identificadas: Latitud='{lat_col}', Longitud='{lon_col}'")
    
    # Filtrar coordenadas nulas o inválidas
    df_clean = df_accidents.dropna(subset=[lat_col, lon_col]).copy()
    
    # Convertir a GeoDataFrame
    gdf_accidents = gpd.GeoDataFrame(
        df_clean,
        geometry=gpd.points_from_xy(df_clean[lon_col], df_clean[lat_col]),
        crs="EPSG:4326"
    )
    
    # Cruce Espacial (Spatial Join) con los límites de Montería
    if monteria_gdf is not None:
        gdf_monteria_accidents = gpd.sjoin(gdf_accidents, monteria_gdf, how="inner", predicate="within")
        print(f"\n--- RESULTADOS DEL CRUCE ESPACIAL ---")
        print(f"Total accidentes georreferenciados: {len(gdf_accidents)}")
        print(f"Accidentes dentro del municipio de Montería: {len(gdf_monteria_accidents)}")
    else:
        gdf_monteria_accidents = gdf_accidents

    # 4. Generación del Mapa Interactivo con Folium
    m = folium.Map(location=[8.7508, -75.8814], zoom_start=13, tiles="OpenStreetMap")
    
    # Añadir capa de frontera de Montería
    if monteria_gdf is not None:
        folium.GeoJson(
            monteria_gdf,
            name="Límite Municipio de Montería",
            style_function=lambda x: {"fillColor": "#3388ff", "color": "#003399", "weight": 2.5, "fillOpacity": 0.1}
        ).add_to(m)
        
    if cordoba_gdf is not None:
        folium.GeoJson(
            cordoba_gdf,
            name="Límite Departamento de Córdoba",
            style_function=lambda x: {"fillColor": "#ffaa00", "color": "#cc6600", "weight": 1.5, "fillOpacity": 0.05}
        ).add_to(m)
        
    # Capa de Mapa de Calor (HeatMap) de concentración de incidentes
    heat_data = [[row[lat_col], row[lon_col]] for _, row in df_clean.iterrows()]
    HeatMap(heat_data, name="Mapa de Calor (Hotspots de Accidentes)", radius=15, blur=20, min_opacity=0.4).add_to(m)
    
    # Capa de Marcadores Agrupados (Cluster)
    marker_cluster = MarkerCluster(name="Marcadores de Accidentes (Detalle)").add_to(m)
    
    for _, row in df_clean.iterrows():
        # Identificar muertes o heridos
        muertes = row.get("fallecidos", row.get("muertos", row.get("muertes", 0)))
        heridos = row.get("heridos", 0)
        gravedad = str(row.get("gravedad", "Accidente")).capitalize()
        
        color = "red" if muertes > 0 else ("orange" if heridos > 0 else "blue")
        popup_html = f"""
        <div style='font-family: Arial; width: 200px;'>
            <h4><b>{gravedad}</b></h4>
            <p><b>Fallecidos:</b> {muertes}</p>
            <p><b>Heridos:</b> {heridos}</p>
            <p><b>Coordenadas:</b> {row[lat_col]:.4f}, {row[lon_col]:.4f}</p>
        </div>
        """
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=color, icon="ambulance" if muertes > 0 else "info-sign", prefix="fa")
        ).add_to(marker_cluster)
        
    folium.LayerControl().add_to(m)
    
    # Guardar mapa interactivo HTML
    map_output_path = os.path.join(GIS_DIR, "mapa_interactivo_accidentes_monteria.html")
    m.save(map_output_path)
    print(f"\n¡Mapa interactivo generado exitosamente!")
    print(f"Archivo guardado en: {map_output_path}")

print("=== PROCESAMIENTO COMPLETADO CON ÉXITO ===")
