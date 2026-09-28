import osmnx as ox
import geopandas as gpd
import os

os.makedirs("mapa_GIS_Monteria", exist_ok=True)

print("Descargando límite vectorial de Montería...")
monteria_gdf = ox.geocode_to_gdf("Monteria, Colombia")
monteria_gdf.to_file("mapa_GIS_Monteria/monteria_boundary.geojson", driver="GeoJSON")
print("Montería descargado.")

print("Descargando límite vectorial del Departamento de Córdoba...")
cordoba_gdf = ox.geocode_to_gdf("Cordoba, Colombia")
cordoba_gdf.to_file("mapa_GIS_Monteria/cordoba_boundary.geojson", driver="GeoJSON")
print("Córdoba descargado.")

print("Descargando red vial urbana (drive) de Montería...")
G_monteria = ox.graph_from_place("Monteria, Colombia", network_type="drive")
nodes_gdf, edges_gdf = ox.graph_to_gdfs(G_monteria)
edges_gdf.to_file("mapa_GIS_Monteria/monteria_road_network.geojson", driver="GeoJSON")
print("Red vial descargada exitosamente.")

print("¡Proceso completado! Archivos GeoJSON generados en mapa_GIS_Monteria/")
