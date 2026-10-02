from geopy.geocoders import Nominatim, ArcGIS
import geopandas as gpd
from shapely.geometry import Point
import time
import json

# Cargar límite
boundary_path = 'mapa_GIS_Monteria/monteria_boundary.geojson'
gdf = gpd.read_file(boundary_path)
poly = gdf.geometry.iloc[0]

nom = Nominatim(user_agent='monteria_audit_v4')
arc = ArcGIS()

queries = [
    ('ZC_01', 'Glorieta de Mocarí', ['Glorieta Mocarí, Montería, Colombia', 'Mocarí, Montería, Colombia', 'Glorieta Mocarí']),
    ('ZC_02', 'Malibú / Vía Cereté', ['Club Campestre Malibú, Montería, Colombia', 'Malibú, Montería, Colombia', 'Los Garzones, Montería, Colombia', 'Garzones, Montería, Colombia', 'Urbanización Los Garzones, Montería']),
    ('ZC_03', 'Unicor', ['Universidad de Córdoba, Montería, Colombia', 'Unicor, Montería, Colombia']),
    ('ZC_04', 'Circunvalar Calle 41', ['Avenida Circunvalar, Montería, Colombia', 'Alamedas del Sinú, Montería, Colombia', 'Calle 41 con Circunvalar, Montería']),
    ('ZC_05', 'Centro', ['Parque Simón Bolívar, Montería, Colombia', 'Centro, Montería, Colombia']),
    ('ZC_06', 'Glorieta de las Vacas', ['Glorieta de las Vacas, Montería, Colombia', 'Terminal de Transportes de Montería, Colombia', 'Glorieta Terminal de Transportes, Montería']),
    ('ZC_07', 'Cantaclaro', ['Cantaclaro, Montería, Colombia', 'Barrio Cantaclaro, Montería, Colombia']),
    ('ZC_08', 'La Granja', ['La Granja, Montería, Colombia', 'Barrio La Granja, Montería, Colombia']),
    ('ZC_09', 'Mogambo', ['Mogambo, Montería, Colombia', 'Barrio Mogambo, Montería, Colombia']),
    ('ZC_10', 'Rancho Grande', ['Rancho Grande, Montería, Colombia', 'Barrio Rancho Grande, Montería, Colombia']),
    ('ZC_11', 'Pringamosa / El Dorado', ['El Dorado, Montería, Colombia', 'Barrio El Dorado, Montería, Colombia', 'Pringamosa, Montería, Colombia']),
    ('ZC_12', 'Los Pericos', ['Los Pericos, Montería, Colombia', 'Vereda Los Pericos, Montería, Colombia', 'Entrada Los Pericos, Montería']),
    ('ZC_13', 'Loma Grande', ['Loma Grande, Montería, Colombia', 'Vereda Loma Grande, Montería, Colombia', 'Relleno Sanitario Loma Grande, Montería'])
]

results = []

for zid, name, qlist in queries:
    print(f"\n==================== {zid}: {name} ====================")
    found = False
    for q in qlist:
        # Nominatim first
        try:
            time.sleep(1.0)
            res_n = nom.geocode(q)
            if res_n:
                pt = Point(res_n.longitude, res_n.latitude)
                in_poly = poly.contains(pt)
                print(f"  [NOM] '{q}' -> ({res_n.latitude:.6f}, {res_n.longitude:.6f}) | InPoly: {in_poly} | {res_n.address[:80]}")
        except Exception as e:
            print(f"  [NOM Error] {e}")
            
        # ArcGIS fallback/comparison
        try:
            time.sleep(0.5)
            res_a = arc.geocode(q)
            if res_a:
                pt_a = Point(res_a.longitude, res_a.latitude)
                in_poly_a = poly.contains(pt_a)
                print(f"  [ARC] '{q}' -> ({res_a.latitude:.6f}, {res_a.longitude:.6f}) | InPoly: {in_poly_a} | {res_a.address[:80]}")
        except Exception as e:
            print(f"  [ARC Error] {e}")
