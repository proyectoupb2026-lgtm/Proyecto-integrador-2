import sys
import os

# -----------------------------------------------------------------------
# FIX: Errores de caché GPU de QtWebEngine en Windows
# -----------------------------------------------------------------------
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
os.environ["QT_WEBENGINE_DISABLE_GPU"] = "1"

import random
import numpy as np
import pandas as pd
import folium
from folium.plugins import HeatMap
from sklearn.cluster import KMeans
import pulp
import simpy

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QProgressBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QThread, pyqtSignal

# -----------------------------------------------------------------------
# Rutas base del proyecto
# -----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
GEOJSON_VIAL = os.path.join(
    PROJECT_ROOT, "MAPAS_VECTORIALES_MONTERIA_OFFLINE",
    "2_GeoJSON_Web_GIS", "monteria_malla_vial.geojson"
)
CSV_ACCIDENTES = os.path.join(PROJECT_ROOT, "bade_datos_accidentes", "accidentes_verificados_actualizados.csv")
if not os.path.exists(CSV_ACCIDENTES):
    CSV_ACCIDENTES = os.path.join(PROJECT_ROOT, "accidentes_verificados_actualizados.csv")
MAP_FILE = os.path.join(BASE_DIR, "temp_map.html")


# -----------------------------------------------------------------------
# Worker Thread: evita que la UI se congele durante la simulación
# -----------------------------------------------------------------------
class SimWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij, centros):
        super().__init__()
        self.num_nodes = num_nodes
        self.num_bases = num_bases
        self.p_ambulances = p_ambulances
        self.T_max = T_max
        self.alpha = alpha
        self.demands = demands
        self.capacities = capacities
        self.t_ij = t_ij
        self.centros = centros

    def run(self):
        try:
            # 1. Optimización MILP
            opt_res = solve_milp(
                self.num_nodes, self.num_bases, self.p_ambulances,
                self.T_max, self.alpha, self.demands, self.capacities, self.t_ij
            )
            if 'error' in opt_res:
                self.error.emit(opt_res['error'])
                return

            alloc = opt_res['allocation']

            # 2. Generar mapa actualizado
            generar_mapa(alloc, self.num_bases, self.centros)

            # 3. Simulación SimPy
            # FIX: remapear índices de bases reales a índices de t_ij secuenciales
            active_bases = [j for j, c in alloc.items() if c > 0]
            # Construir un mapa de base_id -> índice_secuencial para t_ij
            sim_res = run_simulation(alloc, self.t_ij, self.demands, self.num_bases)

            avg = float(np.mean(sim_res)) if sim_res else 0.0
            cov = (len([t for t in sim_res if t <= self.T_max]) / len(sim_res) * 100) if sim_res else 0.0
            max_t = float(np.max(sim_res)) if sim_res else 0.0

            self.finished.emit({
                'allocation': alloc,
                'objective': opt_res['objective'],
                'avg_response_time': avg,
                'coverage': cov,
                'max_response_time': max_t,
                'total_incidents': len(sim_res)
            })
        except Exception as e:
            self.error.emit(str(e))


