# 📢 Guía Oficial de Entrega en Teams: Tarea Segundo Corte (Corte 2)
### Asignatura: Proyecto Integrador II (`Código: 8830 0059 0`)
**Universidad Pontificia Bolivariana — Seccional Montería**  
**Facultad de Ingeniería Industrial // Grupo de Investigación SILOGE // Hub Industrial Solution (HIS)**  
**Docente Titular:** M.Sc. Cristian Javier Cano Mogollón  
**Periodo Académico:** 2026-2 &nbsp;|&nbsp; **Ponderación:** Segundo Corte (30% de la Nota Semestral)  

---

> ### 📌 Mensaje para Publicar y Programar en Microsoft Teams / Moodle:
> 
> Estimados ingenieros en formación de **Proyecto Integrador II**:  
> 
> Se encuentra formalmente habilitada la entrega de la **Tarea del Segundo Corte (Corte 2)**. En esta etapa decisiva del semestre, los equipos transitan del modelo conceptual hacia la consolidación de la **arquitectura tecnológica, ingeniería de datos, diagramación de flujos y gobernanza de la información**, integrando su prototipo computacional, gemelo digital o sistema analítico con la viabilidad financiera real del proyecto.
> 
> ---
> 
> ### 📋 Estructura y Componentes Obligatorios de la Entrega
> 
> Cada equipo de trabajo debe entregar los siguientes cuatro productos técnicos debidamente articulados:
> 
> #### 1. 📄 Documento Técnico de Proyecto y Arquitectura de Prototipado (PDF - Formato APA 7ma Edición)
> El documento debe consolidar los avances del semestre en los siguientes capítulos:
> * **1. Título Canónico, Resumen Estructurado y Abstract:** Fórmula oficial `[Acción/Variable Independiente] + [Efecto/Variable Dependiente] + [Población/Empresa] + [Montería/Córdoba] + [2026]`.
> * **2. Diagnóstico Empírico en Planta (*Gemba Walk*) & Línea Base:** Cuantificación rigurosa de tiempos de ciclo, cuellos de botella y mermas en la empresa de Córdoba vinculada.
> * **3. Formulación del Modelo Matemático / Algorítmico Formal:**  
>   - Conjuntos e Índices.
>   - Parámetros del sistema con unidades físicas de medida.
>   - Variables de Decisión ($x_i \in \mathbb{R}^+, \mathbb{Z}^+, \{0,1\}$).
>   - Función Objetivo formalizada ($\text{Minimizar Costos/Tiempos}$ o $\text{Maximizar Utilidad/Eficiencia}$).
>   - Restricciones operativas (capacidad, balance de flujo/masa, demanda, no negatividad).
> * **4. Arquitectura del Prototipo Computacional / Gemelo Digital (*Digital Twin*):**  
>   - Diagrama de bloques de integración: Python 3.11+, SimPy / SciPy, Gemini API, Streamlit / FastHTML y PostgreSQL.
>   - Explicación del funcionamiento del motor analítico y estado actual de desarrollo.
> 
> #### 2. 📐 Diagramas de Flujos de Datos (DFD) — Niveles 0, 1 y 2
> Mapeo exhaustivo de la información bajo notación formal (Yourdon/DeMarco o Gane & Sarson):
> * **DFD Nivel 0 (Diagrama de Contexto):** Delimitación de fronteras del sistema, identificando entidades externas (operario, sensores, ERP empresarial, base de datos) y flujos principales de entrada/salida.
> * **DFD Nivel 1 (Descomposición Funcional de Subsistemas):** Desglose en procesos primarios (ingesta de datos empíricos, preprocesamiento/limpieza, ejecución del algoritmo de optimización/simulación, generación de reportes y alertas).
> * **DFD Nivel 2 (Detalle Operativo de Procesos Críticos):** Desglose granular del proceso analítico central, mostrando transacciones atómicas, validación de variables y consultas hacia almacenes de datos (*Data Stores*).
> 
> #### 3. 🛡️ Gobernanza de Datos (Data Governance — Estándar DAMA-DMBOK / ISO 8000)
> Formulación de la estrategia de gestión integral de activos de datos:
> * **Catálogo y Diccionario de Datos:** Tabla formal con todos los atributos capturados y generados (nombre técnico, tipo de dato, longitud, descripción operativa, reglas de integridad y fuente de captura).
> * **Linaje del Dato (*Data Lineage*):** Diagrama y matriz de trazabilidad extremo a extremo (desde la captura manual o por sensores en planta, pasando por el almacenamiento, la transformación algorítmica, hasta el consumo en el panel de control).
> * **Políticas y Métricas de Calidad de Datos:** Definición de indicadores para monitorear las dimensiones de calidad: *Completitud* (% datos no nulos), *Exactitud* (tolerancia de error), *Consistencia* (reglas relacionales) y *Oportunidad* (latencia de actualización).
> * **Seguridad, Privacidad y Ciclo de Vida:** Matriz de control de accesos basada en roles (**RBAC**), políticas de respaldo (*backup*), anonimización o protección de datos confidenciales de la empresa y políticas de retención.
> 
> #### 4. 🎨 Pieza Gráfica Institucional: Póster Científico Oficial (90 x 120 cm)
> * Orientación vertical estricta (**90 cm de ancho $\times$ 120 cm de alto**).
> * Logotipos oficiales en cabecera: **UPB**, **HIS** y **SILOGE** (ubicados en `assets/logos/`).
> * Incorporación de diagramas DFD, arquitectura del gemelo digital, resumen del marco de gobernanza, interfaces de usuario y **Tarjeta destacada de KPI Financiero (ROI y Payback)**.
> * Código QR dinámico que vincule al video demo del prototipo en ejecución y repositorio técnico.
> * *(Puede usarse la plantilla web interactiva provista `plantilla_poster_cientifico.html` o herramienta gráfica equivalente a tamaño 90x120 cm).*
> 
> #### 5. 💰 Evaluación Financiera y Justificación del Retorno de Inversión (ROI)
> * Modelo económico completo elaborado según la `GUIA_CALCULO_Y_JUSTIFICACION_ROI.md`:
>   - Inversión Inicial (**CAPEX**): hardware, licencias, horas de programación y prototipado.
>   - Costos Operativos (**OPEX**): hosting, APIs, mantenimiento anual.
>   - Beneficios Económicos Cuantificados (ahorro en horas-hombre, reducción de mermas, optimización de combustible).
>   - Cálculo formal de **ROI (%)** y **Periodo de Retorno (*Payback* en meses)**.
> 
> ---
> 
> ### ⚖️ Reglas de Rigor Editorial SILOGE
> * **Redacción estrictamente impersonal** en tercera persona (*"se implementó"*, *"el algoritmo minimiza"*).
> * Cursiva para términos técnicos extranjeros (*Gemba Walk*, *Data Lineage*, *Payback*); no usar negrita en el cuerpo del texto.
> * Acrónimos con comas parentéticas (*...mediante Diagramas de Flujos de Datos, DFD, se representó...*).
> * Enlaces **DOI verificados y activos** para toda literatura de soporte citada.
> 
> ---
> 
> ### 📦 Convención de Nombres y Entrega
> Subir un único archivo comprimido `.zip` por equipo en el canal de Microsoft Teams:  
> `PINT2_Corte2_Equipo_XX_NombreProyecto.zip`  
> *(Ejemplo: `PINT2_Corte2_Equipo_02_BoviLog_Transporte.zip`)*
> 
> Estructura interna requerida:
> 1. `01_Documento_Tecnico_PINT2_Equipo_XX.pdf`
> 2. `02_Diagramas_DFD_Gobernanza_Equipo_XX.pdf` (o integrado en el documento principal)
> 3. `03_Poster_Cientifico_90x120_Equipo_XX.pdf`
> 4. `04_Modelo_Financiero_ROI_Equipo_XX.xlsx` (opcional si está inserto en el documento)
> 
> ---
> 
> ### 📊 Criterios de Evaluación y Ponderación (100% de la Tarea)
> * 📄 **30%** — Documentación Técnica, Formulación Matemática y Arquitectura del Prototipo.
> * 📐 **25%** — Diagramas de Flujos de Datos (DFD Niveles 0, 1 y 2).
> * 🛡️ **20%** — Marco de Gobernanza de Datos (Catálogo, Linaje, Calidad y Seguridad).
> * 🎨 **15%** — Pieza Gráfica Institucional (Póster 90x120 cm con logos UPB, HIS y SILOGE).
> * 💰 **10%** — Análisis Financiero, Justificación del ROI y Payback.
> 
> ¡Avanzamos con excelencia hacia el cierre del semestre y la sustentación pública de sus prototipos!
