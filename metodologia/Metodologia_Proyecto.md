# Propuesta Metodológica del Proyecto Integrador

> **Título del Proyecto:** Optimización y Gestión inteligente del tiempo de respuesta en atención prehospitalaria de urgencias en la ciudad de Montería mediante programación lineal entera y aprendizaje por refuerzo.  
> **Documentos Base:** [Problema.md](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/Problema/Problema.md) y literatura científica almacenada en [Base_datos](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/Base_datos).

---

## 1. Enfoque y Paradigma Metodológico

Para el desarrollo del proyecto se propone un **Enfoque Cuantitativo con Alcance Explicativo-Aplicado**, articulado bajo el marco de **Design Science Research (DSR)** e **Investigación de Operaciones Híbrida (OR + AI)**.

### Racionalidad del Enfoque:
- **Design Science Research (DSR):** Paradigma metodológico en ingeniería e informática que guía la creación rigurosa de un *artefacto tecnológico/sistemático* (el modelo híbrido de gestión inteligente de ambulancias).
- **Enfoque Cuantitativo y Experimental Basado en Simulación:** Se fundamenta en el análisis de datos matemáticos, espaciales (GIS) y temporales (series de tiempo de incidentes y tráfico urbano) para alimentar modelos de optimización lineal y algoritmos de inteligencia artificial evaluados computacionalmente en simulaciones controladas.

---

## 2. Estructura de la Metodología por Fases y Objetivos

La metodología se organiza en **4 Fases Metodológicas**, asociadas directamente a cada uno de los 4 objetivos específicos del proyecto:

```mermaid
flowchart TD
    subgraph Fase 1 [Fase 1: Diagnóstico Espacio-Temporal]
        A1[Recolección datos históricos emergencias Montería] --> A2[Limpieza y preparación espacial/GIS OSM]
        A2 --> A3[Clustering K-Means / KDE Hotspots]
        A3 --> A4[Modelado estocástico Poisson demand]
    end

    subgraph Fase 2 [Fase 2: Optimización Estática PLE / MILP]
        B1[Formulación matemática del modelo MALP / MCLP] --> B2[Definición de variables, objetivo y restricciones]
        B2 --> B3[Resolución computacional en GUROBI / PuLP]
        B3 --> B4[Ubicación estática óptima de bases y flota inicial]
    end

    subgraph Fase 3 [Fase 3: Aprendizaje por Refuerzo Dinámico]
        C1[Formulación del MDP: Estado, Acción, Recompensa] --> C2[Arquitectura DRL: Agent DQN / PPO]
        C2 --> C3[Entrenamiento con tráfico en tiempo real y reubicación]
        C3 --> C4[Política óptima de despacho y reubicación preventiva]
    end

    subgraph Fase 4 [Fase 4: Simulación y Evaluación Comparativa]
        D1[Construcción entorno de simulación SUMO / SimPy] --> D2[Ejecución de experimentos comparativos]
        D2 --> D3[Métricas: Tiempos respuesta, Cobertura <8 min, Eficiencia]
        D3 --> D4[Validación estadística de resultados]
    end

    Fase 1 --> Fase 2
    Fase 2 --> Fase 3
    Fase 3 --> Fase 4
```

---

### FASE 1: Diagnóstico y Caracterización Espacio-Temporal de la Demanda (Objetivo Específico 1)

**Propósito:** Caracterizar el comportamiento espacial y temporal de las urgencias prehospitalarias en Montería y construir la matriz de tiempos de viaje.

#### Actividades y Técnicas:
1. **Recolección y Preprocesamiento de Datos Históricos:**
   - Limpieza y estructuración del registro histórico de incidentes médicos en Montería (coordenadas geográficas, hora de llamada, día de la semana, nivel de gravedad).
   - Extracción de la red vial urbana de Montería mediante **OpenStreetMap (OSM)** y librerías espacial de Python (`OSMnx`, `GeoPandas`).
2. **Análisis Espacial de Hotspots (Puntos Calientes):**
   - Aplicación de **Estimación de Densidad Kernel (KDE)** o agrupamiento espacial (**K-Means / DBSCAN**) para identificar zonas críticas de alta demanda.