# -----------------------------------------------------------------------
# Lógica MILP separada del widget (funciones puras)
# -----------------------------------------------------------------------
def solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij):
    """
    Resuelve el modelo MILP de cobertura estocástica de ambulancias.
    Maximiza Z = sum(d_i * y_i) - alpha * sum(d_i * v_ij)
    """
    prob = pulp.LpProblem("MILP_APH_Monteria", pulp.LpMaximize)
    I, J, K = range(num_nodes), range(num_bases), range(p_ambulances)

    # Variables de decisión
    x = pulp.LpVariable.dicts("x", ((j, k) for j in J for k in K), cat='Binary')
    y = pulp.LpVariable.dicts("y", (i for i in I), cat='Binary')
    z = pulp.LpVariable.dicts("z", ((i, j) for i in I for j in J), lowBound=0, cat='Continuous')
    v = pulp.LpVariable.dicts("v", ((i, j) for i in I for j in J), lowBound=0, cat='Continuous')

    # Función objetivo
    prob += (
        pulp.lpSum(demands[i] * y[i] for i in I)
        - alpha * pulp.lpSum(demands[i] * v[i, j] for i in I for j in J)
    )

    # Restricción 1: flota total exacta
    prob += pulp.lpSum(x[j, k] for j in J for k in K) == p_ambulances

    # Restricción 2: capacidad física de la base
    for j in J:
        prob += pulp.lpSum(x[j, k] for k in K) <= capacities[j]

    # Restricción 3: cobertura dentro de T_max
    for i in I:
        valid = [j for j in J if t_ij[i][j] <= T_max]
        if valid:
            prob += y[i] <= pulp.lpSum(x[j, k] for j in valid for k in K)
        else:
            prob += y[i] == 0  # FIX: nodo inalcanzable, no puede cubrirse

    # Restricción 4: balance de asignación de demanda
    for i in I:
        prob += pulp.lpSum(z[i, j] for j in J) == 1

    # Restricción 5: acoplamiento lógico
    for i in I:
        for j in J:
            prob += z[i, j] <= pulp.lpSum(x[j, k] for k in K)

    # Restricción 6: linealización de holgura
    for i in I:
        for j in J:
            prob += v[i, j] >= (t_ij[i][j] - T_max) * z[i, j]

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] != 'Optimal':
        return {"error": f"Sin solución óptima (estado: {pulp.LpStatus[prob.status]})"}

    allocation = {j: 0 for j in J}
    for j in J:
        for k in K:
            val = pulp.value(x[j, k])
            if val is not None and round(val) == 1:
                allocation[j] += 1

    return {"allocation": allocation, "objective": pulp.value(prob.objective)}


def run_simulation(allocation, t_ij, demands, num_bases, sim_time_hours=720):
    """
    Simulación de Eventos Discretos con SimPy.
    Genera incidentes con proceso de Poisson y despacha ambulancias.
    FIX: usa índices secuenciales para t_ij (0..num_bases-1)
    """
    env = simpy.Environment()

    # FIX: solo crear recursos para bases con ambulancias (capacity >= 1)
    bases = {}
    for j, count in allocation.items():
        if count > 0:
            bases[j] = simpy.Resource(env, capacity=count)

    if not bases:
        return []

    response_times = []

    def incident_gen(env, node_id, freq):
        if freq <= 0:
            return
        # Tiempo medio entre incidentes en horas
        mtbi = sim_time_hours / freq
        while True:
            yield env.timeout(random.expovariate(1.0 / mtbi))
            env.process(handle_inc(env, node_id))

    def handle_inc(env, node_id):
        start = env.now
        # FIX: ordenar solo entre bases activas (las que tienen ambulancias)
        active = sorted(bases.keys(), key=lambda j: t_ij[node_id][j])

        dispatched = False
        for j in active:
            if bases[j].count < bases[j].capacity:
                with bases[j].request() as req:
                    yield req
                    travel = t_ij[node_id][j] / 60.0  # minutos a horas
                    yield env.timeout(travel)
                    response_times.append((env.now - start) * 60.0)
                    # Tiempo de atención + regreso (aprox 30 min fijo)
                    yield env.timeout((30.0 + t_ij[node_id][j]) / 60.0)
                dispatched = True
                break

        if not dispatched and active:
            # Cola en la base más cercana aunque esté ocupada
            c = active[0]
            with bases[c].request() as req:
                yield req
                travel = t_ij[node_id][c] / 60.0
                yield env.timeout(travel)
                response_times.append((env.now - start) * 60.0)
                yield env.timeout((30.0 + t_ij[node_id][c]) / 60.0)

    for i, freq in enumerate(demands):
        env.process(incident_gen(env, i, freq))

    env.run(until=sim_time_hours)
    return response_times


