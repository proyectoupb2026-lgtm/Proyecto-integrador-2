import requests
import json
import geopandas as gpd
from shapely.geometry import shape, Point

# Check Nominatim search for Monteria admin_level=6
headers = {'User-Agent': 'monteria_full_boundary_fetcher_v1'}

# 1. First test Nominatim with osm_type=relation and lookup or search
url = 'https://nominatim.openstreetmap.org/search'
params = {
    'q': 'Montería, Córdoba, Colombia',
    'format': 'json',
    'polygon_geojson': 1,
    'extratags': 1
}

r = requests.get(url, params=params, headers=headers)
data = r.json()
print(f"Results for search: {len(data)}")
for i, item in enumerate(data):
    print(f"[{i}] osm_type: {item.get('osm_type')}, osm_id: {item.get('osm_id')}, class: {item.get('class')}, type: {item.get('type')}, display: {item.get('display_name')[:80]}")
    tags = item.get('extratags', {})
    print(f"    admin_level: {tags.get('admin_level')}, place: {tags.get('place')}")

# Also check overpass query specifically for admin_level 6 in Cordoba
query = """
[out:json][timeout:30];
area["ISO3166-2"="CO-COR"]->.cordoba;
relation["admin_level"="6"](area.cordoba);
out tags;
"""
try:
    r_op = requests.post('https://overpass-api.de/api/interpreter', data={'data': query}, headers=headers, timeout=30)
    if r_op.status_code == 200:
        op_data = r_op.json()
        print(f"\nMunicipalities (admin_level 6) in Cordoba found: {len(op_data.get('elements', []))}")
        for el in op_data.get('elements', []):
            tags = el.get('tags', {})
            print(f"  ID: {el.get('id')} | Name: {tags.get('name')} | admin_level: {tags.get('admin_level')}")
    else:
        print(f"Overpass failed with status {r_op.status_code}")
except Exception as e:
    print(f"Overpass error: {e}")
