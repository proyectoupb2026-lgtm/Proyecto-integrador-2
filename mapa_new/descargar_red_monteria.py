import osmnx as ox
import os

# Definir la ubicación y el tipo de red (en este caso, calles transitables para vehículos)
place_name = "Montería, Córdoba, Colombia"
network_type = "drive" # Solo vías para automóviles

print(f"Descargando la red vial para: {place_name}")
try:
    # Descargar el grafo desde OpenStreetMap
    G = ox.graph_from_place(place_name, network_type=network_type)
    
    print("Red vial descargada exitosamente. Procesando...")
    
    # Directorio de salida
    output_dir = r"C:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\datos_viales_monteria\street_map"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Guardar el grafo en formato GraphML (Útil para cargar después con NetworkX/OSMnx)
    graphml_path = os.path.join(output_dir, "monteria_network.graphml")
    ox.save_graphml(G, filepath=graphml_path)
    print(f"Grafo guardado en: {graphml_path}")
    
    # 2. (Opcional) Trazar y guardar una imagen de la red vial
    fig_path = os.path.join(output_dir, "monteria_street_map.png")
    fig, ax = ox.plot_graph(G, show=False, save=True, filepath=fig_path, node_size=0, edge_linewidth=0.5)
    print(f"Imagen del mapa guardada en: {fig_path}")

except Exception as e:
    print(f"Ocurrió un error al intentar descargar los datos: {e}")
