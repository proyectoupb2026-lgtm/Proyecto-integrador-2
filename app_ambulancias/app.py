import streamlit as st
from streamlit_folium import st_folium
import numpy as np
import random

from utils.data_loader import calculate_clusters, generate_t_ij
from models.milp import solve_milp
from models.simpy_engine import run_simulation
from utils.map_generator import create_folium_map

st.set_page_config(page_title="Gemelo Digital APH", layout="wide")

st.title("🚑 Gemelo Digital APH Montería")
st.markdown("Dashboard interactivo para la optimización y simulación de despacho de ambulancias.")

# Sidebar
st.sidebar.header("⚙️ Configuración MILP")
num_nodes = st.sidebar.number_input("Nodos de Demanda", min_value=1, value=4)
num_bases = st.sidebar.number_input("Bases Candidatas", min_value=1, value=4)
p_ambulances = st.sidebar.number_input("Flota Total", min_value=1, value=6)
T_max = st.sidebar.number_input("T_max (min)", min_value=1.0, value=10.0)
alpha = st.sidebar.slider("Penalización (Alpha)", min_value=0.0, max_value=1.0, value=0.5)

st.sidebar.header("⏱️ Simulación SimPy")
sim_days = st.sidebar.number_input("Días a simular", min_value=1, value=30)
sim_hours = sim_days * 24

if st.sidebar.button("⚡ Ejecutar Simulación", type="primary"):
    with st.spinner("Optimizando y simulando..."):
        # 1. Preparar datos
        centros = calculate_clusters(num_nodes)
        if len(centros) >= num_bases:
            base_coords = centros[:num_bases]
            node_coords = centros[:num_nodes]
            t_ij = generate_t_ij(node_coords, base_coords)
            demands = [random.randint(10, 60) for _ in range(num_nodes)]
            capacities = [max(2, p_ambulances // num_bases + 1) for _ in range(num_bases)]
        else:
            st.error("No hay suficientes datos de accidentes para los nodos/bases.")
            st.stop()

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
                    st.metric("Cobertura", f"{cov:.1f}%")
                    st.metric("Total Llamadas", len(response_times))
                
                st.subheader("📍 Asignación")
                for b, c in allocation.items():
                    if c > 0:
                        st.write(f"**Base {b}**: {c} ambulancias")

            with col2:
                st.subheader("🗺️ Mapa de Asignación")
                m = create_folium_map(allocation, num_bases, base_coords)
                st_folium(m, width=800, height=500)
else:
    # Estado inicial
    st.info("Configura los parámetros en el panel izquierdo y haz clic en Ejecutar Simulación.")
    m = create_folium_map({}, 0, [])
    st_folium(m, width="100%", height=600)