3. **Modelado Estocástico de la Demanda:**
   - Ajuste de distribuciones de probabilidad espacio-temporales mediante **Procesos de Poisson No Homogéneos** $\lambda(x, y, t)$ para representar la naturaleza estocástica de las emergencias a lo largo del día.
4. **Construcción de Matrices Origen-Destino (OD) y Tráfico:**
   - Definición de matrices de tiempo de viaje dependientes del tiempo $T_{ij}(t)$ considerando velocidades promedio en hora pico y hora valle en las arterias principales de Montería.

---

### FASE 2: Formulación e Implementación del Modelo de Programación Lineal Entera (Objetivo Específico 2)

**Propósito:** Determinar la ubicación estática óptima de las bases de ambulancias y la asignación inicial de la flota minimizando las distancias recorridas y maximizando la cobertura.

#### Modelo Matemático de Referencia: *Capacitated Maximum Availability Location Problem (MALP)* / *MCLP*

#### Formulación Estructurada:
1. **Conjuntos e Índices:**
   - $I$: Conjunto de nodos de demanda urbana en Montería ($i \in I$).
   - $J$: Conjunto de ubicaciones candidatas para bases de ambulancias ($j \in J$).
2. **Parámetros:**
   - $d_{ij}$: Distancia o tiempo de recorrido entre la base $j$ y el nodo de demanda $i$.
   - $S$: Umbral máximo de tiempo de respuesta estándar (ej. 8 minutos / "hora dorada").
   - $w_i$: Peso o volumen de demanda histórica en el nodo $i$.
   - $N$: Número total de ambulancias disponibles en la flota de Montería.
   - $C_j$: Capacidad máxima de ambulancias en la base $j$.
   - $a_{ij} = 1$ si $d_{ij} \le S$, de lo contrario $0$.
3. **Variables de Decisión:**
   - $x_j \in \{0, 1\}$: $1$ si se habilita una base en la ubicación $j$; $0$ de lo contrario.
   - $y_j \in \mathbb{Z}^+$: Número de ambulancias asignadas a la base $j$.
   - $z_{i} \in \{0, 1\}$: $1$ si el nodo de demanda $i$ está cubierto dentro del tiempo límite $S$.

4. **Función Objetivo:**
   $$\text{Minimizar } Z = \alpha \sum_{i \in I} \sum_{j \in J} w_i \cdot d_{ij} \cdot x_j - \beta \sum_{i \in I} w_i \cdot z_i$$
   *(Combina la minimización del tiempo promedio recorrido con la maximización de la demanda cubierta dentro del umbral recomendado).*

5. **Resolución Computacional:**
   - Programado en Python utilizando **GUROBI**, **CPLEX** o **PuLP**.

---

### FASE 3: Diseño del Algoritmo de Aprendizaje por Refuerzo (RL) para Control Dinámico (Objetivo Específico 3)

**Propósito:** Desarrollar un agente dinámico capaz de reubicar preventivamente las ambulancias y adaptar las rutas en tiempo real frente a congestiones de tráfico e imprevistos.

#### Formulación como Proceso de Decisión de Markov (MDP):
1. **Espacio de Estados ($S_t$):**
   - Ubicación espacial actual de cada ambulancia $k$ (coordenadas o nodo del grafo).
   - Estado operativo de la ambulancia (Disponible, En desplazamiento hacia emergencia, Ocupada en traslado, En reubicación).
   - Matriz de congestión del tráfico en tiempo real $V_{\text{tráfico}}(t)$.
   - Vector de probabilidad espacio-temporal de demanda futura derivado de la Fase 1.
2. **Espacio de Acciones ($A_t$):**
   - **Acción de Despacho:** Asignar la ambulancia $k$ al incidente $i$.
   - **Acción de Reubicación Preventiva (Relocation):** Mover una ambulancia disponible desde la base $j_1$ hacia la base estratégica $j_2$ anticipating demanda futura.
   - **Acción de Enrutamiento:** Seleccionar la ruta óptima evitando cuellos de botella urbanos.
3. **Función de Recompensa ($R_t$):**
   $$R_t = - \left( \text{Tiempo\_Respuesta}_{k, i} + \gamma \cdot \mathbb{I}(\text{Tiempo} > 8 \text{ min}) + \delta \cdot \text{Costo\_Desplazamiento\_Reubicación} \right)$$
   *(Penaliza los tiempos prolongados de llegada y el incumplimiento del umbral internacional).*

