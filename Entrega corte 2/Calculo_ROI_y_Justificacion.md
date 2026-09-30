# Capítulo 5: Viabilidad Financiera y Retorno de Inversión (ROI)

## 5.1 Supuestos y Justificación de Costos y Beneficios
El modelo financiero para el *Sistema de Sugerencia de Ubicación de Ambulancias* en Montería se fundamenta en un enfoque estrictamente conservador, derivando los beneficios matemáticamente de la hipótesis central de investigación: una **reducción del 25% en el tiempo de respuesta**. 

**Sobre la Muestra Empírica vs. Cifras Oficiales:**
Para evitar inflar los beneficios asumiendo operación continua e irreal, el cálculo se basa exclusivamente en la muestra extraída mediante *web scraping*, la cual consolidó **338 incidentes viales severos**. Cabe aclarar la diferencia entre esta muestra (incidentes con cobertura periodística/graves que abarcan un histórico proyectado de 5.7 años, lo que equivale a **59 despachos anuales**) y las cifras oficiales de la Alcaldía de Montería. Según los reportes de la Secretaría de Tránsito, la ciudad registra entre 41 y 46 accidentes mensuales (aproximadamente **490 a 550 incidentes anuales**). La muestra de 59 incidentes/año representa un subconjunto crítico (siniestros severos), mientras que la cifra oficial engloba el universo total, incluyendo choques menores que no siempre requieren asistencia prehospitalaria avanzada. El modelo financiero se proyecta sobre los 59 despachos críticos.

### A. Inversión Inicial (CAPEX)
* **Horas de Desarrollo e Ingeniería:** 250 horas invertidas en modelado matemático (MILP), desarrollo en Python y visualización GIS. Tarifa base UPB: \$35.000 COP/hora. Total: \$8.750.000 COP.
* **Licenciamiento y Configuración Inicial:** APIs de mapas avanzados y entorno de simulación. Total: \$1.500.000 COP.
* **Equipamiento Computacional:** Servidor local o terminal de procesamiento para el centro regulador. Total: \$3.500.000 COP.
* **Capacitación y Puesta en Marcha:** 2 sesiones de entrenamiento de 4 horas para el personal del centro regulador y paramédicos. Total: \$1.000.000 COP.
* **Total CAPEX:** \$14.750.000 COP.

### B. Costos Operativos Anuales (OPEX)
* **Infraestructura Cloud / Servidores:** Alojamiento de la base de datos y la interfaz web en la nube (\$150.000 COP/mes). Total anual: \$1.800.000 COP.
* **Mantenimiento y Soporte:** Actualización de algoritmos y revisión de fuentes de datos. Total anual: \$2.000.000 COP.
* **Total OPEX:** \$3.800.000 COP.

### C. Beneficios Económicos Cuantificables (Ahorros Anuales)
Los ahorros se derivan estrictamente de la meta de reducción del 25% aplicada a la frecuencia anualizada de la muestra (59 despachos):
* **Ahorro en Horas-Hombre (Paramédicos/Conductores):** 
  * *Línea base:* Tiempo de respuesta promedio actual = 18 minutos.
  * *Reducción (25%):* 4.5 minutos ahorrados por despacho.
  * *Cálculo:* 4.5 minutos $\times$ 59 despachos = 265.5 minutos al año (4.42 horas). 
  * *Monetización:* 4.42 horas $\times$ \$35.000 COP/hora = **\$154.700 COP/año**.
* **Ahorro Logístico en Combustible y Desgaste Vehicular:** La reubicación preventiva acerca las ambulancias al siniestro, reduciendo la distancia de viaje en un 25% estimado.
  * *Línea base:* Distancia promedio estimada de despacho = 10 Km.
  * *Reducción (25%):* 2.5 Km ahorrados por despacho.
  * *Cálculo:* 2.5 Km $\times$ 59 despachos = 147.5 Km ahorrados al año.
  * *Monetización:* 147.5 Km $\times$ \$1.500 COP (costo combustible/desgaste por Km) = **\$221.250 COP/año**.
* **Total Beneficios Brutos Anuales:** **\$375.950 COP/año**.

---

## 5.2 Tabla Resumen Financiero y KPIs (Formato Oficial)

| Componente Financiero | Descripción / Detalle de Ingeniería | Valor Total (COP) |
| :--- | :--- | :---: |
| **Inversión Inicial (CAPEX)** | Desarrollo (250h), hardware, licencias y capacitación | \$ 14.750.000 |
| **Costos Operativos Anuales (OPEX)** | Servidores cloud y mantenimiento de algoritmos | \$ 3.800.000 |
| **Beneficios Brutos Anuales** | Ahorro logístico y horas sobre 59 despachos críticos | \$ 375.950 |
| **Beneficio Neto Anual** | Beneficios Brutos (\$375.950) - OPEX (\$3.800.000) | **-\$ 3.424.050** |
| **ROI Calculado (Año 1)** | (Beneficio Neto / CAPEX) * 100 | **-23.21%** |
| **Periodo de Retorno (Payback)** | CAPEX / Beneficio Neto Mensual | **Indefinido** |

---

## 5.3 Conclusión de Factibilidad y Limitaciones del Modelo
Al evaluar el proyecto bajo una perspectiva de austeridad extrema y utilizando **exclusivamente la frecuencia anualizada de la muestra de *scraping* (59 incidentes/año)**, el modelo arroja un **ROI negativo del -23.21%**. 

Este resultado no invalida la utilidad clínica o logística del sistema, sino que transparenta las limitaciones inherentes al alcance de la muestra. Una evaluación con 59 despachos anuales subdimensiona drásticamente la operatividad real de la ciudad, donde la cifra oficial de la Alcaldía de Montería supera los 500 accidentes anuales. La penalidad financiera actual evidencia que la infraestructura tecnológica (servidores cloud y mantenimiento) es costosa para una demanda tan reducida, pero que, al escalar la evaluación al universo real de accidentes (o al incluir la monetización de vidas salvadas y demandas evitadas por llegar a tiempo), el apalancamiento operativo del algoritmo MILP volverá financieramente viable la inversión. Estas proyecciones de escala y sensibilidad económica serán el foco principal al integrar la simulación estocástica en *SimPy*.
