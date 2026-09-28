# Mapas Vectoriales de Montería y Córdoba (Uso 100% Offline / Fuera de Línea)

Este paquete contiene todos los archivos vectoriales georreferenciados de **Montería, Córdoba, Colombia**, listos para descargar y abrir localmente sin necesidad de internet.

---

## Estructura del Paquete de Descarga:

### 1. `1_Shapefiles_ESRI_QGIS_ArcGIS/` (Formato Estándar GIS Offline)
Compatible con **QGIS, ArcGIS Pro, ArcMap, AutoCAD Civil 3D, gvSIG**:
- `monteria_limite_municipal.shp` (y sus archivos asociados .dbf, .prj, .shx): Polígono oficial del municipio de Montería.
- `cordoba_limite_departamental.shp`: Polígono departamental de Córdoba.
- `monteria_malla_vial.shp`: Líneas de toda la red vial urbana y rural de Montería con atributos de vías.
- `monteria_nodos_intersecciones.shp`: Puntos de todas las intersecciones viales.

### 2. `2_GeoJSON_Web_GIS/` (Formato Abierto y Ligero)
Compatible con visualizadores web offline, Python, R, Kepler.gl, D3.js:
- `monteria_limite_municipal.geojson`
- `cordoba_limite_departamental.geojson`
- `monteria_malla_vial.geojson`
- `monteria_nodos_intersecciones.geojson`

### 3. `3_GeoPackage_OGC_Universal/` (Base de Datos Vectorial Todo en Uno)
- `monteria_geopackage_completo.gpkg`: Contiene **todas las capas juntas** en un único archivo SQLite ultrarrápido y estándar OGC. Solo arrástralo y suéltalo dentro de QGIS o ArcGIS.

### 4. `4_SVG_Vectores_Graficos_Illustrator/` (Gráficos Vectoriales Escalables)
Para diseño gráfico, infografías, tesis, ponencias y planos impresos:
- `monteria_mapa_completo_vectorial.svg`: Gráfico vectorial puro, editable en Adobe Illustrator, Inkscape o CorelDraw sin perder resolución al ampliarlo.
- `monteria_solo_limite_municipal.svg`: Contorno del polígono municipal.
- `monteria_mapa_completo_alta_resolucion.png`: Imagen de alta resolución (300 DPI).

### 5. `5_KML_Google_Earth/`
- Compatible con Google Earth Pro de escritorio (sin requerir conexión si ya tienes la zona en caché).

---

## Sistema de Coordenadas de Referencia (CRS)
- **EPSG: 4326** (WGS 84 - Coordenadas Geográficas estándar mundial).
