import os
import shutil
import zipfile
import geopandas as gpd
import matplotlib.pyplot as plt

# Definir carpetas de destino
BASE_DIR = r"c:\Users\pc\OneDrive\Desktop\Proyecto integrador 2"
OUT_DIR = os.path.join(BASE_DIR, "MAPAS_VECTORIALES_MONTERIA_OFFLINE")
SHP_DIR = os.path.join(OUT_DIR, "1_Shapefiles_ESRI_QGIS_ArcGIS")
GEOJSON_DIR = os.path.join(OUT_DIR, "2_GeoJSON_Web_GIS")
GPKG_DIR = os.path.join(OUT_DIR, "3_GeoPackage_OGC_Universal")
SVG_DIR = os.path.join(OUT_DIR, "4_SVG_Vectores_Graficos_Illustrator")
KML_DIR = os.path.join(OUT_DIR, "5_KML_Google_Earth")

for d in [SHP_DIR, GEOJSON_DIR, GPKG_DIR, SVG_DIR, KML_DIR]:
    os.makedirs(d, exist_ok=True)

print("Cargando capas base existentes...")
monteria_bnd = gpd.read_file(os.path.join(BASE_DIR, "mapa_GIS_Monteria", "monteria_boundary.geojson"))
cordoba_bnd = gpd.read_file(os.path.join(BASE_DIR, "mapa_GIS_Monteria", "cordoba_boundary.geojson"))
roads = gpd.read_file(os.path.join(BASE_DIR, "mapa_GIS_Monteria", "monteria_road_network.geojson"))

# Cargar nodos si existen
nodes_path = os.path.join(BASE_DIR, "datos_viales_monteria", "monteria_nodos_drive.geojson")
nodes = gpd.read_file(nodes_path) if os.path.exists(nodes_path) else None

# Asegurar CRS EPSG:4326 WGS84
for gdf in [monteria_bnd, cordoba_bnd, roads]:
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)
if nodes is not None and nodes.crs is None:
    nodes.set_crs(epsg=4326, inplace=True)

# Limpiar columnas complejas para exportación a Shapefile (evitar error de tipos lista/dict y truncamiento de 10 caracteres)
def clean_for_shp(df):
    clean = df.copy()
    for col in clean.columns:
        if clean[col].dtype == object:
            # Si contiene listas o diccionarios, pasarlo a string
            clean[col] = clean[col].apply(lambda x: str(x) if isinstance(x, (list, dict)) else x)
            # Acortar textos gigantes si los hay
            clean[col] = clean[col].astype(str).str.slice(0, 254)
    return clean

print("Exportando a 1_Shapefiles_ESRI_QGIS_ArcGIS...")
clean_for_shp(monteria_bnd).to_file(os.path.join(SHP_DIR, "monteria_limite_municipal.shp"))
clean_for_shp(cordoba_bnd).to_file(os.path.join(SHP_DIR, "cordoba_limite_departamental.shp"))
clean_for_shp(roads).to_file(os.path.join(SHP_DIR, "monteria_malla_vial.shp"))
if nodes is not None:
    clean_for_shp(nodes).to_file(os.path.join(SHP_DIR, "monteria_nodos_intersecciones.shp"))

print("Exportando a 2_GeoJSON_Web_GIS...")
monteria_bnd.to_file(os.path.join(GEOJSON_DIR, "monteria_limite_municipal.geojson"), driver="GeoJSON")
cordoba_bnd.to_file(os.path.join(GEOJSON_DIR, "cordoba_limite_departamental.geojson"), driver="GeoJSON")
roads.to_file(os.path.join(GEOJSON_DIR, "monteria_malla_vial.geojson"), driver="GeoJSON")
if nodes is not None:
    nodes.to_file(os.path.join(GEOJSON_DIR, "monteria_nodos_intersecciones.geojson"), driver="GeoJSON")

print("Exportando a 3_GeoPackage_OGC_Universal...")
gpkg_path = os.path.join(GPKG_DIR, "monteria_geopackage_completo.gpkg")
if os.path.exists(gpkg_path):
    os.remove(gpkg_path)
clean_for_shp(monteria_bnd).to_file(gpkg_path, layer="monteria_limite_municipal", driver="GPKG")
clean_for_shp(cordoba_bnd).to_file(gpkg_path, layer="cordoba_limite_departamental", driver="GPKG")
clean_for_shp(roads).to_file(gpkg_path, layer="monteria_malla_vial", driver="GPKG")
if nodes is not None:
    clean_for_shp(nodes).to_file(gpkg_path, layer="monteria_nodos_intersecciones", driver="GPKG")

print("Exportando a 4_SVG_Vectores_Graficos_Illustrator...")
# 1. Mapa completo (Límite + Vías)
fig, ax = plt.subplots(figsize=(14, 14), dpi=300)
monteria_bnd.plot(ax=ax, facecolor='#E8F5E9', edgecolor='#2E7D32', linewidth=2.5, label='Límite Montería')
roads.plot(ax=ax, color='#1565C0', linewidth=0.6, alpha=0.85, label='Malla Vial')
ax.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(os.path.join(SVG_DIR, "monteria_mapa_completo_vectorial.svg"), format='svg', bbox_inches='tight', pad_inches=0)
plt.savefig(os.path.join(SVG_DIR, "monteria_mapa_completo_alta_resolucion.png"), format='png', dpi=300, bbox_inches='tight', pad_inches=0)
plt.close()

# 2. Solo límite municipal
fig, ax = plt.subplots(figsize=(10, 10))
monteria_bnd.plot(ax=ax, facecolor='#E8F5E9', edgecolor='#1B5E20', linewidth=2.5)
ax.axis('off')
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig(os.path.join(SVG_DIR, "monteria_solo_limite_municipal.svg"), format='svg', bbox_inches='tight', pad_inches=0)
plt.close()

print("Exportando a 5_KML_Google_Earth...")
try:
    monteria_bnd[['name', 'geometry']].to_file(os.path.join(KML_DIR, "monteria_limite_municipal.kml"), driver="KML")
    cordoba_bnd[['name', 'geometry']].to_file(os.path.join(KML_DIR, "cordoba_limite_departamental.kml"), driver="KML")
except Exception as e:
    print(f"Aviso KML (se omitirá si falta driver GDAL KML): {e}")

# Crear archivo README explicativo
readme_content = """# Mapas Vectoriales de Montería y Córdoba (Uso 100% Offline / Fuera de Línea)

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
"""

with open(os.path.join(OUT_DIR, "LEEME_COMO_USAR_OFFLINE.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)

print("Creando archivo ZIP comprimido completo...")
zip_path = os.path.join(BASE_DIR, "MAPAS_VECTORIALES_MONTERIA_OFFLINE.zip")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(OUT_DIR):
        for file in files:
            file_abs = os.path.join(root, file)
            arcname = os.path.relpath(file_abs, BASE_DIR)
            zipf.write(file_abs, arcname)

print(f"¡TODO GENERADO CON ÉXITO!")
print(f"Carpeta: {OUT_DIR}")
print(f"Archivo ZIP: {zip_path} ({os.path.getsize(zip_path)/(1024*1024):.2f} MB)")
