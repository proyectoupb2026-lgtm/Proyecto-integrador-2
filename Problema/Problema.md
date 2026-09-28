# titulo:
Optimizacion y Gestión inteligente del tiempo de respuesta en atención prehospitalaria de urgencias en la ciudad de monteria mediante programación lineal entera y aprendizaje por refuerzo

# Planteamiento del problema

En la actualidad, los sistemas tradicionales de respuesta prehospitalaria suelen operar bajo lógicas de asignación heurísticas básicas, tales como el despacho de la unidad más cercana al evento o políticas de atención por orden de llegada (First-In, First-Out). Estos métodos estáticos presentan deficiencias operativas severas, ya que no contemplan la naturaleza estocástica de las emergencias ni las condiciones dinámicas del entorno urbano.

En la ciudad de Montería, el sistema de atención de urgencias se ve afectado por fluctuaciones en los flujos de tráfico a lo largo del día, cuellos de botella en arterias principales y una distribución subóptima de las bases de ambulancias. Como resultado, las unidades a menudo deben recorrer distancias prolongadas o enfrentarse a retrasos imprevistos, lo que incrementa los tiempos de llegada por encima de los estándares internacionales recomendados (frecuentemente establecidos en la "hora dorada" o en respuestas inferiores a 8-10 minutos para incidentes críticos).

Las consecuencias de estos retrasos son críticas: disminuyen drásticamente las probabilidades de supervivencia en paros cardiorrespiratorios, agravan cuadros de trauma severo y generan un uso ineficiente de la flota disponible, incrementando los costos operativos y reduciendo la capacidad de respuesta simultánea. Este escenario evidencia la necesidad imperativa de transitar de un modelo reactivo e intuitivo a un sistema de gestión inteligente, basado en la investigación de operaciones y la inteligencia artificial, capaz de anticipar la demanda y optimizar las rutas en tiempo real.

# Formulación de la pregunta problema: 

Con base en la problemática expuesta, la investigación se guiará por el siguiente interrogante fundamental:

¿De qué manera el diseño e implementación de un sistema inteligente de gestión basado en la integración de programación lineal entera (PLE) y aprendizaje por refuerzo permite optimizar la asignación y el enrutamiento de ambulancias, minimizando los tiempos de respuesta prehospitalaria en la ciudad de Montería?

# objetivo: 
Desarrollar un modelo de optimización y gestión inteligente para el sistema de atención prehospitalaria de la ciudad de Montería, combinando técnicas de programación lineal entera y algoritmos de aprendizaje por refuerzo, con el propósito de minimizar los tiempos de respuesta ante emergencias médicas y mejorar la eficiencia en la asignación de recursos.

# objetivos especificos: 

Para alcanzar el objetivo general, se establecen las siguientes metas operativas:

1. *Diagnosticar* el estado actual del sistema de atención prehospitalaria en Montería, caracterizando espacial y temporalmente la demanda de servicios de emergencia mediante el análisis de datos históricos.
2. *Formular* un modelo matemático de programación lineal entera para determinar la ubicación estática óptima de las bases de ambulancias y la asignación inicial de la flota minimizando las distancias recorridas.
3. *Diseñar* un algoritmo de aprendizaje por refuerzo capaz de adaptar dinámicamente las rutas y ejecutar la reubicación preventiva de los vehículos de emergencia, respondiendo a las variaciones del tráfico y la probabilidad espacial de nuevos incidentes en tiempo real.
4. *Evaluar* el desempeño del sistema híbrido propuesto mediante entornos de simulación, comparando los tiempos de respuesta proyectados y la eficiencia operativa frente a las políticas de despacho tradicionales.

