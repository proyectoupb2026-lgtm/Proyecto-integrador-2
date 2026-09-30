# Modelo Matemático y Notación Científica

Este documento detalla el fundamento cuantitativo del sistema, basado en la **Programación Lineal Entera Mixta (MILP)** adaptado para cobertura estocástica.

## Formulación del Modelo

El sistema busca equilibrar la máxima cobertura poblacional con el riesgo estocástico de congestión. Para ello, se formula el siguiente modelo:

### 1. Conjuntos e Índices
- $I$: Conjunto de zonas o nodos de demanda poblacional (accidentes), $i \in I$.
- $J$: Conjunto de ubicaciones candidatas para bases de ambulancias (hospitales y puntos estratégicos), $j \in J$.
- $K$: Conjunto de ambulancias de la flota disponible, $k \in K$.

### 2. Parámetros Determinísticos
- $d_i$: Demanda horaria estimada en el nodo $i$ (Frecuencia $\lambda$ de Poisson).
- $t_{ij}$: Tiempo dinámico de viaje (minutos) desde la base $j$ hasta el nodo $i$.
- $T_{max}$: Umbral de tiempo límite para la "Hora Dorada" (Ej: 10 minutos).
- $p$: Número total de vehículos a posicionar.
- $C_j$: Capacidad máxima de estacionamiento en el nodo $j$.
- $\alpha$: Factor de penalización por minuto de exceso sobre $T_{max}$.

### 3. Variables de Decisión
- $x_{jk} \in \{0, 1\}$: 1 si la ambulancia $k$ se ubica en la base $j$; 0 de lo contrario.
- $y_i \in \{0, 1\}$: 1 si el nodo $i$ tiene al menos una ambulancia asignada a una distancia $t_{ij} \le T_{max}$.
- $z_{ij} \ge 0$: Fracción probabilística de la demanda del nodo $i$ que es atendida por la base $j$.
- $v_{ij} \ge 0$: Holgura de tiempo continuo que excede $T_{max}$ (para efectos de penalización).

### 4. Función Objetivo
Maximizar la cobertura efectiva menos el costo de la penalización por exceder el tiempo crítico:

$$ \max Z = \sum_{i \in I} d_i y_i - \alpha \sum_{i \in I} \sum_{j \in J} d_i v_{ij} $$

### 5. Restricciones Críticas
1. **Conservación de Flota**:
   $$ \sum_{j \in J} \sum_{k \in K} x_{jk} = p $$
   *(Asegura que todas las ambulancias sean desplegadas).*

2. **Capacidad de las Bases**:
   $$ \sum_{k \in K} x_{jk} \le C_j, \quad \forall j \in J $$
   *(No se puede exceder el límite físico de estacionamiento de la clínica/base).*

3. **Condición Matemática de Cobertura**:
   $$ y_i \le \sum_{j \in J | t_{ij} \le T_{max}} \sum_{k \in K} x_{jk}, \quad \forall i \in I $$

4. **Balance de Asignación**:
   $$ \sum_{j \in J} z_{ij} = 1, \quad \forall i \in I $$

5. **Acoplamiento de Holgura (Linealización)**:
   $$ v_{ij} \ge t_{ij} z_{ij} - T_{max} z_{ij}, \quad \forall i \in I, j \in J $$
