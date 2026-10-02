import geopandas as gpd
from shapely.geometry import Point
import geopy
from geopy.geocoders import Nominatim, ArcGIS
import time
import numpy as np
import json
import pandas as pd

# 1. Cargar polígono límite de Montería
boundary_path = 'mapa_GIS_Monteria/monteria_boundary.geojson'
gdf_boundary = gpd.read_file(boundary_path)
poly_monteria = gdf_boundary.geometry.iloc[0]

# 2. Inicializar geocodificadores
geolocator_nom = Nominatim(user_agent="investigacion_aph_monteria_audit_v3")
geolocator_arc = ArcGIS()

# Las 13 zonas actuales
zonas_actuales = [
    {
        'id_zona': 'ZC_01',
        'nombre': 'Glorieta de Mocarí',
        'query_nom': 'Glorieta de Mocarí, Montería, Córdoba, Colombia',
        'query_alt': 'Mocarí, Montería, Córdoba, Colombia',
        'lat_actual': 8.795200,
        'lon_actual': -75.862100
    },
    {
        'id_zona': 'ZC_02',
        'nombre': 'Malibú / Vía Cereté',
        'query_nom': 'Club Campestre Malibú, Montería, Córdoba, Colombia',
        'query_alt': 'Vía Montería - Cereté, Montería, Córdoba, Colombia',
        'lat_actual': 8.815000,
        'lon_actual': -75.835000
    },
    {
        'id_zona': 'ZC_03',
        'nombre': 'Universidad de Córdoba (Unicor)',
        'query_nom': 'Universidad de Córdoba, Montería, Córdoba, Colombia',
        'query_alt': 'Unicor, Montería, Córdoba, Colombia',
        'lat_actual': 8.784000,
        'lon_actual': -75.857000
    },
    {
        'id_zona': 'ZC_04',
        'nombre': 'Avenida Circunvalar / Calle 41',
        'query_nom': 'Avenida Circunvalar con Calle 41, Montería, Córdoba, Colombia',
        'query_alt': 'Centro Comercial Alamedas del Sinú, Montería, Córdoba, Colombia',
        'lat_actual': 8.758000,
        'lon_actual': -75.873000
    },
    {
        'id_zona': 'ZC_05',
        'nombre': 'Sector Centro (Carreras 2 a 6)',
        'query_nom': 'Parque Simón Bolívar, Montería, Córdoba, Colombia',
        'query_alt': 'Centro, Montería, Córdoba, Colombia',
        'lat_actual': 8.751000,
        'lon_actual': -75.885000
    },
    {
        'id_zona': 'ZC_06',
        'nombre': 'Glorieta de las Vacas / Terminal',
        'query_nom': 'Terminal de Transportes de Montería, Montería, Córdoba, Colombia',
        'query_alt': 'Glorieta de las Vacas, Montería, Córdoba, Colombia',
        'lat_actual': 8.745100,
        'lon_actual': -75.863300
    },
    {
        'id_zona': 'ZC_07',
        'nombre': 'Cantaclaro',
        'query_nom': 'Barrio Cantaclaro, Montería, Córdoba, Colombia',
        'query_alt': 'Cantaclaro, Montería, Córdoba, Colombia',
        'lat_actual': 8.738700,
        'lon_actual': -75.863200
    },
    {
        'id_zona': 'ZC_08',
        'nombre': 'La Granja (Diagonal 21 / Cra 24F)',
        'query_nom': 'Barrio La Granja, Montería, Córdoba, Colombia',
        'query_alt': 'La Granja, Montería, Córdoba, Colombia',
        'lat_actual': 8.736000,
        'lon_actual': -75.889000
    },
    {
        'id_zona': 'ZC_09',
        'nombre': 'Mogambo / Calle 4 Sur',
        'query_nom': 'Barrio Mogambo, Montería, Córdoba, Colombia',
        'query_alt': 'Mogambo, Montería, Córdoba, Colombia',
        'lat_actual': 8.729000,
        'lon_actual': -75.875000
    },
    {
        'id_zona': 'ZC_10',
        'nombre': 'Rancho Grande (Margen Izquierda)',
        'query_nom': 'Barrio Rancho Grande, Montería, Córdoba, Colombia',
        'query_alt': 'Rancho Grande, Montería, Córdoba, Colombia',
        'lat_actual': 8.758000,
        'lon_actual': -75.901000
    },
    {
        'id_zona': 'ZC_11',
        'nombre': 'Pringamosa / El Dorado',
        'query_nom': 'Barrio El Dorado, Montería, Córdoba, Colombia',
        'query_alt': 'El Dorado, Montería, Córdoba, Colombia',
        'lat_actual': 8.771700,
        'lon_actual': -75.893900
    },
    {
        'id_zona': 'ZC_12',
        'nombre': 'Los Pericos / Troncal Oriental',
        'query_nom': 'Los Pericos, Montería, Córdoba, Colombia',
        'query_alt': 'Vía Montería - Planeta Rica, Montería, Córdoba, Colombia',
        'lat_actual': 8.762000,
        'lon_actual': -75.842000
    },
    {
        'id_zona': 'ZC_13',
        'nombre': 'Loma Grande',
        'query_nom': 'Loma Grande, Montería, Córdoba, Colombia',
        'query_alt': 'Vereda Loma Grande, Montería, Córdoba, Colombia',
        'lat_actual': 8.705829,
        'lon_actual': -75.843551
    }
]

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

