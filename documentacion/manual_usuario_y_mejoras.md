# Manual de Usuario e Interfaz y Posibles Mejoras

## 1. Uso de la Aplicación Web (Gemelo Digital)

El proyecto cuenta con un entorno web interactivo diseñado para los operadores del centro regulador.

### Interfaz Principal:
1. **Configuración Paramétrica:**
   - Ubicada en el panel lateral o superior, permite al operador definir la **Flota Total** ($p$), el **Tiempo de Respuesta Crítico** (ej. 10 minutos), y la **Penalización**.
   - Presionando "Generar Matrices", el sistema estructura la tabla para ingresar la capacidad de las bases.
2. **Mapa Interactivo (GIS):**
   - El corazón de la interfaz es un mapa generado con `Folium` y `OpenStreetMap`.
   - **Controles de Capas (Layers):** En la esquina superior derecha del mapa, existe un botón interactivo que permite activar o desactivar:
     - *Capa de Mapa de Calor (Heatmap):* Visualiza en tonos rojos y naranjas los clústeres de alta siniestralidad.
     - *Capa de Hospitales:* Muestra pines con ubicación real de los centros médicos.
     - *Capa de Ambulancias:* Indica dónde el algoritmo de optimización (MILP) decidió ubicar las ambulancias disponibles para maximizar cobertura.
3. **Simulación:**
   - Al pulsar "Ejecutar Simulación", el motor `SimPy` corre internamente un escenario (ej. 30 días de accidentes) y presenta métricas comparativas.

## 2. Posibles Mejoras Futuras

Para iteraciones posteriores del prototipo, se sugieren las siguientes optimizaciones de grado avanzado:

- **Integración de Tráfico en Tiempo Real:** 
  Actualmente, las velocidades se asumen con un factor multiplicador estático (hora pico / hora valle). Una integración con la API de Google Maps o Waze permitiría alterar los tiempos de viaje dinámicamente durante la simulación.
  
- **Modelos de Reubicación Dinámica (Dynamic Relocation):**
  Desarrollar un módulo que, una vez despachada una ambulancia, evalúe si el resto de las unidades disponibles deben "moverse" preventivamente a otras bases para cubrir el "hueco" de cobertura generado.

- **Inteligencia Artificial de Despacho (Reinforcement Learning):**
  Sustituir la heurística de "enviar a la más cercana" por un agente entrenado mediante *Deep Q-Learning* que prevea la probabilidad de un accidente futuro cercano y decida si es mejor dejar la ambulancia más cercana reservada.
