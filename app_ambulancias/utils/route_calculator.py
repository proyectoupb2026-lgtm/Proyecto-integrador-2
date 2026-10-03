import os
import pickle
import time
import numpy as np
import geopandas as gpd
import networkx as nx
from scipy.spatial import KDTree

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GEOJSON_ROAD = os.path.join(BASE_DIR, "mapa_GIS_Monteria", "monteria_road_network.geojson")
CACHE_PKL = os.path.join(BASE_DIR, "mapa_GIS_Monteria", "monteria_graph_cache.pkl")

_GRAPH = None
_TREE = None
_COORDS_ARR = None

def get_road_graph():
    """Carga o reconstruye el grafo de red vial de Montería de forma ultra eficiente."""
    global _GRAPH, _TREE, _COORDS_ARR
    if _GRAPH is not None and _TREE is not None:
        return _GRAPH, _TREE, _COORDS_ARR

    # 1. Intentar cargar desde caché .pkl
    if os.path.exists(CACHE_PKL):
        try:
            with open(CACHE_PKL, 'rb') as f:
                data = pickle.load(f)
                _GRAPH = data['graph']
                _TREE = data['tree']
                _COORDS_ARR = data['coords_arr']
                return _GRAPH, _TREE, _COORDS_ARR
        except Exception as e:
            print(f"Error cargando caché pkl: {e}")

    # 2. Reconstruir desde GeoJSON si no hay caché
    if not os.path.exists(GEOJSON_ROAD):
        return None, None, None

    gdf = gpd.read_file(GEOJSON_ROAD)
    G = nx.Graph()
    node_coords = []
    node_ids = {}

    def get_node_id(pt):
        coords = (round(pt[1], 6), round(pt[0], 6))
        if coords not in node_ids:
            nid = len(node_coords)
            node_ids[coords] = nid
            node_coords.append(coords)
            G.add_node(nid, lat=coords[0], lon=coords[1])
        return node_ids[coords]

    for idx, row in gdf.iterrows():
        geom = row.geometry
        if geom and geom.geom_type == 'LineString':
            coords_list = list(geom.coords)
            u_id = get_node_id(coords_list[0])
            v_id = get_node_id(coords_list[-1])
            length_m = float(row.get('length', 10.0))
            line_path = [[round(pt[1], 6), round(pt[0], 6)] for pt in coords_list]
            G.add_edge(u_id, v_id, weight=length_m, path=line_path)

    _COORDS_ARR = np.array(node_coords)
    _TREE = KDTree(_COORDS_ARR)
    _GRAPH = G

    # Guardar caché para ejecuciones futuras
    try:
        with open(CACHE_PKL, 'wb') as f:
            pickle.dump({'graph': G, 'tree': _TREE, 'coords_arr': _COORDS_ARR}, f)
    except Exception as e:
        print(f"No se pudo guardar caché: {e}")

    return _GRAPH, _TREE, _COORDS_ARR

def calculate_real_road_route(start_lat, start_lon, end_lat, end_lon, speed_kmh=30.0, traffic_factor=1.0):
    """
    Calcula la ruta real navegable entre dos puntos GPS usando la malla vial de Montería.
    traffic_factor: 1.0 para Hora Valle, 1.6 para Hora Pico.
    """
    G, tree, coords_arr = get_road_graph()
    if G is None or tree is None:
        # Fallback euclidiano si no hay red vial
        dist_km = (((start_lat - end_lat)*111)**2 + ((start_lon - end_lon)*88)**2)**0.5
        eff_speed = speed_kmh / traffic_factor
        travel_time_min = (dist_km / eff_speed) * 60.0
        return {
            'distance_km': round(dist_km, 2),
            'travel_time_min': round(travel_time_min, 2),
            'path_coords': [[start_lat, start_lon], [end_lat, end_lon]],
            'is_fallback': True
        }

    # Búsqueda de nodos más cercanos
    dist_start, u_idx = tree.query([start_lat, start_lon])
    dist_end, v_idx = tree.query([end_lat, end_lon])

    try:
        path_nodes = nx.shortest_path(G, source=u_idx, target=v_idx, weight='weight')
        dist_m = nx.shortest_path_length(G, source=u_idx, target=v_idx, weight='weight')
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        # Fallback en caso de nodos inconexos
        dist_km = (((start_lat - end_lat)*111)**2 + ((start_lon - end_lon)*88)**2)**0.5
        eff_speed = speed_kmh / traffic_factor
        travel_time_min = (dist_km / eff_speed) * 60.0
        return {
            'distance_km': round(dist_km, 2),
            'travel_time_min': round(travel_time_min, 2),
            'path_coords': [[start_lat, start_lon], [end_lat, end_lon]],
            'is_fallback': True
        }

    # Reconstruir coordenadas continuas de la ruta
    full_path_coords = [[start_lat, start_lon]]
    for i in range(len(path_nodes) - 1):
        n1 = path_nodes[i]
        n2 = path_nodes[i+1]
        edge_data = G.get_edge_data(n1, n2)
        if edge_data and 'path' in edge_data:
            segment_path = edge_data['path']
            # Asegurar orientación del segmento
            pt1 = segment_path[0]
            n1_coord = (round(G.nodes[n1]['lat'], 6), round(G.nodes[n1]['lon'], 6))
            if pt1 != list(n1_coord):
                segment_path = list(reversed(segment_path))
            full_path_coords.extend(segment_path)
        else:
            full_path_coords.append([G.nodes[n2]['lat'], G.nodes[n2]['lon']])

    full_path_coords.append([end_lat, end_lon])

    dist_km = dist_m / 1000.0
    effective_speed = speed_kmh / traffic_factor
    travel_time_min = (dist_km / effective_speed) * 60.0

    return {
        'distance_km': round(dist_km, 2),
        'travel_time_min': round(travel_time_min, 2),
        'path_coords': full_path_coords,
        'is_fallback': False
    }
