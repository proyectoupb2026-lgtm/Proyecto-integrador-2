# Gemelo Digital APH Montería - Streamlit App
import sys
import os
import streamlit as st
import numpy as np
import random
import uuid
import pandas as pd
from datetime import datetime

# Configurar path e importar módulos sin problemas de caché
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

for m in list(sys.modules.keys()):
    if m.startswith('utils') or m.startswith('models'):
        sys.modules.pop(m, None)

from streamlit_folium import st_folium

try:
    from utils.data_loader import calculate_clusters, generate_t_ij, load_candidatos, load_zonas_demanda
    from models.milp import solve_milp
    from models.simpy_engine import run_simulation
    from utils.map_generator import create_folium_map
    from utils.route_calculator import calculate_real_road_route
except ImportError:
    from app_ambulancias.utils.data_loader import calculate_clusters, generate_t_ij, load_candidatos, load_zonas_demanda
    from app_ambulancias.models.milp import solve_milp
    from app_ambulancias.models.simpy_engine import run_simulation
    from app_ambulancias.utils.map_generator import create_folium_map
    from app_ambulancias.utils.route_calculator import calculate_real_road_route

st.set_page_config(page_title="Gemelo Digital APH", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

:root {
    --primary-color: #0369a1;      /* Azul institucional */
    --primary-light: #f0f9ff;
    --accent-color: #dc2626;       /* Rojo alertas */
    --accent-light: #fef2f2;
    --success-color: #16a34a;      /* Verde confirmación/disponible */
    --bg-color: #f8fafc;           /* Gris claro fondo */
    --card-border: #e2e8f0;
    --text-main: #334155;
    --text-muted: #64748b;
}

/* Tarjetas y Contenedores Custom */
.custom-card {
    background-color: white;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 1rem;
}

/* Botones redondeados */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Títulos */
h1, h2, h3, h4, h5 {
    color: var(--text-main) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
}

p, span, div {
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if "app_stage" not in st.session_state:
    st.session_state.app_stage = "CONFIG"
if "opt_res" not in st.session_state:
    st.session_state.opt_res = None
if "fleet_status" not in st.session_state:
    st.session_state.fleet_status = {}
if "active_incidents" not in st.session_state:
    st.session_state.active_incidents = []
if "incident_counter" not in st.session_state:
    st.session_state.incident_counter = 1000
if "custom_lat" not in st.session_state:
    st.session_state.custom_lat = 8.75
    st.session_state.custom_lon = -75.88
if "custom_zone_name" not in st.session_state:
    st.session_state.custom_zone_name = "Centro de Montería"
if "prev_clicked" not in st.session_state:
    st.session_state.prev_clicked = None


# --- LOAD DATA ---
@st.cache_data
def get_data():
    return load_candidatos(), load_zonas_demanda()

df_cand_global, df_zonas_global = get_data()
max_bases = len(df_cand_global) if not df_cand_global.empty else 7
max_zonas = len(df_zonas_global) if not df_zonas_global.empty else 13

# --- MAIN LAYOUT ---
st.title("Gemelo Digital APH Montería")
st.markdown("Plataforma interactiva para optimización, simulación y ruteo en tiempo real de emergencias médicas.")

import math
def get_interpolated_coord_by_dist(path, progress):
    if progress <= 0: return path[0]
    if progress >= 1: return path[-1]
    def dist(p1, p2):
        return math.sqrt(((p1[0]-p2[0])*111)**2 + ((p1[1]-p2[1])*88)**2)
    segments = []
    total_dist = 0
    for i in range(len(path)-1):
        d = dist(path[i], path[i+1])
        segments.append(d)
        total_dist += d
    if total_dist == 0: return path[0]
    target_d = total_dist * progress
    accum = 0
    for i in range(len(path)-1):
        if accum + segments[i] >= target_d:
            excess = target_d - accum
            frac = excess / segments[i] if segments[i] > 0 else 0
            return [path[i][0] + (path[i+1][0] - path[i][0])*frac, path[i][1] + (path[i+1][1] - path[i][1])*frac]
        accum += segments[i]
    return path[-1]

# ==========================================================
# STAGE: CONFIGURACIÓN INICIAL
# ==========================================================
if st.session_state.app_stage == "CONFIG":
    st.info("Paso 1: Configura los parámetros iniciales y genera el despliegue óptimo de ambulancias.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Parámetros del Modelo (MILP)")
        num_nodes = st.number_input("Nodos de Demanda (Zonas Montería)", min_value=1, max_value=max_zonas, value=min(13, max_zonas))
        num_bases_hosp = st.number_input("Hospitales/Clínicas Candidatos", min_value=1, max_value=max_bases, value=min(7, max_bases))
        incluir_estrategicos = st.checkbox("Incluir Puntos Estratégicos (Intersecciones clave) como bases candidatas", value=True)
        
        p_ambulances = st.number_input("Flota Total de Ambulancias", min_value=1, value=6)
        T_max = st.number_input("T_max Respuesta (minutos)", min_value=1.0, value=10.0)
        alpha = st.slider("Penalización Exceso Tiempo (Alpha)", min_value=0.0, max_value=1.0, value=0.5)
        
        traffic_scenario = st.radio(
            "Escenario de Tráfico",
            ["Hora Valle (Fluido - 1.0x)", "Hora Pico (Congestión - 1.6x)"]
        )
        st.session_state.traffic_factor = 1.6 if "1.6x" in traffic_scenario else 1.0
        
        if st.button("Iniciar Simulación", type="primary", use_container_width=True):
            with st.spinner("Calculando ubicación óptima con MILP..."):
                # Preparar datos
                df_cand_local = df_cand_global.copy()
                
                # Agregar puntos estratégicos si se selecciona
                if incluir_estrategicos:
                    puntos_extra = calculate_clusters(5)  # 5 puntos estratégicos adicionales
                    extra_data = []
                    for idx, pt in enumerate(puntos_extra):
                        extra_data.append({
                            'nombre': f'Punto Estratégico {idx+1}',
                            'lat': pt[0], 'lon': pt[1], 'direccion': 'Vía Pública / Intersección'
                        })
                    df_extra = pd.DataFrame(extra_data)
                    df_cand_local = pd.concat([df_cand_local, df_extra], ignore_index=True)
                
                num_bases = min(num_bases_hosp + (5 if incluir_estrategicos else 0), len(df_cand_local))
                st.session_state.df_cand_activa = df_cand_local # Guardar el df con los estratégicos

                if not df_cand_local.empty and not df_zonas_global.empty:
                    base_coords = df_cand_local[['lat', 'lon']].values.tolist()[:num_bases]
                    node_coords = df_zonas_global[['lat', 'lon']].values.tolist()[:num_nodes]
                    demands = []
                    for _, r in df_zonas_global.iloc[:num_nodes].iterrows():
                        acc = int(r.get('accidentes_reales_asignados', 0))
                        demands.append(max(15, acc * 12 if acc > 0 else 20))
                    capacities = [max(2, p_ambulances // num_bases + 1) for _ in range(num_bases)]
                    t_ij = generate_t_ij(node_coords, base_coords)
                else:
                    centros = calculate_clusters(num_nodes)
                    base_coords = centros[:num_bases]
                    node_coords = centros[:num_nodes]
                    t_ij = generate_t_ij(node_coords, base_coords)
                    demands = [random.randint(10, 60) for _ in range(num_nodes)]
                    capacities = [max(2, p_ambulances // num_bases + 1) for _ in range(num_bases)]
                
                # Ejecutar MILP
                opt_res = solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij)
                
                if "error" not in opt_res:
                    st.session_state.opt_res = opt_res
                    st.session_state.base_coords = base_coords
                    st.session_state.node_coords = node_coords
                    st.session_state.num_bases = num_bases
                    st.session_state.T_max = T_max
                    st.session_state.t_ij = t_ij
                    st.session_state.demands = demands
                    
                    # Inicializar flota
                    allocation = opt_res["allocation"]
                    fleet = {}
                    for b, cant in allocation.items():
                        if cant > 0:
                            h_n = df_cand_local.iloc[b]['nombre'] if not df_cand_local.empty and b < len(df_cand_local) else f"Base {b}"
                            fleet[b] = {
                                'name': h_n,
                                'total': cant,
                                'available': cant,
                                'busy': 0
                            }
                    st.session_state.fleet_status = fleet
                    st.session_state.active_incidents = []
                    st.session_state.app_stage = "LIVE"
                    st.rerun()
                else:
                    st.error(opt_res["error"])
    
    with col2:
        st.write("### Descripción del Sistema")
        st.write("Esta herramienta te permite ubicar matemáticamente una flota de ambulancias en Montería basándose en datos históricos, y luego simular el despacho en tiempo real a emergencias.")

# ==========================================================
# STAGE: SIMULACIÓN EN VIVO
# ==========================================================
elif st.session_state.app_stage == "LIVE":
    
    # --- HEADER PANEL ---
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.subheader("Panel de Operaciones en Vivo")
    with col_head2:
        if st.button("Detener y Reconfigurar", use_container_width=True):
            st.session_state.app_stage = "CONFIG"
            st.rerun()
            
    if 'global_sim_time' not in st.session_state:
        st.session_state.global_sim_time = 0
    
    # --- MAPA PRINCIPAL ---
    st.markdown("#### Mapa de Despliegue en Tiempo Real")
    
    # Recoger coordenadas destino pre-despacho
    target_lat = st.session_state.custom_lat
    target_lon = st.session_state.custom_lon
    
    active_routes = []
    if st.session_state.active_incidents:
        for inc in st.session_state.active_incidents:
            elapsed = st.session_state.global_sim_time - inc['start_sim_time']
            travel_t = inc['route_data']['travel_time_min']
            
            if elapsed < 0: elapsed = 0
            progress = min(1.0, elapsed / travel_t) if travel_t > 0 else 1.0
            
            current_pos = get_interpolated_coord_by_dist(inc['route_data']['path_coords'], progress)
            status_text = "En Camino" if progress < 1.0 else "En Escena"
            
            active_routes.append({
                'path_coords': inc['route_data']['path_coords'],
                'hospital_name': inc['hospital_name'],
                'zone_name': inc['zone_name'],
                'distance_km': inc['route_data']['distance_km'],
                'travel_time_min': travel_t,
                'progress': progress,
                'current_pos': current_pos,
                'status': status_text
            })

    pending_lat = target_lat if True else None
    pending_lon = target_lon if True else None

    m = create_folium_map(st.session_state.opt_res["allocation"], st.session_state.num_bases, st.session_state.base_coords, active_routes=active_routes, pending_lat=pending_lat, pending_lon=pending_lon)
    map_data = st_folium(m, width="100%", height=600, key="main_map")
    
    current_clicked = map_data.get("last_clicked") if map_data else None
    if current_clicked and current_clicked != st.session_state.prev_clicked:
        st.session_state.custom_lat = current_clicked["lat"]
        st.session_state.custom_lon = current_clicked["lng"]
        st.session_state.custom_zone_name = "Coordenada Elegida en Mapa"
        st.session_state.prev_clicked = current_clicked
        st.rerun()

    # --- PANEL DE DESPACHO ---
    st.markdown("---")
    st.markdown("#### Despacho de Unidades")
    
    col_d1, col_d2, col_d3 = st.columns([1, 1.5, 1])
    
    with col_d1:
        sim_mode = st.radio("Modo de Selección", ["Zonas Históricas", "Ubicación Personalizada"])
        
    with col_d2:
        if sim_mode == "Zonas Históricas":
            if not df_zonas_global.empty:
                df_zonas_sorted = df_zonas_global.sort_values(by='accidentes_reales_asignados', ascending=False).reset_index(drop=True)
                zonas_options = [f"{r['id_zona']} - {r['barrio_zona']}" for _, r in df_zonas_sorted.iterrows()]
                selected_zone_str = st.selectbox("Seleccionar Zona", options=zonas_options)
                sel_id = selected_zone_str.split(" - ")[0]
                sel_row = df_zonas_sorted[df_zonas_sorted['id_zona'] == sel_id].iloc[0]
                st.session_state.custom_lat = sel_row['lat']
                st.session_state.custom_lon = sel_row['lon']
                st.session_state.custom_zone_name = f"{sel_row['id_zona']}: {sel_row['barrio_zona']}"
        else:
            custom_address = st.text_input("Buscar dirección por texto:", placeholder="Ej: Parque Simón Bolívar")
            if st.button("Buscar"):
                try:
                    from geopy.geocoders import Nominatim
                    geolocator = Nominatim(user_agent="monteria_aph_digital_twin")
                    location = geolocator.geocode(f"{custom_address}, Montería, Colombia")
                    if location:
                        st.session_state.custom_lat = location.latitude
                        st.session_state.custom_lon = location.longitude
                        st.session_state.custom_zone_name = f"Búsqueda: {custom_address}"
                        st.rerun()
                    else:
                        st.warning("Dirección no encontrada.")
                except Exception as e:
                    pass

    target_lat = st.session_state.custom_lat
    target_lon = st.session_state.custom_lon
    zone_name = st.session_state.custom_zone_name

    with col_d3:
        st.write(" ")
        st.write(" ")
        if st.button("DESPACHAR AMBULANCIA", type="primary", use_container_width=True):
            available_bases = [b for b, data in st.session_state.fleet_status.items() if data['available'] > 0]
            
            if not available_bases:
                st.error("CRÍTICO: No hay ambulancias disponibles en ninguna base.")
            else:
                with st.spinner("Calculando mejor ruta en la red vial..."):
                    base_coords = st.session_state.base_coords
                    distances = []
                    for b in available_bases:
                        b_lat, b_lon = base_coords[b]
                        d_straight = (((target_lat - b_lat)*111)**2 + ((target_lon - b_lon)*88)**2)**0.5
                        distances.append((b, d_straight))
                    distances.sort(key=lambda x: x[1])
                    top_candidates = [x[0] for x in distances[:3]]
                    
                    best_base = None
                    best_route_data = None
                    min_time = float('inf')
                    
                    for b in top_candidates:
                        start_lat, start_lon = base_coords[b]
                        r_data = calculate_real_road_route(start_lat, start_lon, target_lat, target_lon, speed_kmh=30.0, traffic_factor=st.session_state.traffic_factor)
                        if r_data['travel_time_min'] < min_time:
                            min_time = r_data['travel_time_min']
                            best_route_data = r_data
                            best_base = b
                    
                    route_data = best_route_data
                
                st.session_state.fleet_status[best_base]['available'] -= 1
                st.session_state.fleet_status[best_base]['busy'] += 1
                
                st.session_state.incident_counter += 1
                incident_id = f"#{st.session_state.incident_counter}"
                
                st.session_state.active_incidents.append({
                    'id': incident_id,
                    'zone_name': zone_name,
                    'base_id': best_base,
                    'hospital_name': st.session_state.fleet_status[best_base]['name'],
                    'route_data': route_data,
                    'start_sim_time': st.session_state.global_sim_time,
                    'time_dispatched': datetime.now().strftime("%H:%M:%S")
                })
                st.success(f"Despachada unidad desde {st.session_state.fleet_status[best_base]['name']}")
                st.rerun()

    # --- INCIDENTES Y ESTADO DE FLOTA ---
    st.markdown("---")
    col_inc, col_flota = st.columns([2, 1])
    
    with col_inc:
        st.markdown("#### Incidentes Activos")
        if not st.session_state.active_incidents:
            st.info("No hay incidentes activos en este momento.")
        else:
            for idx, inc in enumerate(st.session_state.active_incidents):
                elapsed = st.session_state.global_sim_time - inc['start_sim_time']
                ttime = inc['route_data']['travel_time_min']
                progress = min(1.0, max(0, elapsed / ttime)) if ttime > 0 else 1.0
                
                border_color = "var(--success-color)" if ttime <= st.session_state.T_max else "var(--accent-color)"
                status_color = "#0284c7" if progress < 1.0 else "#16a34a"
                status_text = "En Camino" if progress < 1.0 else "Llegó a la Escena"
                
                html_card = f"""<div class="custom-card" style="border-left: 4px solid {border_color}; padding: 1rem; margin-bottom: 0.5rem;"><div style="display: flex; justify-content: space-between; align-items: center;"><div style="width: 100%;"><div style="display: flex; justify-content: space-between;"><h5 style="margin: 0; color: {border_color} !important;">Emergencia Médica {inc['id']}</h5><span style="background-color: {status_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;">{status_text}</span></div><p style="margin: 4px 0 0 0; font-size: 0.9em;">Destino: {inc['zone_name']}</p><p style="margin: 2px 0 0 0; font-size: 0.85em; color: var(--text-muted);">Asignación: {inc['hospital_name']} • Llegada en {ttime} min</p></div></div></div>"""
                st.markdown(html_card, unsafe_allow_html=True)
                
                if st.button(f"Completar y Liberar Unidad", key=f"btn_{inc['id']}"):
                    b_id = inc['base_id']
                    st.session_state.fleet_status[b_id]['available'] += 1
                    st.session_state.fleet_status[b_id]['busy'] -= 1
                    st.session_state.active_incidents.pop(idx)
                    st.rerun()

    with col_flota:
        st.markdown("#### Estado de Flota")
        for b, stats in st.session_state.fleet_status.items():
            st.markdown(f"""
            <div class="custom-card" style="padding: 1rem; margin-bottom: 0.5rem;">
                <h5 style="margin-top: 0;">{stats['name']}</h5>
                <div style="display: flex; justify-content: space-between; font-size: 0.9em; font-weight: 600;">
                    <span style="color: var(--success-color);">Libres: {stats['available']}</span>
                    <span style="color: var(--accent-color);">Ocupadas: {stats['busy']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- MÉTRICAS GLOBALES ---
    st.markdown("---")
    with st.expander("Métricas Globales (Documento Técnico)"):
        col_m1, col_m2 = st.columns([1, 2])
        with col_m1:
            st.metric("Función Objetivo MILP (Z*)", f"{st.session_state.opt_res['objective']:.2f}")
        
        with col_m2:
            st.markdown("#### Simulación Estocástica (SimPy)")
            sim_days = st.number_input("Días de Simulación", value=30, min_value=1)
            if st.button("Ejecutar Simulación"):
                with st.spinner("Corriendo simulaciones..."):
                    response_times = run_simulation(st.session_state.opt_res["allocation"], st.session_state.t_ij, st.session_state.demands, sim_days*24)
                    if response_times:
                        avg_t = np.mean(response_times)
                        cov = len([t for t in response_times if t <= st.session_state.T_max]) / len(response_times) * 100
                        c1, c2 = st.columns(2)
                        c1.metric("Tiempo Medio de Respuesta", f"{avg_t:.2f} min")
                        c2.metric("Cobertura Global (≤ T_max)", f"{cov:.1f}%")