4. **Algoritmo de Aprendizaje:**
   - **Deep Q-Network (DQN)** o **Proximal Policy Optimization (PPO)** implementado en PyTorch / TensorFlow / Gymnasium.

---

### FASE 4: Evaluación, Simulación y Validación Comparativa (Objetivo Específico 4)

**Propósito:** Evaluar el rendimiento del sistema híbrido propuesto frente a las políticas de despacho tradicionales mediante un entorno de simulación computacional.

#### Entorno de Simulación:
- **Herramienta:** **SUMO (Simulation of Urban MObility)** integrado con Python mediante la API TraCI, o entorno custom en **SimPy**.
- **Red Vial:** Modelado de las arterias viales principales y secundarias de la ciudad de Montería.

#### Escenarios de Experimentación Comparativa:

| Escenario | Estrategia de Asignación / Despacho | Reubicación Dinámica | Adaptación al Tráfico |
| :--- | :--- | :--- | :--- |
| **Escenario 1 (Tradicional / Baseline)** | Despacho unidad más cercana / Lógica FIFO | No (Bases estáticas tradicionales) | No (Rutas estáticas fijas) |
| **Escenario 2 (PLE Puro)** | Asignación estática basada en modelo PLE | No | Parcial (Rutas con distancia mínima) |
| **Escenario 3 (Híbrido Propuesto: PLE + RL)** | Asignación estática óptima (PLE) + Despacho Inteligente (RL) | Sí (Reubicación preventiva adaptativa) | Sí (Rutas dinámicas adaptadas al tráfico en tiempo real) |

#### Métricas de Evaluación Operativa:
1. **Tiempo Promedio de Respuesta ($\bar{T}_{\text{resp}}$):** Tiempo transcurrido desde la llamada hasta la llegada de la ambulancia.
2. **Tasa de Cobertura en la "Hora Dorada" ($\% C_8$):** Porcentaje de servicios atendidos en un tiempo inferior a 8 minutos.
3. **Porcentaje de Utilización de Flota ($\% U$):** Eficiencia en el uso de los vehículos de emergencia.
4. **Distancia Total Recorrida y Costo Operativo:** Reducción de kilómetros en desplazamientos en vacío.

---

## 3. Matriz Metodológica de Sintesis (Alineación Objetivos - Técnicas - Herramientas)

| Objetivo Específico | Productos Esperados | Técnicas / Métodos | Herramientas / Software | Soporte Literario (Base_datos) |
| :--- | :--- | :--- | :--- | :--- |
| **1. Diagnóstico de la demanda** | Mapas de densidad (KDE), caracterización estocástica de emergencias y red de Montería. | Clustering (K-Means), Estimación Kernel, Procesos de Poisson No Homogéneos. | Python (`GeoPandas`, `OSMnx`, `scikit-learn`), QGIS. | *Measuring and optimizing spatial accessibility to EMS (2026)* |
| **2. Modelo de Optimización PLE** | Ubicación óptima estática de bases de ambulancias y asignación inicial de flota. | Programación Lineal Entera Mixta (MILP), MALP, MCLP, P-Median. | Python (`GUROBI`, `PuLP`, `SciPy`). | *Positioning of ambulances by Integer Programming (2016)* |
| **3. Algoritmo de Aprendizaje por Refuerzo** | Agente DRL de reubicación preventiva y enrutamiento dinámico adaptativo al tráfico. | Proceso de Decisión de Markov (MDP), Deep Q-Networks (DQN), PPO. | Python (`PyTorch`, `Gymnasium`, `RLlib`). | *Ambulance route optimization using Deep Neural Network (2025)* |
| **4. Evaluación y Simulación** | Informe comparativo del tiempo de respuesta del sistema híbrido vs. tradicional. | Simulación de eventos discretos, simulación de tráfico urbano, pruebas ANOVA. | **SUMO (Simulation of Urban MObility)**, `TraCI`, `SimPy`. | *Dynamic penalty-based dispatching decision making (2025)* |

---
*Documento metodológico preparado para el desarrollo del Proyecto Integrador II.*
