# Gemelo Digital APH Montería - Streamlit App
import sys
import os
import streamlit as st

# Configurar path e importar módulos sin problemas de caché
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

for m in list(sys.modules.keys()):
    if m.startswith('utils') or m.startswith('models'):
        sys.modules.pop(m, None)

from streamlit_folium import st_folium
import numpy as np
import random

try:
    from utils.data_loader import calculate_clusters, generate_t_ij, load_candidatos, load_zonas_demanda
    from models.milp import solve_milp
    from models.simpy_engine import run_simulation
    from utils.map_generator import create_folium_map
except ImportError:
    from app_ambulancias.utils.data_loader import calculate_clusters, generate_t_ij, load_candidatos, load_zonas_demanda
    from app_ambulancias.models.milp import solve_milp
    from app_ambulancias.models.simpy_engine import run_simulation
    from app_ambulancias.utils.map_generator import create_folium_map

st.set_page_config(page_title="Gemelo Digital APH Montería", layout="wide")

st.title("🚑 Gemelo Digital APH Montería")
st.markdown("Dashboard interactivo para la optimización MILP y simulación SimPy de despacho de ambulancias en **Montería, Córdoba**.")

# Cargar fuentes oficiales
df_cand_global = load_candidatos()
df_zonas_global = load_zonas_demanda()

max_bases = len(df_cand_global) if not df_cand_global.empty else 7
max_zonas = len(df_zonas_global) if not df_zonas_global.empty else 13

# Sidebar
st.sidebar.header("⚙️ Configuración MILP")
num_nodes = st.sidebar.number_input("Nodos de Demanda (Zonas Montería)", min_value=1, max_value=max_zonas, value=min(13, max_zonas))
num_bases = st.sidebar.number_input("Bases Candidatas (Hospitales/Clínicas)", min_value=1, max_value=max_bases, value=min(7, max_bases))
p_ambulances = st.sidebar.number_input("Flota Total de Ambulancias", min_value=1, value=6)
T_max = st.sidebar.number_input("T_max Respuesta (min)", min_value=1.0, value=10.0)
alpha = st.sidebar.slider("Penalización Exceso Tiempo (Alpha)", min_value=0.0, max_value=1.0, value=0.5)

st.sidebar.header("⏱️ Simulación SimPy")
sim_days = st.sidebar.number_input("Días a simular", min_value=1, value=30)
sim_hours = sim_days * 24

if st.sidebar.button("⚡ Ejecutar Simulación", type="primary"):
    with st.spinner("Optimizando modelo MILP y ejecutando simulación estocástica..."):
        # 1. Preparar datos
        if not df_cand_global.empty and not df_zonas_global.empty:
            base_coords = df_cand_global[['lat', 'lon']].values.tolist()[:num_bases]
            node_coords = df_zonas_global[['lat', 'lon']].values.tolist()[:num_nodes]
            # Ponderación de demanda usando el conteo validado
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

        # 2. MILP
        opt_res = solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij)
        if "error" in opt_res:
            st.error(opt_res["error"])
        else:
            allocation = opt_res["allocation"]

            # 3. Simulación
            response_times = run_simulation(allocation, t_ij, demands, sim_hours)
            
            # Layout de Resultados
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("📊 Resultados KPIs")
                st.metric("Z* (Función Objetivo)", f"{opt_res['objective']:.2f}")
                
                if response_times:
                    avg_t = np.mean(response_times)
                    max_t = np.max(response_times)
                    cov = len([t for t in response_times if t <= T_max]) / len(response_times) * 100
                    st.metric("Tiempo Medio Resp.", f"{avg_t:.2f} min")
                    st.metric("Tiempo Máx", f"{max_t:.2f} min")
                    st.metric("Cobertura (≤ T_max)", f"{cov:.1f}%")
                    st.metric("Total Incidentes Atendidos", len(response_times))
                
                st.subheader("📍 Asignación Óptima")
                for b, c in allocation.items():
                    if c > 0:
                        h_name = df_cand_global.iloc[b]['nombre'] if not df_cand_global.empty and b < len(df_cand_global) else f"Base {b}"
                        st.write(f"🚑 **{h_name}**: `{c} ambulancia(s)`")

            with col2:
                st.subheader("🗺️ Mapa de Despliegue en Montería")
                m = create_folium_map(allocation, num_bases, base_coords)
                st_folium(m, width=800, height=520)
else:
    # Estado inicial
    st.info("Configura los parámetros en el panel izquierdo y haz clic en **Ejecutar Simulación**.")
    m = create_folium_map({}, num_bases, [])
    st_folium(m, width="100%", height=600)
