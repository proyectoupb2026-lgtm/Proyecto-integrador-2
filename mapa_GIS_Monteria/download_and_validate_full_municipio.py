import requests
import json
import geopandas as gpd
from shapely.geometry import shape, Point

headers = {'User-Agent': 'monteria_full_municipio_downloader_v1'}

# 1. Fetch relation 1343449 from Nominatim with polygon_geojson
url = 'https://nominatim.openstreetmap.org/details'
params = {
    'osmtype': 'R',
    'osmid': 1343449,
    'polygon_geojson': 1,
    'format': 'json'
}

r = requests.get(url, params=params, headers=headers)
data = r.json()

geojson_geom = data.get('geometry')
if not geojson_geom:
    # Fallback to search lookup
    lookup_url = 'https://nominatim.openstreetmap.org/lookup'
    r2 = requests.get(lookup_url, params={'osm_ids': 'R1343449', 'polygon_geojson': 1, 'format': 'json'}, headers=headers)
    data2 = r2.json()
    geojson_geom = data2[0].get('geojson')
    props = {
        'osm_id': 1343449,
        'osm_type': 'relation',
        'admin_level': 6,
        'name': 'Municipio de Montería',
        'display_name': data2[0].get('display_name')
    }
else:
    props = {
        'osm_id': 1343449,
        'osm_type': 'relation',
        'admin_level': 6,
        'name': 'Municipio de Montería',
        'display_name': 'Municipio de Montería, Córdoba, Colombia'
    }

feature_collection = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": props,
            "geometry": geojson_geom
        }
    ]
}

target_file = 'mapa_GIS_Monteria/monteria_municipio_completo.geojson'
with open(target_file, 'w', encoding='utf-8') as f:
    json.dump(feature_collection, f, ensure_ascii=False, indent=2)

print(f"Polígono municipal completo guardado en {target_file}")

# Validar point-in-polygon
poly_municipio = shape(geojson_geom)

puntos_test = [
    ('ZC_01 Glorieta Mocarí', 8.800470, -75.855003),
    ('ZC_02 Los Garzones', 8.824900, -75.842290),
    ('ZC_03 Unicor', 8.790424, -75.861793),
    ('ZC_04 Circunvalar Cll 41', 8.763296, -75.873706),
    ('ZC_05 Centro', 8.755898, -75.886984),
    ('ZC_06 Glorieta de las Vacas', 8.748558, -75.867643),
    ('ZC_07 Cantaclaro', 8.740323, -75.867316),
    ('ZC_08 La Granja', 8.737990, -75.894669),
    ('ZC_09 Mogambo', 8.728639, -75.881794),
    ('ZC_10 Rancho Grande', 8.752114, -75.907972),
    ('ZC_11 El Dorado', 8.764055, -75.899484),
    ('ZC_12 Los Pericos', 8.742540, -75.834670),
    ('ZC_13 Loma Grande', 8.694447, -75.841499),
]

print("\n=== VALIDACIÓN POINT-IN-POLYGON CONTRA MUNICIPIO COMPLETO (admin_level 6) ===")
todos_dentro = True
for nom, lat, lon in puntos_test:
    pt = Point(lon, lat)
    dentro = poly_municipio.contains(pt)
    if not dentro:
        todos_dentro = False
    print(f"{nom:28s} | ({lat:.6f}, {lon:.6f}) | Dentro del Municipio Completo: {dentro}")

print(f"\n¿Las 13 zonas caen 100% dentro del Municipio de Montería?: {todos_dentro}")
