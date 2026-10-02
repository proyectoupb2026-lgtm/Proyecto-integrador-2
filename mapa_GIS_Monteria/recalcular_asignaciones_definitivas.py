import pandas as pd
import numpy as np
import json

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return float(2 * R * np.arcsin(np.sqrt(a)))

df_ev = pd.read_csv('mapa_GIS_Monteria/evidencia_geocodificacion_zonas.csv')
zonas = df_ev.to_dict('records')

df_acc = pd.read_csv('bade_datos_accidentes/accidentes_verificados_actualizados.csv')
df_m = df_acc[df_acc['municipio'] == 'Montería']
df_fid = df_m[~((df_m['latitud'].round(4) == 8.7508) & (df_m['longitud'].round(4) == -75.8814))]

print(f"Total accidentes fidedignos de Montería: {len(df_fid)}")

# 1. Enfoque por radio estricto de 1.5 km
print("\n--- ENFOQUE 1: Radio estricto de <= 1.5 km (1500m) ---")
conteo_radio_1500 = {z['id_zona']: [] for z in zonas}
for _, acc in df_fid.iterrows():
    aid = int(acc['id'])
    for z in zonas:
        d = haversine_m(acc['latitud'], acc['longitud'], z['lat_geocodificada'], z['lon_geocodificada'])
        if d <= 1500.0:
            conteo_radio_1500[z['id_zona']].append(aid)

for z in zonas:
    c = conteo_radio_1500[z['id_zona']]
    print(f"[{z['id_zona']}] {z['nombre_zona']:30s} | Conteo (<=1.5km): {len(c):2d} | IDs: {c}")

# 2. Enfoque de partición Voronoi / zona más cercana
print("\n--- ENFOQUE 2: Partición única (zona más cercana si dist <= 2.0 km) ---")
asignacion_cercana = {z['id_zona']: [] for z in zonas}
rurales_aislados = []

for _, acc in df_fid.iterrows():
    aid = int(acc['id'])
    dists = []
    for z in zonas:
        d = haversine_m(acc['latitud'], acc['longitud'], z['lat_geocodificada'], z['lon_geocodificada'])
        dists.append((d, z['id_zona']))
    dists.sort()
    min_d, best_zid = dists[0]
    if min_d <= 2000.0:
        asignacion_cercana[best_zid].append((aid, round(min_d, 1)))
    else:
        rurales_aislados.append((aid, str(acc['barrio_sector']), round(min_d, 1)))

for z in zonas:
    c = asignacion_cercana[z['id_zona']]
    ids = [x[0] for x in c]
    print(f"[{z['id_zona']}] {z['nombre_zona']:30s} | Conteo Partición: {len(ids):2d} | IDs: {ids}")

print(f"\nAccidentes rurales lejanos (> 2.0 km de cualquier zona): {len(rurales_aislados)}")
for r in rurales_aislados:
    print(f"  ID {r[0]:3d} ({r[1]}): a {r[2]}m de la zona más cercana")