def generar_mapa(allocation, num_bases, centros):
    """
    Genera el mapa Folium con 4 capas y lo guarda en MAP_FILE.
    Usa datos locales: GeoJSON (red vial) + CSV (accidentes).
    """
    m = folium.Map(location=[8.7508, -75.8814], zoom_start=13, tiles='OpenStreetMap')

    # Capa 0: Red Vial Offline (GeoJSON local)
    if os.path.exists(GEOJSON_VIAL):
        vial_layer = folium.FeatureGroup(name='🗺️ Red Vial (Offline)', show=False)
        folium.GeoJson(
            GEOJSON_VIAL,
            style_function=lambda x: {'color': '#4a90d9', 'weight': 1.0, 'opacity': 0.4}
        ).add_to(vial_layer)
        vial_layer.add_to(m)

    # Capa 1: Mapa de Calor de Accidentes
    if os.path.exists(CSV_ACCIDENTES):
        df = pd.read_csv(CSV_ACCIDENTES, dtype={'latitud': str, 'longitud': str})
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df_valid = df.dropna(subset=['latitud', 'longitud'])
        heat_data = [[r['latitud'], r['longitud']] for _, r in df_valid.iterrows()]
        heat_layer = folium.FeatureGroup(name='🔥 Zonas de Alta Accidentalidad', show=True)
        HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(heat_layer)
        heat_layer.add_to(m)

    # Capa 2: Bases Candidatas (Nodos MILP)
    hosp_layer = folium.FeatureGroup(name='🏥 Bases Candidatas (Nodos MILP)', show=True)
    for j in range(num_bases):
        coord = list(centros[j]) if j < len(centros) else [8.75 + random.uniform(-0.02, 0.02), -75.88 + random.uniform(-0.02, 0.02)]
        folium.CircleMarker(
            location=coord, radius=10,
            color='#FFA500', fill=True, fill_color='#FFA500', fill_opacity=0.7,
            popup=folium.Popup(f"<b>Base Candidata {j}</b>", max_width=200)
        ).add_to(hosp_layer)
    hosp_layer.add_to(m)

    # Capa 3: Ambulancias asignadas por MILP
    amb_layer = folium.FeatureGroup(name='🚑 Ambulancias Asignadas (Óptimas)', show=True)
    for j in range(num_bases):
        cant = allocation.get(j, 0)
        if cant > 0:
            coord = list(centros[j]) if j < len(centros) else [8.75 + random.uniform(-0.02, 0.02), -75.88 + random.uniform(-0.02, 0.02)]
            folium.Marker(
                location=coord,
                popup=folium.Popup(f"<b>🚑 Base {j}</b><br>Ambulancias: <b>{cant}</b>", max_width=200),
                icon=folium.Icon(color='green', icon='plus-sign', prefix='glyphicon')
            ).add_to(amb_layer)
    amb_layer.add_to(m)

    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    m.save(MAP_FILE)


