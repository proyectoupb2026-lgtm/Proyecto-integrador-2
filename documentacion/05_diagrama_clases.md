# 05 — Diagrama de Clases (UML)

## Estructura Orientada a Objetos del Sistema

```mermaid
classDiagram
    class GemeloDigitalApp {
        -centros: list
        -worker: SimWorker
        -browser: QWebEngineView
        -in_nodos: QLineEdit
        -in_bases: QLineEdit
        -in_ambulancias: QLineEdit
        -in_tmax: QLineEdit
        -in_alpha: QLineEdit
        -in_sim_hours: QLineEdit
        -lbl_obj: QLabel
        -lbl_avg_time: QLabel
        -lbl_cov: QLabel
        -lbl_alloc: QLabel
        -progress: QProgressBar
        +__init__()
        +initUI()
        +load_map()
        +ejecutar()
        +_calcular_centros_csv(n_clusters) list
        +on_sim_done(result: dict)
        +on_sim_error(msg: str)
    }

    class SimWorker {
        -num_nodes: int
        -num_bases: int
        -p_ambulances: int
        -T_max: float
        -alpha: float
        -demands: list
        -capacities: list
        -t_ij: list
        -centros: list
        +finished: pyqtSignal
        +error: pyqtSignal
        +__init__(params)
        +run()
    }

    class MILPSolver {
        <<module function>>
        +solve_milp(num_nodes, num_bases, p, T_max, alpha, demands, capacities, t_ij) dict
        -_build_variables(I, J, K) tuple
        -_add_constraints(prob, x, y, z, v) 
        -_extract_allocation(x, J, K) dict
    }

    class SimPyEngine {
        <<module function>>
        +run_simulation(allocation, t_ij, demands, num_bases, sim_time) list
        -incident_gen(env, node_id, freq)
        -handle_inc(env, node_id)
    }

    class MapGenerator {
        <<module function>>
        +generar_mapa(allocation, num_bases, centros)
        -_add_vial_layer(m) FeatureGroup
        -_add_heat_layer(m, csv_path) FeatureGroup
        -_add_bases_layer(m, centros) FeatureGroup
        -_add_ambulances_layer(m, allocation, centros) FeatureGroup
    }

    class DataConstants {
        <<module constants>>
        +BASE_DIR: str
        +GEOJSON_VIAL: str
        +CSV_ACCIDENTES: str
        +MAP_FILE: str
    }

    GemeloDigitalApp "1" --> "0..1" SimWorker : lanza
    SimWorker --> MILPSolver : invoca
    SimWorker --> SimPyEngine : invoca
    SimWorker --> MapGenerator : invoca
    MILPSolver --> DataConstants : lee rutas
    MapGenerator --> DataConstants : lee rutas
    GemeloDigitalApp --> DataConstants : lee rutas

    GemeloDigitalApp --|> QMainWindow : hereda
    SimWorker --|> QThread : hereda
```

---

## Relaciones de Responsabilidad

| Clase / Módulo | Responsabilidad | Patrón |
|----------------|-----------------|--------|
| `GemeloDigitalApp` | Orquestación de UI y comunicación con el worker | MVC (View + Controller) |
| `SimWorker` | Ejecutar cálculos pesados fuera del hilo principal | Worker Thread Pattern |
| `solve_milp()` | Resolver el modelo MILP con PuLP | Strategy Pattern |
| `run_simulation()` | Ejecutar la simulación DES con SimPy | Strategy Pattern |
| `generar_mapa()` | Construir y serializar el mapa Folium | Builder Pattern |
| `DataConstants` | Centralizar las rutas de archivos del proyecto | Constants Module |
