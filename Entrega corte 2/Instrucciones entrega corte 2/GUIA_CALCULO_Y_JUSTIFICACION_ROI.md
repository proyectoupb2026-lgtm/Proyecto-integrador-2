# 💰 Guía Metodológica Oficial: Cálculo y Justificación del Retorno sobre la Inversión (ROI)
### *Evaluación Económica, Factibilidad Financiera e Impacto en Ingeniería*
**Universidad Pontificia Bolivariana — Seccional Montería**  
**Facultad de Ingeniería Industrial // Grupo de Investigación SILOGE // Hub Industrial Solution (HIS)**  
**Docente Titular:** M.Sc. Cristian Javier Cano Mogollón  
**Periodo Académico:** 2026-2  

---

## 📌 1. Introducción y Propósito Pedagógico

En el ejercicio profesional de la Ingeniería Industrial y la Gestión Tecnológica, una solución técnica excelente carece de viabilidad real si no demuestra un **retorno económico positivo y sostenible** para la organización que la adopta.

El **Retorno sobre la Inversión (ROI - *Return on Investment*)** es el indicador financiero fundamental exigido en las evaluaciones de **Segundo Corte** para todas las asignaturas (**Proyecto Integrador I**, **Proyecto Integrador II** y **Gestión Tecnológica**). Permite medir la eficiencia del capital invertido en el desarrollo, implementación o automatización del proyecto frente a los beneficios económicos generados.

---

## 📐 2. Formulación Matemática Rigurosa

### 2.1 Ecuación Principal del ROI
El ROI se expresa como un porcentaje que indica cuánto dinero se recupera por cada peso invertido:

$$\text{ROI} = \left( \frac{\text{Beneficio Neto Acumulado}}{\text{Costo Total de Inversión (CAPEX)}} \right) \times 100\%$$

Donde:
* **Beneficio Neto Acumulado:** Corresponde a los beneficios económicos totales generados (ahorros + ingresos adicionales) menos los costos operativos recurrentes durante el periodo de evaluación (generalmente 12 meses):
  $$\text{Beneficio Neto} = \text{Beneficios Brutos (Ahorros)} - \text{Costos Operativos (OPEX)}$$
* **Costo Total de Inversión (CAPEX):** Gastos de capital requeridos para diseñar, prototipar y poner en marcha la solución.

---

### 2.2 Periodo de Recuperación de la Inversión (*Payback Period*)
Indica el tiempo exacto (en meses o años) necesario para que los ahorros netos acumulados igualen la inversión inicial:

$$\text{Payback (meses)} = \frac{\text{CAPEX}}{\text{Beneficio Neto Mensual Promedio}}$$

> [!TIP]
> **Criterio de Aceptación para Proyectos Universitarios de Base Tecnológica:**
> - $\text{ROI} \ge 30\%$ en el primer año de operación.
> - $\text{Payback} \le 12 \text{ meses}$ para soluciones de software, optimización o prototipos maker; $\le 24 \text{ meses}$ para inversiones industriales de alto porte.

---

## 📊 3. Desglose Estructurado de Componentes Financieros

Cada equipo debe discriminar sus costos y beneficios en las siguientes categorías formales:

### A. Inversión Inicial — CAPEX (*Capital Expenditures*)
Gastos que se realizan **una sola vez** al inicio del proyecto:
1. **Horas de Ingeniería y Desarrollo:** Costo del tiempo dedicado por el equipo en análisis, modelado, programación y diseño. *(Tarifa base de referencia UPB: $25.000 a $40.000 COP/hora de ingeniero junior).*
2. **Equipamiento y Hardware:** Microcontroladores (Arduino, ESP32, Raspberry Pi), sensores, actuadores, balanzas, dispositivos IoT o terminales de cómputo.
3. **Prototipado Físico / Fabricación Aditiva:** Filamento 3D, cortes láser, perfiles de aluminio, componentes mecánicos (Lista de Materiales - BOM).
4. **Licenciamiento y Configuración Inicial:** Suscripciones iniciales de software especializado, dominios o servicios cloud.
5. **Capacitación y Puesta en Marcha:** Horas de entrenamiento a operarios o personal de planta en Montería/Córdoba.

---

### B. Costos Operativos Recurrentes — OPEX (*Operational Expenditures*)
Costos necesarios para mantener la solución en funcionamiento a lo largo de un año:
1. **Infraestructura Cloud / Servidores:** Alojamiento web, bases de datos (PostgreSQL en la nube, Firebase, Supabase), APIs de Inteligencia Artificial (tokens de Gemini API u OpenAI).
2. **Mantenimiento Preventivo y Correctivo:** Calibración de sensores, reposición de piezas fungibles y soporte técnico.
3. **Consumo Eléctrico y Conectividad:** Datos móviles (SIMs M2M para IoT en zonas rurales de Córdoba) o internet de banda ancha.

---

### C. Beneficios Económicos Cuantificables (Ahorros Operativos Anuales)
La justificación del ROI debe fundamentarse en **métricas reales o proyectadas con rigor de ingeniería**:
1. **Ahorro en Horas-Hombre (Mano de Obra Directa/Indirecta):**
   $$\text{Ahorro Horas} = (\text{Horas Reducidas por Día}) \times (\text{Días Laborales/Año}) \times (\text{Costo Hora con Cargas Prestacionales})$$
