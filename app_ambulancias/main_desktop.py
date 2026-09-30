import sys
import os
import random
import numpy as np

# FIX: Errores de caché GPU de QtWebEngine en Windows
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-software-rasterizer"
os.environ["QT_WEBENGINE_DISABLE_GPU"] = "1"

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QGroupBox, QMessageBox, QProgressBar, QFrame
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QThread, pyqtSignal, Qt

# Importar los nuevos módulos limpios
from utils.data_loader import calculate_clusters, generate_t_ij
from utils.map_generator import create_folium_map
from models.milp import solve_milp
from models.simpy_engine import run_simulation

MAP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_map.html")

# -----------------------------------------------------------------------
# Estilos CSS (Tema Oscuro Moderno)
# -----------------------------------------------------------------------
LIGHT_THEME = """
QMainWindow, QWidget {
    background-color: #f1f5f9;
    color: #0f172a;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QGroupBox {
    font-weight: bold;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 15px;
    color: #0284c7;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
}
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #94a3b8;
    border-radius: 4px;
    padding: 5px;
    color: #0f172a;
}
QPushButton {
    background-color: #0284c7;
    color: white;
    border-radius: 6px;
    padding: 10px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #0369a1;
}
QPushButton:disabled {
    background-color: #cbd5e1;
    color: #64748b;
}
QLabel {
    font-size: 13px;
}
#TitleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #0284c7;
}
#KpiBox {
    background-color: #ffffff;
    border-radius: 6px;
    padding: 10px;
}
"""

class SimWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, num_nodes, num_bases, p_ambulances, T_max, alpha, sim_hours):
        super().__init__()
        self.params = (num_nodes, num_bases, p_ambulances, T_max, alpha, sim_hours)

    def run(self):
        try:
            n_nodes, n_bases, p_amb, T_max, alpha, sim_hrs = self.params
            
            # 1. Datos
            centros = calculate_clusters(n_nodes)
            if len(centros) < n_bases:
                self.error.emit("Faltan datos de accidentes para calcular nodos.")
                return
                
            base_coords = centros[:n_bases]
            node_coords = centros[:n_nodes]
            t_ij = generate_t_ij(node_coords, base_coords)
            demands = [random.randint(10, 60) for _ in range(n_nodes)]
            capacities = [max(2, p_amb // n_bases + 1) for _ in range(n_bases)]
            
            # 2. MILP
            opt_res = solve_milp(n_nodes, n_bases, p_amb, T_max, alpha, demands, capacities, t_ij)
            if 'error' in opt_res:
                self.error.emit(opt_res['error'])
                return
            
            alloc = opt_res['allocation']
            
            # 3. Simulación
            sim_res = run_simulation(alloc, t_ij, demands, sim_hrs)
            
            # 4. Mapa
            m = create_folium_map(alloc, n_bases, base_coords)
            m.save(MAP_FILE)
            
            avg = float(np.mean(sim_res)) if sim_res else 0.0
            cov = (len([t for t in sim_res if t <= T_max]) / len(sim_res) * 100) if sim_res else 0.0
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


class GemeloDigitalDesktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador APH — Interfaz Local")
        self.setGeometry(100, 100, 1300, 850)
        self.setStyleSheet(LIGHT_THEME)
        self.initUI()
        
        # Generar mapa vacío
        m = create_folium_map({}, 0, [])
        m.save(MAP_FILE)
        self.load_map()

    def initUI(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ---- PANEL IZQUIERDO ----
        left = QWidget()
        left.setFixedWidth(350)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 15, 0)

        # Header
        title = QLabel("🚑 Simulador APH")
        title.setObjectName("TitleLabel")
        left_layout.addWidget(title)
        
        sub = QLabel("Optimización y Simulación Local")
        sub.setStyleSheet("color: #64748b; font-size: 11px; margin-bottom: 10px;")
        left_layout.addWidget(sub)

        # Formulario
        grp_param = QGroupBox("Configuración MILP y SimPy")
        form = QFormLayout()
        
        self.in_nodos = QLineEdit("4")
        self.in_bases = QLineEdit("4")
        self.in_ambul = QLineEdit("6")
        self.in_tmax = QLineEdit("10.0")
        self.in_alpha = QLineEdit("0.5")
        self.in_dias = QLineEdit("30")
        
        form.addRow("Nodos (Siniestros):", self.in_nodos)
        form.addRow("Bases Candidatas:", self.in_bases)
        form.addRow("Flota Total (p):", self.in_ambul)
        form.addRow("T_max (min):", self.in_tmax)
        form.addRow("Penalización (α):", self.in_alpha)
        form.addRow("Días a simular:", self.in_dias)
        
        grp_param.setLayout(form)
        left_layout.addWidget(grp_param)

        # Botón
        self.btn = QPushButton("⚡ Ejecutar Simulación")
        self.btn.clicked.connect(self.ejecutar)
        left_layout.addWidget(self.btn)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)

        # KPIs
        grp_kpi = QGroupBox("Resultados de la Simulación")
        kpi_lay = QVBoxLayout()
        
        self.lbl_z = QLabel("Z*: —")
        self.lbl_t = QLabel("T. Medio: —")
        self.lbl_cov = QLabel("Cobertura: —")
        self.lbl_max = QLabel("T. Máximo: —")
        self.lbl_inc = QLabel("Llamadas: —")
        self.lbl_alloc = QLabel("Asignación:\n—")
        self.lbl_alloc.setWordWrap(True)
        self.lbl_alloc.setStyleSheet("color: #059669; font-weight: bold; margin-top: 10px;")
        
        for l in [self.lbl_z, self.lbl_t, self.lbl_cov, self.lbl_max, self.lbl_inc]:
            kpi_lay.addWidget(l)
            
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #cbd5e1;")
        kpi_lay.addWidget(line)
        
        kpi_lay.addWidget(self.lbl_alloc)
        grp_kpi.setLayout(kpi_lay)
        left_layout.addWidget(grp_kpi)

        # Leyenda de Capas
        grp_capas = QGroupBox("¿Qué hace cada Capa en el Mapa?")
        capas_lay = QVBoxLayout()
        capas_lay.setSpacing(5)
        
        lbl_c1 = QLabel("🗺️ <b>Red Vial:</b> Dibuja las calles de Montería para calcular las rutas reales.")
        lbl_c2 = QLabel("🔥 <b>Alta Accidentalidad:</b> Mapa de calor (rojo) mostrando dónde ocurren más siniestros.")
        lbl_c5 = QLabel("📍 <b>Puntos de Siniestros (Radial):</b> Círculos rojos cuyo tamaño crece según la cantidad de accidentes (frecuencia) en ese punto exacto.")
        lbl_c3 = QLabel("🏥 <b>Bases Candidatas:</b> Puntos naranjas donde el sistema <i>podría</i> ubicar ambulancias.")
        lbl_c4 = QLabel("🚑 <b>Ambulancias Asignadas:</b> Marcadores verdes indicando dónde <i>decidió</i> ubicar la flota.")
        
        for l in [lbl_c1, lbl_c2, lbl_c5, lbl_c3, lbl_c4]:
            l.setWordWrap(True)
            l.setStyleSheet("font-size: 11px; color: #475569; margin-bottom: 5px;")
            capas_lay.addWidget(l)
            
        grp_capas.setLayout(capas_lay)
        left_layout.addWidget(grp_capas)
        
        # Controles Adicionales
        ctrl_lay = QHBoxLayout()
        
        self.btn_reset = QPushButton("🔄 Reiniciar")
        self.btn_reset.setStyleSheet("background-color: #64748b; color: white;")
        self.btn_reset.clicked.connect(self.reiniciar_app)
        
        self.btn_close = QPushButton("❌ Cerrar")
        self.btn_close.setStyleSheet("background-color: #ef4444; color: white;")
        self.btn_close.clicked.connect(self.close)
        
        ctrl_lay.addWidget(self.btn_reset)
        ctrl_lay.addWidget(self.btn_close)
        
        left_layout.addLayout(ctrl_lay)
        
        left_layout.addStretch()

        # ---- PANEL DERECHO ----
        self.browser = QWebEngineView()
        
        main_layout.addWidget(left)
        main_layout.addWidget(self.browser)

    def load_map(self):
        self.browser.setUrl(QUrl.fromLocalFile(MAP_FILE))

    def reiniciar_app(self):
        self.in_nodos.setText("4")
        self.in_bases.setText("4")
        self.in_ambul.setText("6")
        self.in_tmax.setText("10.0")
        self.in_alpha.setText("0.5")
        self.in_dias.setText("30")
        
        self.lbl_z.setText("Z*: —")
        self.lbl_t.setText("T. Medio: —")
        self.lbl_cov.setText("Cobertura: —")
        self.lbl_max.setText("T. Máximo: —")
        self.lbl_inc.setText("Llamadas: —")
        self.lbl_alloc.setText("Asignación:\n—")
        
        m = create_folium_map({}, 0, [])
        m.save(MAP_FILE)
        self.load_map()

    def ejecutar(self):
        try:
            n = int(self.in_nodos.text())
            b = int(self.in_bases.text())
            p = int(self.in_ambul.text())
            tm = float(self.in_tmax.text())
            al = float(self.in_alpha.text())
            h = int(self.in_dias.text()) * 24
            
            self.btn.setEnabled(False)
            self.btn.setText("Calculando...")
            self.progress.setVisible(True)
            
            self.worker = SimWorker(n, b, p, tm, al, h)
            self.worker.finished.connect(self.on_success)
            self.worker.error.connect(self.on_error)
            self.worker.start()
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Verifica los valores numéricos.")

    def on_success(self, res):
        self.btn.setEnabled(True)
        self.btn.setText("⚡ Ejecutar Simulación")
        self.progress.setVisible(False)
        
        self.lbl_z.setText(f"Z*: {res['objective']:.2f}")
        self.lbl_t.setText(f"T. Medio: {res['avg_response_time']:.2f} min")
        self.lbl_cov.setText(f"Cobertura: {res['coverage']:.1f}%")
        self.lbl_max.setText(f"T. Máximo: {res['max_response_time']:.2f} min")
        self.lbl_inc.setText(f"Llamadas (Eventos): {res['total_incidents']}")
        
        alloc = res['allocation']
        txt = "Asignación Óptima:\n" + "\n".join([f"• Base {j}: {c} ambulancias" for j, c in alloc.items() if c > 0])
        self.lbl_alloc.setText(txt)
        
        self.load_map()

    def on_error(self, err):
        self.btn.setEnabled(True)
        self.btn.setText("⚡ Ejecutar Simulación")
        self.progress.setVisible(False)
        QMessageBox.critical(self, "Error", err)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = GemeloDigitalDesktop()
    win.show()
    sys.exit(app.exec_())
