# Análisis de Restricciones del Modelo Matemático MILP

Basado en la formulación de Programación Lineal Entera Mixta (MILP) diseñada para la localización-asignación de ambulancias en Montería, las restricciones del modelo se dividen conceptualmente en dos categorías: **duras (Hard Constraints)** y **blandas (Soft Constraints)**.

En Investigación de Operaciones, una restricción dura es una regla física o lógica obligatoria (si se viola, el modelo matemático falla y la solución es inviable). Por el contrario, una restricción blanda es una meta deseable que, de no cumplirse, no invalida la solución, pero es "castigada" mediante una penalización en la Función Objetivo.

A continuación, se presenta la clasificación técnica según el documento base:

## 🔴 Restricciones Duras (Cumplimiento obligatorio)

Estas restricciones garantizan que la logística propuesta tenga viabilidad y sentido en el mundo físico y operativo real.

1. **Límite total de la flota desplegada (Fórmula 1)**
   - **Descripción:** El total de ambulancias activadas en las bases candidatas debe ser exactamente igual a $p$ (la flota disponible).
   - **Por qué es dura:** Matemáticamente no se pueden "inventar" vehículos médicos que la ciudad no posee, ni se puede dejar parte de la flota útil sin asignar a la red.

2. **Capacidad física máxima de las bases (Fórmula 2)**
   - **Descripción:** El número de ambulancias estacionadas en cualquier base $j$ no puede superar la capacidad máxima de parqueo o infraestructura de dicha base ($C_j$).
   - **Por qué es dura:** Físicamente, un centro hospitalario o nodo de despacho no puede albergar más unidades operativas de las que su espacio permite.

3. **Asignación total de la demanda de siniestros (Fórmula 4)**
   - **Descripción:** El 100% de la demanda (1 en la suma de fracciones) de cada uno de los nodos de accidentalidad $i$ debe quedar asignada al sistema de bases.
   - **Por qué es dura:** El sistema de urgencias no puede ignorar ninguna zona crítica; toda emergencia debe tener garantizada la asignación de una unidad, incluso si esta se encuentra lejos.

4. **Lógica de acoplamiento de despacho (Fórmula 5)**
   - **Descripción:** La asignación de la demanda de un siniestro a una base en específico solo es posible si dicha base tiene asignada al menos una ambulancia.
   - **Por qué es dura:** Es ilógico y operativamente imposible despachar un vehículo de emergencia desde una base que se encuentra completamente vacía.

---

## 🟢 Restricciones Blandas (Cumplimiento deseable con penalización)

1. **El estándar de la *Hora Dorada* / Tiempo Máximo de Respuesta ($T_{max}$ = 10 minutos)**
   - **Descripción:** El modelo *desea* que todas las ambulancias lleguen al siniestro en 10 minutos o menos. 
   - **Por qué es blanda:** En la realidad urbana (congestión heterogénea en horas pico, distancias a la periferia), es matemáticamente y físicamente imposible garantizar de forma absoluta que *todas* las ambulancias lleguen en menos de 10 minutos para cualquier incidente. Por lo tanto, el modelo **no prohíbe** llegar más tarde de los 10 minutos. 
   - **Manejo en el modelo:** En lugar de invalidar la solución, el modelo calcula una "holgura de tiempo excedente" ($v_{ij}$, mediante la Fórmula 6). Como castigo por violar esta restricción blanda, la **Función Objetivo** penaliza el retraso multiplicando esos minutos extra por el factor de penalización $\alpha$, reduciendo así la eficiencia ponderada de la propuesta.