2. **Reducción de Mermas y Desperdicios:**
   $$\text{Ahorro Merma} = (\text{Kg o Unidades de Producto Salvadas/Mes}) \times (\text{Costo Unitario}) \times 12$$
3. **Optimización Logística de Combustible y Rutas:**
   $$\text{Ahorro Transporte} = (\text{Km Reducidos por Ruta}) \times (\text{Costo Combustible + Desgaste/Km}) \times (\text{Frecuencia Anual})$$
4. **Eliminación de Paradas No Programadas (Mantenimiento Predictivo / IoT):**
   $$\text{Ahorro Paradas} = (\text{Horas de Parada Evitadas}) \times (\text{Costo de Oportunidad / Lucro Cesante por Hora})$$

---

## 📝 4. Caso Modelo Aplicado (Contexto Montería / Córdoba)

A modo de ejemplo ilustrativo, se presenta el modelo financiero para un proyecto de optimización y trazabilidad en una planta de acopio de granos o lácteos en Cereté/Montería:

| Categoría | Concepto Específico | Detalle Cuantitativo | Valor Anual (COP) |
| :--- | :--- | :--- | :---: |
| **CAPEX** | Horas de Desarrollo e Ingeniería | 200 horas $\times$ $35.000 COP | $ 7.000.000 |
| **CAPEX** | Sensores IoT, Gateway LoRaWAN y Balanza | Hardware y cajas IP67 | $ 4.500.000 |
| **CAPEX** | Fabricación de Carcasa y BOM Maker | Impresión 3D + Perfiles | $ 1.300.000 |
| **CAPEX** | Capacitación de Operarios en Planta | 2 sesiones $\times$ 4 horas | $ 1.000.000 |
| **TOTAL CAPEX** | **Inversión Inicial Total ($I_0$)** | — | **$ 13.800.000** |
| **OPEX** | Hosting Cloud y Base de Datos | $ 150.000 COP / mes $\times$ 12 | $ 1.800.000 |
| **OPEX** | Mantenimiento de Sensores y Repuestos | Inspecciones trimestrales | $ 1.600.000 |
| **TOTAL OPEX** | **Costos de Operación Anuales** | — | **$ 3.400.000** |
| **BENEFICIOS** | Ahorro en tiempo de pesaje y registro | 2.5 h/día ahorradas en 2 operarios | $ 18.500.000 |
| **BENEFICIOS** | Reducción de mermas por mal almacenamiento | 1.8% de merma prevenida sobre $600M | $ 10.800.000 |
| **BENEFICIOS** | Eliminación de errores en facturación | Auditorías y multas evitadas | $ 4.200.000 |
| **TOTAL BENEF.** | **Beneficios Brutos Anuales** | — | **$ 33.500.000** |

### Cálculo Numérico:
1. **Beneficio Neto Anual:**
   $$\text{Beneficio Neto} = \$33.500.000 - \$3.400.000 = \$30.100.000 \text{ COP/año}$$
2. **Retorno sobre la Inversión (ROI):**
   $$\text{ROI} = \left( \frac{\$30.100.000}{\$13.800.000} \right) \times 100\% = \mathbf{218.1\%}$$
3. **Periodo de Recuperación (*Payback*):**
   $$\text{Beneficio Neto Mensual} = \frac{\$30.100.000}{12} = \$2.508.333 \text{ COP/mes}$$
   $$\text{Payback} = \frac{\$13.800.000}{\$2.508.333} \approx \mathbf{5.5 \text{ meses}}$$

---

## 📋 5. Plantilla Obligatoria de Tabla Financiera para los Entregables

Cada equipo debe incluir en el **Capítulo de Viabilidad Financiera** de su documento y en la **Tarjeta de ROI del Póster Científico** la siguiente tabla formal diligenciada con los valores reales o paramétricos de su proyecto:

```markdown
| Componente Financiero | Descripción / Detalle de Ingeniería | Valor Total (COP) |
| :--- | :--- | :---: |
| **Inversión Inicial (CAPEX)** | Desarrollo, hardware, BOM, licencias iniciales | $ [Monto] |
| **Costos Operativos Anuales (OPEX)** | Servidores, nube, mantenimiento, conectividad | $ [Monto] |
| **Beneficios Brutos Anuales** | Ahorros cuantificados en tiempo, mermas, combustible | $ [Monto] |
| **Beneficio Neto Anual** | Beneficios Brutos - OPEX | $ [Monto] |
| **ROI Calculado (Año 1)** | (Beneficio Neto / CAPEX) * 100 | **[XX.X]%** |
| **Periodo de Retorno (Payback)** | CAPEX / Beneficio Neto Mensual | **[X.X] meses** |
```

---

## ⚖️ 6. Errores Comunes que Penalizan la Calificación
1. **Presentar un ROI sin discriminar costos:** Asumir que la inversión es únicamente el costo de compra de un sensor, ignorando las horas de desarrollo o los costos de la nube.
2. **Beneficios "mágicos" no justificados:** Colocar cifras de ahorro sin explicar la fórmula ni la fuente empírica de datos en el contexto de Montería/Córdoba.
3. **Confundir Beneficio Bruto con Beneficio Neto:** Olvidar restar los costos operativos (OPEX) al calcular el retorno.
4. **Falta de concordancia:** Presentar valores diferentes de ROI en el documento escrito y en el póster científico.

---
*Documento avalado por la Coordinación de Proyectos Integradores y Gestión Tecnológica — UPB Seccional Montería*
