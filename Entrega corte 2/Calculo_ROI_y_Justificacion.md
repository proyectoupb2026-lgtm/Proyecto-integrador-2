# Capítulo 5: Viabilidad Financiera y Retorno de Inversión (ROI)

## 5.1 Supuestos y Justificación de Costos y Beneficios
El modelo financiero para el *Sistema de Sugerencia de Ubicación de Ambulancias* en Montería se fundamenta en los siguientes rubros proyectados a 12 meses de operación:

### Inversión Inicial (CAPEX)
* **Horas de Desarrollo e Ingeniería:** 250 horas invertidas en modelado matemático (MILP), desarrollo en Python y visualización GIS. A una tarifa base UPB de \$35.000 COP/hora. Total: \$8.750.000 COP.
* **Licenciamiento y Configuración Inicial:** APIs de mapas avanzados y entorno de simulación. Total: \$1.500.000 COP.
* **Equipamiento Computacional:** Servidor local o terminal de procesamiento para el centro regulador. Total: \$3.500.000 COP.

### Costos Operativos Anuales (OPEX)
* **Infraestructura Cloud / Servidores:** Alojamiento de la base de datos y la interfaz web en la nube (\$150.000 COP/mes). Total anual: \$1.800.000 COP.
* **Mantenimiento y Soporte:** Actualización de algoritmos y revisión de las fuentes de datos geográficos (OSMnx). Total anual: \$2.000.000 COP.

### Beneficios Económicos Cuantificables (Ahorros Anuales)
* **Ahorro Logístico en Combustible y Desgaste Vehicular:** Al estar las ambulancias ubicadas estratégicamente cerca de las zonas *hot* de accidentalidad, se evitan despachos desde largas distancias. 
  * *Cálculo:* 15 Km ahorrados diarios por ambulancia $\times$ 4 ambulancias en la flota $\times$ 365 días $\times$ \$1.200 COP (costo combustible/desgaste por Km) = **\$26.280.000 COP/año**.
* **Ahorro en Horas-Hombre (Paramédicos/Conductores):** La optimización de rutas disminuye el tiempo ocioso y el tiempo de viaje en tráfico pesado.
  * *Cálculo:* 2 horas ahorradas al día $\times$ 365 días $\times$ \$25.000 COP/hora (con cargas) = **\$18.250.000 COP/año**.

---

## 5.2 Tabla Resumen Financiero y KPIs (Formato Oficial)

| Componente Financiero | Descripción / Detalle de Ingeniería | Valor Total (COP) |
| :--- | :--- | :---: |
| **Inversión Inicial (CAPEX)** | Desarrollo (250h), servidor local, licencias y configuración inicial | \$ 13.750.000 |
| **Costos Operativos Anuales (OPEX)** | Servidor web en la nube y mantenimiento de algoritmos | \$ 3.800.000 |
| **Beneficios Brutos Anuales** | Ahorros cuantificados en combustible, desgaste y horas-hombre | \$ 44.530.000 |
| **Beneficio Neto Anual** | Beneficios Brutos (\$44.530.000) - OPEX (\$3.800.000) | \$ 40.730.000 |
| **ROI Calculado (Año 1)** | (Beneficio Neto / CAPEX) * 100 | **296.2%** |
| **Periodo de Retorno (Payback)** | CAPEX / Beneficio Neto Mensual (\$3.394.166) | **4.05 meses** |

---

## 5.3 Conclusión de Factibilidad
El proyecto demuestra una altísima viabilidad financiera, superando ampliamente el umbral del 30% exigido. Con un **ROI del 296.2%** en el primer año y un periodo de recuperación de la inversión (**Payback**) de aproximadamente **4 meses**, la implementación del modelo matemático no solo salva vidas al reducir los tiempos de respuesta (cumpliendo el objetivo misional), sino que representa una optimización agresiva en el uso de los recursos de la red de atención prehospitalaria de Montería.
