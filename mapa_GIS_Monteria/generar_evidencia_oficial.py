import geopandas as gpd
from shapely.geometry import Point
import numpy as np
import pandas as pd
import json
import time
from geopy.geocoders import Nominatim, ArcGIS

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return float(2 * R * np.arcsin(np.sqrt(a)))

# Cargar polígono límite
boundary_path = 'mapa_GIS_Monteria/monteria_boundary.geojson'
gdf_boundary = gpd.read_file(boundary_path)
poly_monteria = gdf_boundary.geometry.iloc[0]

nom = Nominatim(user_agent="auditoria_geocodificacion_monteria_definitiva_2026")
arc = ArcGIS()

zonas_config = [
    {
        'id_zona': 'ZC_01',
        'nombre': 'Glorieta de Mocarí',
        'sector': 'Norte (Acceso Anillo Vial / Mocarí)',
        'lat_actual': 8.795200,
        'lon_actual': -75.862100,
        'consultas': [
            ('Nominatim', 'Mocarí, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Glorieta Mocarí, Montería, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_02',
        'nombre': 'Malibú / Vía Cereté (Garzones)',
        'sector': 'Norte Oriente (Corredor Aeropuerto)',
        'lat_actual': 8.815000,
        'lon_actual': -75.835000,
        'consultas': [
            ('ArcGIS', 'Barrio Los Garzones, Montería, Córdoba'),
            ('Nominatim', 'Los Garzones, Montería, Córdoba, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_03',
        'nombre': 'Universidad de Córdoba (Unicor)',
        'sector': 'Norte (Carrera 6 / Corredor Educativo)',
        'lat_actual': 8.784000,
        'lon_actual': -75.857000,
        'consultas': [
            ('Nominatim', 'Universidad de Córdoba, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Universidad de Córdoba, Montería, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_04',
        'nombre': 'Avenida Circunvalar / Calle 41',
        'sector': 'Centro Oriente (Arteria Principal / Alamedas)',
        'lat_actual': 8.758000,
        'lon_actual': -75.873000,
        'consultas': [
            ('Nominatim', 'Centro Comercial Alamedas del Sinú, Montería, Colombia'),
            ('Nominatim', 'Avenida Circunvalar, Montería, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_05',
        'nombre': 'Sector Centro (Carreras 2 a 6)',
        'sector': 'Centro Histórico y Administrativo',
        'lat_actual': 8.751000,
        'lon_actual': -75.885000,
        'consultas': [
            ('Nominatim', 'Parque Simón Bolívar, Montería, Córdoba, Colombia'),
            ('Nominatim', 'Centro, Montería, Córdoba, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_06',
        'nombre': 'Glorieta de las Vacas / Terminal',
        'sector': 'Centro Oriente (Anillo Vial / Calle 41)',
        'lat_actual': 8.745100,
        'lon_actual': -75.863300,
        'consultas': [
            ('Nominatim', 'Terminal de Transportes de Montería, Colombia'),
            ('ArcGIS', 'Terminal de Transportes de Montería, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_07',
        'nombre': 'Cantaclaro',
        'sector': 'Oriente (Sector Residencial y Comercial)',
        'lat_actual': 8.738700,
        'lon_actual': -75.863200,
        'consultas': [
            ('Nominatim', 'Cantaclaro, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Cantaclaro, Montería, Córdoba')
        ]
    },
    {
        'id_zona': 'ZC_08',
        'nombre': 'La Granja (Diagonal 21 / Cra 24F)',
        'sector': 'Sur Occidente (Núcleo Urbano Sur)',
        'lat_actual': 8.736000,
        'lon_actual': -75.889000,
        'consultas': [
            ('Nominatim', 'La Granja, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'La Granja, Montería, Córdoba')
        ]
    },
    {
        'id_zona': 'ZC_09',
        'nombre': 'Mogambo / Calle 4 Sur',
        'sector': 'Sur (Eje Residencial Sur Oriental)',
        'lat_actual': 8.729000,
        'lon_actual': -75.875000,
        'consultas': [
            ('Nominatim', 'Mogambo, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Mogambo, Montería, Córdoba')
        ]
    },
    {
        'id_zona': 'ZC_10',
        'nombre': 'Rancho Grande (Margen Izquierda)',
        'sector': 'Centro Occidente (Margen Izquierda)',
        'lat_actual': 8.758000,
        'lon_actual': -75.901000,
        'consultas': [
            ('Nominatim', 'Rancho Grande, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Rancho Grande, Montería, Córdoba')
        ]
    },
    {
        'id_zona': 'ZC_11',
        'nombre': 'Pringamosa / El Dorado',
        'sector': 'Norte Occidente (Margen Izquierda)',
        'lat_actual': 8.771700,
        'lon_actual': -75.893900,
        'consultas': [
            ('Nominatim', 'Barrio el Dorado, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Pringamosa, Montería, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_12',
        'nombre': 'Los Pericos / Troncal Oriental',
        'sector': 'Oriente (Salida Troncal a Planeta Rica)',
        'lat_actual': 8.762000,
        'lon_actual': -75.842000,
        'consultas': [
            ('ArcGIS', 'Los Pericos, Montería, Córdoba'),
            ('Nominatim', 'Los Pericos, Montería, Córdoba, Colombia')
        ]
    },
    {
        'id_zona': 'ZC_13',
        'nombre': 'Loma Grande',
        'sector': 'Sur Oriente Periurbano',
        'lat_actual': 8.705829,
        'lon_actual': -75.843551,
        'consultas': [
            ('Nominatim', 'Loma Grande, Montería, Córdoba, Colombia'),
            ('ArcGIS', 'Loma Grande, Montería, Córdoba')
        ]
    }
]

registros = []

print("=== EJECUTANDO GEOCODIFICACIÓN FORMAL Y COMPARATIVA ===")

for z in zonas_config:
    zid = z['id_zona']
    nombre = z['nombre']
    
    loc_sel = None
    serv_sel = None
    q_sel = None
    osm_id = None
    osm_type = None
    
    for serv, q in z['consultas']:
        try:
            time.sleep(1.0)
            if serv == 'Nominatim':
                loc = nom.geocode(q, timeout=10)
                if loc:
                    loc_sel = loc
                    serv_sel = serv
                    q_sel = q
                    osm_id = str(loc.raw.get('osm_id', ''))
                    osm_type = str(loc.raw.get('osm_type', ''))
                    break
            elif serv == 'ArcGIS':
                loc = arc.geocode(q, timeout=10)
                if loc:
                    loc_sel = loc
                    serv_sel = serv
                    q_sel = q
                    osm_id = 'ArcGIS_Locator'
                    osm_type = 'Feature'
                    break
        except Exception as e:
            print(f"Error {serv} con query '{q}': {e}")
            
    if loc_sel:
        lat_g = float(loc_sel.latitude)
        lon_g = float(loc_sel.longitude)
        addr = str(loc_sel.address)
    else:
        lat_g = z['lat_actual']
        lon_g = z['lon_actual']
        serv_sel = 'No localizado'
        q_sel = 'N/A'
        addr = 'N/A'
        
    dist_m = haversine_m(z['lat_actual'], z['lon_actual'], lat_g, lon_g)
    
    pt_g = Point(lon_g, lat_g)
    pt_a = Point(z['lon_actual'], z['lat_actual'])
    
    in_poly_g = bool(poly_monteria.contains(pt_g))
    in_poly_a = bool(poly_monteria.contains(pt_a))
    dist_border_g = float(poly_monteria.boundary.distance(pt_g) * 111320.0)
    
    rec = {
        'id_zona': zid,
        'nombre_zona': nombre,
        'sector_general': z['sector'],
        'servicio': serv_sel,
        'query_ejecutada': q_sel,
        'osm_id': osm_id,
        'osm_type': osm_type,
        'direccion_completa_encontrada': addr,
        'lat_actual_codigo': round(z['lat_actual'], 6),
        'lon_actual_codigo': round(z['lon_actual'], 6),
        'lat_geocodificada': round(lat_g, 6),
        'lon_geocodificada': round(lon_g, 6),
        'distancia_diff_m': round(dist_m, 1),
        'diferencia_gt_300m': bool(dist_m > 300.0),
        'dentro_monteria_boundary_actual': in_poly_a,
        'dentro_monteria_boundary_geocodificada': in_poly_g,
        'distancia_al_borde_m': round(dist_border_g, 1)
    }
    registros.append(rec)
    print(f"[{zid}] {nombre:30s} | {serv_sel:9s} -> ({lat_g:.5f}, {lon_g:.5f}) | Diff: {dist_m:6.1f}m | En Polígono: {in_poly_g}")

# Guardar archivos
with open('mapa_GIS_Monteria/evidencia_geocodificacion_zonas.json', 'w', encoding='utf-8') as f:
    json.dump(registros, f, ensure_ascii=False, indent=2)

df_out = pd.DataFrame(registros)
df_out.to_csv('mapa_GIS_Monteria/evidencia_geocodificacion_zonas.csv', index=False, encoding='utf-8-sig')

print("\nArchivos guardados en mapa_GIS_Monteria/evidencia_geocodificacion_zonas.csv y .json exitosamente.")
