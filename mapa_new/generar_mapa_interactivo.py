import folium
from folium.plugins import HeatMap
import pandas as pd
import os
from sklearn.cluster import KMeans
import numpy as np

def generar_mapa():
    print("Generando mapa interactivo de Montería...")
    
    # 1. Coordenadas de Montería
    monteria_coords = [8.7508, -75.8814]
    
    # 2. Crear mapa base
    m = folium.Map(location=monteria_coords, zoom_start=13, tiles='CartoDB dark_matter')
    
    # 3. Cargar datos de accidentes
    csv_path = r"C:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\accidentes_verificados_actualizados.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path, dtype={'latitud': str, 'longitud': str})
            
            # Limpiar datos: convertir a numérico, eliminar NaNs
            df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
            df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
            df_valid = df.dropna(subset=['latitud', 'longitud'])
            
            heat_data = [[row['latitud'], row['longitud']] for index, row in df_valid.iterrows()]
            
            # CAPA 1: Mapa de Calor (Accidentes)
            heatmap_layer = folium.FeatureGroup(name='🔥 Zonas de Alta Accidentalidad (Heatmap)', show=True)
            HeatMap(heat_data, radius=15, blur=20).add_to(heatmap_layer)
            heatmap_layer.add_to(m)
            
            # 4. CAPA 2: Hospitales y Clínicas (Ejemplos fijos para demostración, ya que extraer de OSM en vivo puede tardar)
            hospitales = [
                {"nombre": "Hospital San Jerónimo", "coord": [8.7554, -75.8805]},
                {"nombre": "Clínica Montería", "coord": [8.7612, -75.8833]},
                {"nombre": "Clínica Zue", "coord": [8.7681, -75.8752]},
                {"nombre": "Hospital de la Margen Izquierda", "coord": [8.7495, -75.8911]}
            ]
            
            hospital_layer = folium.FeatureGroup(name='🏥 Hospitales y Clínicas (Bases)', show=True)
            for hosp in hospitales:
                folium.Marker(
                    location=hosp["coord"],
                    popup=f"<b>{hosp['nombre']}</b><br>Base Principal",
                    icon=folium.Icon(color='green', icon='plus')
                ).add_to(hospital_layer)
            hospital_layer.add_to(m)
            
            # 5. CAPA 3: Ubicaciones Estratégicas Posibles (Ambulancias)
            # Usaremos K-Means para encontrar 4 centros de gravedad de los accidentes
            if len(heat_data) > 4:
                coords_array = np.array(heat_data)
                kmeans = KMeans(n_clusters=4, random_state=42, n_init=10).fit(coords_array)
                centros = kmeans.cluster_centers_
                
                ambulancias_layer = folium.FeatureGroup(name='🚑 Posibles Ubicaciones Ambulancias (IA)', show=False)
                for idx, centro in enumerate(centros):
                    folium.Marker(
                        location=[centro[0], centro[1]],
                        popup=f"<b>Punto Estratégico {idx+1}</b><br>Sugerido por MILP",
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(ambulancias_layer)
                ambulancias_layer.add_to(m)
            
            # Añadir control de capas
            folium.LayerControl(position='topright', collapsed=False).add_to(m)
            
            # Guardar mapa
            output_path = r"C:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\mapa_interactivo.html"
            m.save(output_path)
            print(f"¡Mapa generado con éxito en: {output_path}!")
            
        except Exception as e:
            print(f"Error procesando CSV: {e}")
    else:
        print("El archivo CSV de accidentes no se encontró.")

if __name__ == "__main__":
    generar_mapa()
