import pandas as pd
import json
import numpy as np

def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlam = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1)*np.cos(phi2)*np.sin(dlam/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

df_acc = pd.read_csv('bade_datos_accidentes/accidentes_verificados_actualizados.csv')
df_monteria = df_acc[df_acc['municipio'] == 'Montería']
df_fidedignos = df_monteria[~((df_monteria['latitud'].round(4) == 8.7508) & (df_monteria['longitud'].round(4) == -75.8814))]

with open('mapa_GIS_Monteria/evidencia_geocodificacion_zonas.json', 'r', encoding='utf-8') as f:
    zonas = json.load(f)

print(f"Total accidentes fidedignos en Montería: {len(df_fidedignos)}")

tot_act_unique = set()
tot_geo_unique = set()

for z in zonas:
    ids_act = []
    ids_geo = []
    
    for _, acc in df_fidedignos.iterrows():
        d_act = haversine_m(z['lat_actual_codigo'], z['lon_actual_codigo'], acc['latitud'], acc['longitud'])
        if d_act <= 1500:
            ids_act.append(int(acc['id']))
            tot_act_unique.add(int(acc['id']))
            
        d_geo = haversine_m(z['lat_geocodificada'], z['lon_geocodificada'], acc['latitud'], acc['longitud'])
        if d_geo <= 1500:
            ids_geo.append(int(acc['id']))
            tot_geo_unique.add(int(acc['id']))
            
    print(f"[{z['id_zona']}] {z['nombre_zona'][:28]:28s} | Act: {len(ids_act):2d} {str(ids_act):22s} | Geo: {len(ids_geo):2d} {str(ids_geo):22s}")

print(f"\nTotal accidentes cubiertos (actuales): {len(tot_act_unique)} de 23")
print(f"Total accidentes cubiertos (geocodificados): {len(tot_geo_unique)} de 23")
