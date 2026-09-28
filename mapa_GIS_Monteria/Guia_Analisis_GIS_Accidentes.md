# Guía del Sistema GIS: Cruce Espacial de Accidentes en Montería y Córdoba

> **Proyecto Integrador II:** Optimización y Gestión Inteligente del Tiempo de Respuesta en Atención Prehospitalaria de Urgencias en Montería.

---

## 1. Archivos Vectoriales Descargados (Capas GIS)

Se descargaron los mapas vectoriales georreferenciados oficiales desde **OpenStreetMap / Nominatim** y se guardaron en la carpeta `mapa_GIS_Monteria/`:

1. **[monteria_boundary.geojson](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/mapa_GIS_Monteria/monteria_boundary.geojson):** Polígono del límite municipal de Montería (EPSG:4326).
2. **[cordoba_boundary.geojson](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/mapa_GIS_Monteria/cordoba_boundary.geojson):** Polígono del límite del Departamento de Córdoba (EPSG:4326).
3. **[monteria_road_network.geojson](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/mapa_GIS_Monteria/monteria_road_network.geojson):** Red vial urbana y rural apta para ambulancias en Montería.

---

## 2. Cómo Ubicar y Cruzar tus Datos de Gobierno de Accidentes

Para integrar los archivos que descargaste de la base de datos oficial del gobierno (ej. Agencia Nacional de Seguridad Vial - ANSV, DANE, Policía Nacional o Secretaría de Tránsito):

### Paso 1: Copiar tus archivos a la carpeta `bade_datos_accidentes`
Guarda tus archivos `.csv`, `.xlsx` o `.geojson` dentro de la carpeta:
`C:\Users\pc\OneDrive\Desktop\Proyecto integrador 2\bade_datos_accidentes\`

*(El script detecta automáticamente las columnas de latitud y longitud, como `latitud`, `longitud`, `lat`, `lon`, `x`, `y`).*

### Paso 2: Ejecutar el script de cruce espacial GIS
Ejecuta en tu terminal el siguiente comando o corre el script en Python:
```bash
python mapa_GIS_Monteria/procesar_y_cruzar_accidentes.py
```

---

## 3. Resultados y Visualización Generada

El sistema procesa los datos y ejecuta las siguientes técnicas espacial-cuantitativas:

1. **Spatial Join (Cruce Espacial `gpd.sjoin`):** Filtra y clasifica cuáles accidentes ocurrieron dentro del casco urbano y rural de Montería frente al resto de municipios de Córdoba.
2. **Kernel Density Estimation (HeatMap):** Mapeo de calor de puntos calientes (*hotspots*) de accidentabilidad.
3. **Cluster de Marcadores por Gravedad:**
   - 🔴 **Marcador Rojo:** Accidentes con fallecidos (muertes viales).
   - 🟠 **Marcador Naranja:** Accidentes con personas heridas.
   - 🔵 **Marcador Azul:** Accidentes con solo daños materiales.

### Visualización Interactiva
Abre directamente en tu navegador el mapa interactivo generado:
👉 **[mapa_interactivo_accidentes_monteria.html](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/mapa_GIS_Monteria/mapa_interactivo_accidentes_monteria.html)**

---
*Módulo GIS desarrollado para la caracterización espacio-temporal del Proyecto Integrador II.*