# -----------------------------------------------------------------------
# Interfaz Gráfica Principal
# -----------------------------------------------------------------------
class GemeloDigitalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APH — Montería, Córdoba")
        self.setGeometry(100, 100, 1300, 820)
        self.centros = []
        self.worker = None
        self.initUI()
        # Generar mapa inicial al arrancar
        generar_mapa({}, 0, [])
        self.load_map()

    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)

        # ---- Panel Izquierdo ----
        left = QWidget()
        left.setFixedWidth(370)
        left_layout = QVBoxLayout(left)

        # Título
        title = QLabel("🚑 APH Montería")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #003366; padding: 6px;")
        left_layout.addWidget(title)

        subtitle = QLabel("Localización y Asignación Óptima de Ambulancias\nModelo MILP + SimPy | Montería, Colombia")
        subtitle.setStyleSheet("font-size: 10px; color: #555; padding: 0 6px 8px 6px;")
        left_layout.addWidget(subtitle)

        # Grupo Parámetros Globales
        param_group = QGroupBox("Parámetros del Modelo MILP")
        param_layout = QFormLayout()

        self.in_nodos = QLineEdit("4")
        self.in_bases = QLineEdit("4")
        self.in_ambulancias = QLineEdit("6")
        self.in_tmax = QLineEdit("10.0")
        self.in_alpha = QLineEdit("0.5")
        self.in_sim_hours = QLineEdit("720")

        param_layout.addRow("Nodos de demanda (|I|):", self.in_nodos)
        param_layout.addRow("Bases candidatas (|J|):", self.in_bases)
        param_layout.addRow("Flota total (p):", self.in_ambulancias)
        param_layout.addRow("T_max (minutos):", self.in_tmax)
        param_layout.addRow("Penalización (α):", self.in_alpha)
        param_layout.addRow("Horizonte simulación (h):", self.in_sim_hours)
        param_group.setLayout(param_layout)
        left_layout.addWidget(param_group)

        # Botón Ejecutar
        self.btn_simular = QPushButton("⚡ Ejecutar Simulación & Optimización")
        self.btn_simular.setStyleSheet(
            "background-color: #0078D7; color: white; padding: 10px;"
            "font-weight: bold; font-size: 12px; border-radius: 4px;"
        )
        self.btn_simular.clicked.connect(self.ejecutar)
        left_layout.addWidget(self.btn_simular)

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminado
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)

        # Grupo KPIs
        res_group = QGroupBox("Resultados KPI")
        res_layout = QVBoxLayout()

        self.lbl_obj = QLabel("Función Objetivo Z: —")
        self.lbl_avg_time = QLabel("Tiempo Medio Respuesta: — min")
        self.lbl_max_time = QLabel("Tiempo Máximo: — min")
        self.lbl_cov = QLabel("Cobertura (≤ T_max): — %")
        self.lbl_incidents = QLabel("Incidentes Simulados: —")
        self.lbl_alloc = QLabel("Asignación:\n—")
        self.lbl_alloc.setWordWrap(True)
        self.lbl_alloc.setStyleSheet("background: #f0f4ff; padding: 6px; border-radius: 4px;")

        for lbl in [self.lbl_obj, self.lbl_avg_time, self.lbl_max_time,
                    self.lbl_cov, self.lbl_incidents]:
            lbl.setStyleSheet("padding: 2px 0;")
            res_layout.addWidget(lbl)
        res_layout.addWidget(self.lbl_alloc)
        res_group.setLayout(res_layout)
        left_layout.addWidget(res_group)
        left_layout.addStretch()

        # ---- Panel Derecho: Mapa ----
        self.browser = QWebEngineView()

        main_layout.addWidget(left)
        main_layout.addWidget(self.browser)

    def load_map(self):
        """Recarga el mapa HTML en el visor web."""
        self.browser.setUrl(QUrl.fromLocalFile(MAP_FILE))

    def ejecutar(self):
        """Valida inputs, calcula centros de clusters y lanza el worker."""
        try:
            num_nodes = int(self.in_nodos.text())
            num_bases = int(self.in_bases.text())
            p_ambulances = int(self.in_ambulancias.text())
            T_max = float(self.in_tmax.text())
            alpha = float(self.in_alpha.text())
            sim_hours = float(self.in_sim_hours.text())

            # Validaciones básicas
            if num_nodes < 1 or num_bases < 1:
                QMessageBox.warning(self, "Error", "Nodos y bases deben ser ≥ 1.")
                return
            if p_ambulances < 1:
                QMessageBox.warning(self, "Error", "La flota debe ser ≥ 1.")
                return
            if T_max <= 0:
                QMessageBox.warning(self, "Error", "T_max debe ser > 0.")
                return

            # Calcular centros de demanda reales desde el CSV
            centros = self._calcular_centros_csv(num_nodes)

            # Generar datos del modelo basados en distancias reales (en minutos)
            # asumiendo velocidad comercial promedio de 30 km/h en zona urbana
            VELOCIDAD_KMH = 30.0

            if len(centros) >= num_bases:
                # Usar los mismos centros para bases y nodos
                base_coords = centros[:num_bases]
                node_coords = centros[:num_nodes]
                # t_ij en minutos = distancia Euclidiana en grados * 111 km/grado / velocidad
                t_ij = []
                for nc in node_coords:
                    row = []
                    for bc in base_coords:
                        dist_km = (((nc[0]-bc[0])*111)**2 + ((nc[1]-bc[1])*88)**2)**0.5
                        row.append(dist_km / VELOCIDAD_KMH * 60.0)
                    t_ij.append(row)
                demands = [random.randint(10, 60) for _ in range(num_nodes)]
                capacities = [max(2, p_ambulances // num_bases + 1) for _ in range(num_bases)]
                self.centros = base_coords
            else:
                # Fallback: datos aleatorios razonables
                demands = [random.randint(10, 50) for _ in range(num_nodes)]
                capacities = [max(2, p_ambulances // num_bases + 1) for _ in range(num_bases)]
                t_ij = [[random.uniform(3.0, 18.0) for _ in range(num_bases)] for _ in range(num_nodes)]
                self.centros = [[8.75 + random.uniform(-0.02, 0.02), -75.88 + random.uniform(-0.02, 0.02)] for _ in range(num_bases)]

        except ValueError:
            QMessageBox.critical(self, "Error de formato", "Verifica que todos los campos contengan números válidos.")
            return

        # Deshabilitar botón y mostrar progreso
        self.btn_simular.setEnabled(False)
        self.btn_simular.setText("⏳ Calculando...")
        self.progress.setVisible(True)

        # Lanzar en hilo separado para no congelar la UI
        self.worker = SimWorker(
            num_nodes, num_bases, p_ambulances, T_max, alpha,
            demands, capacities, t_ij, self.centros
        )
        self.worker.finished.connect(self.on_sim_done)
        self.worker.error.connect(self.on_sim_error)
        self.worker.start()

    def _calcular_centros_csv(self, n_clusters):
        """Calcula n_clusters centros geográficos desde el CSV de accidentes."""
        if not os.path.exists(CSV_ACCIDENTES):
            return []
        df = pd.read_csv(CSV_ACCIDENTES, dtype={'latitud': str, 'longitud': str})
        df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
        df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
        df_valid = df.dropna(subset=['latitud', 'longitud'])
        coords = df_valid[['latitud', 'longitud']].values
        if len(coords) < n_clusters:
            return []
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(coords)
        return kmeans.cluster_centers_.tolist()

    def on_sim_done(self, result):
        """Callback cuando el worker termina exitosamente."""
        self.btn_simular.setEnabled(True)
        self.btn_simular.setText("⚡ Ejecutar Simulación & Optimización")
        self.progress.setVisible(False)

        # Actualizar KPIs
        self.lbl_obj.setText(f"Función Objetivo Z: {result['objective']:.2f}")
        self.lbl_avg_time.setText(f"Tiempo Medio Respuesta: {result['avg_response_time']:.2f} min")
        self.lbl_max_time.setText(f"Tiempo Máximo: {result['max_response_time']:.2f} min")
        self.lbl_cov.setText(f"Cobertura (≤ T_max): {result['coverage']:.1f} %")
        self.lbl_incidents.setText(f"Incidentes Simulados: {result['total_incidents']}")

        alloc = result['allocation']
        alloc_lines = [f"  Base {b}: {c} ambulancia(s)" for b, c in alloc.items() if c > 0]
        self.lbl_alloc.setText("Asignación Óptima:\n" + "\n".join(alloc_lines) if alloc_lines else "Sin asignación")

        # Recargar mapa con las nuevas posiciones
        self.load_map()

    def on_sim_error(self, msg):
        """Callback cuando el worker reporta un error."""
        self.btn_simular.setEnabled(True)
        self.btn_simular.setText("⚡ Ejecutar Simulación & Optimización")
        self.progress.setVisible(False)
        QMessageBox.critical(self, "Error en la simulación", msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = GemeloDigitalApp()
    window.show()
    sys.exit(app.exec_())
