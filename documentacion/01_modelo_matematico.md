# 01 — Formulación Matemática Formal del Modelo MILP

## Modelo de Programación Lineal Entera Mixta de Cobertura Estocástica

El sistema adopta la **Alternativa C** de la literatura científica revisada: un modelo MILP que maximiza cobertura poblacional con penalización por tiempos de viaje que excedan el umbral crítico $T_{max}$, incorporando factores de ocupación probabilística de la flota.

---

## 1. Conjuntos e Índices

| Símbolo | Descripción |
|---------|-------------|
| $I$ | Conjunto de nodos de demanda (zonas de accidentalidad de Montería), $i \in I$ |
| $J$ | Conjunto de ubicaciones candidatas para bases de ambulancias, $j \in J$ |
| $K$ | Conjunto de ambulancias disponibles en la flota pública/privada, $k \in K$ |

---

## 2. Parámetros del Modelo

| Parámetro | Unidad | Descripción |
|-----------|--------|-------------|
| $d_i$ | incidentes/mes | Frecuencia de Poisson estimada de accidentes en el nodo $i$ |
| $t_{ij}$ | minutos | Tiempo dinámico de viaje desde la base $j$ al nodo $i$ |
| $T_{max}$ | minutos | Umbral máximo de respuesta (referencia: 10 min, "Hora Dorada") |
| $p$ | unidades | Total de ambulancias a desplegar en la red |
| $C_j$ | unidades | Capacidad de estacionamiento en el sitio candidato $j$ |
| $\alpha$ | adimensional | Factor de penalización por minuto excedido sobre $T_{max}$ |

### 2.1 Calibración de $t_{ij}$ desde datos empíricos

El tiempo de viaje se estima mediante la fórmula:

$$t_{ij} = \frac{d_{ij}^{geo}}{v_{comercial}} \times 60 \quad [\text{minutos}]$$

Donde:
- $d_{ij}^{geo}$ es la distancia geodésica en kilómetros entre el nodo $i$ y la base $j$, calculada desde los clusters KMeans de los 338 puntos del CSV de accidentes.
- $v_{comercial}$ es la velocidad media de 30 km/h en zona urbana de Montería.

---

## 3. Variables de Decisión

| Variable | Tipo | Descripción |
|----------|------|-------------|
| $x_{jk} \in \{0,1\}$ | Binaria | 1 si la ambulancia $k$ se asigna a la base $j$ |
| $y_i \in \{0,1\}$ | Binaria | 1 si el nodo $i$ queda cubierto con $t_{ij} \le T_{max}$ |
| $z_{ij} \ge 0$ | Continua | Fracción de demanda del nodo $i$ atendida por la base $j$ |
| $v_{ij} \ge 0$ | Continua | Holgura de tiempo excedente sobre $T_{max}$ (variable de penalización) |

---

## 4. Función Objetivo

$$\max \; Z = \underbrace{\sum_{i \in I} d_i \, y_i}_{\text{cobertura ponderada}} - \alpha \underbrace{\sum_{i \in I} \sum_{j \in J} d_i \, v_{ij}}_{\text{penalización por exceso de tiempo}}$$

**Interpretación:** El modelo maximiza simultáneamente la cantidad de incidentes cubiertos en tiempo oportuno y minimiza el impacto de los retrasos ponderados por la frecuencia de accidentes de cada zona.

---

## 5. Restricciones Operativas

### R1 — Conservación de Flota
$$\sum_{j \in J} \sum_{k \in K} x_{jk} = p$$
*Todas las ambulancias de la flota deben ser asignadas a exactamente una base.*

### R2 — Capacidad Física de las Bases
$$\sum_{k \in K} x_{jk} \le C_j, \quad \forall j \in J$$
*El número de unidades en la base $j$ no puede superar su capacidad física $C_j$.*

### R3 — Condición de Cobertura Temporal
$$y_i \le \sum_{\substack{j \in J \\ t_{ij} \le T_{max}}} \sum_{k \in K} x_{jk}, \quad \forall i \in I$$
*El nodo $i$ se considera cubierto ($y_i = 1$) solo si existe al menos una base con ambulancia asignada dentro del radio $T_{max}$.*

### R4 — Balance de Asignación de Demanda
$$\sum_{j \in J} z_{ij} = 1, \quad \forall i \in I$$
*La totalidad de la demanda de cada nodo debe ser asignada al sistema de bases.*

### R5 — Acoplamiento Lógico de Asignación
$$z_{ij} \le \sum_{k \in K} x_{jk}, \quad \forall i \in I, \; j \in J$$
*Solo se puede asignar demanda a una base que tenga al menos una ambulancia.*

### R6 — Linealización de la Holgura de Tiempo
$$v_{ij} \ge (t_{ij} - T_{max}) \cdot z_{ij}, \quad \forall i \in I, \; j \in J$$
*Captura el exceso de tiempo de viaje sobre el umbral, proporcional a la fracción de demanda asignada.*

### R7 — Dominio de Variables
$$x_{jk} \in \{0,1\}, \quad y_i \in \{0,1\}, \quad z_{ij} \ge 0, \quad v_{ij} \ge 0$$

---

## 6. Indicadores de Salida (KPIs)

| Indicador | Fórmula | Descripción |
|-----------|---------|-------------|
| $\bar{T}_{resp}$ | $\frac{1}{N}\sum_{n=1}^{N} T_n$ | Tiempo promedio de respuesta (SimPy) |
| $\rho_k$ | $\frac{T_{ocup,k}}{T_{sim}}$ | Tasa de utilización de la ambulancia $k$ |
| $\text{Cov}_{T_{max}}$ | $\frac{\|\{n : T_n \le T_{max}\}\|}{N}$ | Fracción de incidentes atendidos en tiempo oportuno |
| $T_{max,obs}$ | $\max_n T_n$ | Peor tiempo de respuesta observado en la simulación |
| $Z^*$ | $\max Z$ | Valor óptimo de la función objetivo del modelo MILP |