resultados = []

print("=== INICIANDO GEOCODIFICACIÓN FORMAL Y VALIDACIÓN ESPACIAL ===")
for z in zonas_actuales:
    zid = z['id_zona']
    nombre = z['nombre']
    q_nom = z['query_nom']
    q_alt = z['query_alt']
    
    # 1. Intentar Nominatim
    loc = None
    servicio = "Nominatim"
    used_query = q_nom
    try:
        time.sleep(1.1)
        loc = geolocator_nom.geocode(q_nom, timeout=10)
        if not loc:
            time.sleep(1.1)
            used_query = q_alt
            loc = geolocator_nom.geocode(q_alt, timeout=10)
    except Exception as e:
        print(f"[{zid}] Error Nominatim: {e}")
        
    # 2. Si falla Nominatim, usar ArcGIS
    if not loc:
        try:
            time.sleep(1.0)
            servicio = "ArcGIS"
            used_query = q_nom
            loc = geolocator_arc.geocode(q_nom, timeout=10)
            if not loc:
                used_query = q_alt
                loc = geolocator_arc.geocode(q_alt, timeout=10)
        except Exception as e:
            print(f"[{zid}] Error ArcGIS: {e}")
            
    if loc:
        lat_geo = loc.latitude
        lon_geo = loc.longitude
        disp_name = loc.address
        dist_m = haversine_m(z['lat_actual'], z['lon_actual'], lat_geo, lon_geo)
        
        # Test Point in Polygon
        pt = Point(lon_geo, lat_geo)
        inside_geo = poly_monteria.contains(pt)
        
        # Test original coordinate
        pt_act = Point(z['lon_actual'], z['lat_actual'])
        inside_act = poly_monteria.contains(pt_act)
        
        res = {
            'id_zona': zid,
            'nombre': nombre,
            'servicio': servicio,
            'query': used_query,
            'display_name': disp_name,
            'lat_actual': z['lat_actual'],
            'lon_actual': z['lon_actual'],
            'lat_geocodificada': lat_geo,
            'lon_geocodificada': lon_geo,
            'distancia_diff_m': round(dist_m, 1),
            'cambio_significativo_gt_300m': dist_m > 300,
            'dentro_poligono_geocodificada': inside_geo,
            'dentro_poligono_actual': inside_act
        }
    else:
        res = {
            'id_zona': zid,
            'nombre': nombre,
            'servicio': 'No encontrado',
            'query': used_query,
            'display_name': 'No resuelto',
            'lat_actual': z['lat_actual'],
            'lon_actual': z['lon_actual'],
            'lat_geocodificada': z['lat_actual'],
            'lon_geocodificada': z['lon_actual'],
            'distancia_diff_m': 0.0,
            'cambio_significativo_gt_300m': False,
            'dentro_poligono_geocodificada': poly_monteria.contains(Point(z['lon_actual'], z['lat_actual'])),
            'dentro_poligono_actual': poly_monteria.contains(Point(z['lon_actual'], z['lat_actual']))
        }
    resultados.append(res)
    print(f"[{zid}] {nombre}: {servicio} -> ({res['lat_geocodificada']:.5f}, {res['lon_geocodificada']:.5f}) | Diff: {res['distancia_diff_m']}m | Dentro: {res['dentro_poligono_geocodificada']}")

# Guardar evidencia en JSON
with open('mapa_GIS_Monteria/evidencia_geocodificacion_zonas.json', 'w', encoding='utf-8') as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

# Guardar evidencia en CSV
df_res = pd.DataFrame(resultados)
df_res.to_csv('mapa_GIS_Monteria/evidencia_geocodificacion_zonas.csv', index=False, encoding='utf-8-sig')
print("\nEvidencia guardada en JSON y CSV exitosamente.")
