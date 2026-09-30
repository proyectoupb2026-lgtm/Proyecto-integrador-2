# 08 — Manual de Despliegue e Instalación

## Requisitos del Sistema

| Requisito | Mínimo | Recomendado |
|-----------|--------|-------------|
| Sistema Operativo | Windows 10 64-bit | Windows 11 64-bit |
| Python | 3.10 | 3.13 |
| RAM | 4 GB | 8 GB |
| Disco libre | 500 MB | 1 GB |
| Conexión a internet | Opcional (tiles OSM) | Sí para primera ejecución |

---

## Instalación de Dependencias

```bash
pip install PyQt5 PyQtWebEngine pulp simpy numpy folium pandas scikit-learn pyinstaller osmnx networkx
```

| Librería | Versión mínima | Función |
|----------|----------------|---------|
| `PyQt5` | 5.15 | Interfaz gráfica nativa |
| `PyQtWebEngine` | 5.15 | Visor de mapas HTML embebido |
| `pulp` | 2.7 | Solver MILP (usa CBC interno) |
| `simpy` | 4.0 | Motor de simulación de eventos discretos |
| `folium` | 0.14 | Generación de mapas Leaflet.js |
| `pandas` | 1.5 | Lectura y procesamiento del CSV |
| `numpy` | 1.24 | Cálculos matriciales |
| `scikit-learn` | 1.2 | KMeans para centros de demanda |
| `osmnx` | 1.6 | Descarga de red vial OSM (script aparte) |

---

## Estructura de Archivos Requerida

```
Proyecto integrador 2/
├── gemelo_digital_desktop.py          ← Aplicación principal
├── accidentes_verificados_actualizados.csv  ← Dataset de accidentes
├── MAPAS_VECTORIALES_MONTERIA_OFFLINE/
│   └── 2_GeoJSON_Web_GIS/
│       └── monteria_malla_vial.geojson     ← Red vial offline
├── temp_map.html                      ← Generado automáticamente en runtime
└── documentacion/                     ← Esta carpeta
```

---

## Ejecución

```bash
# Desde la carpeta del proyecto:
python gemelo_digital_desktop.py
```

---

## Compilación a Ejecutable (.exe)

Para distribuir la app sin necesitar Python instalado:

```bash
# Opción 1: Ejecutar el script de compilación
compilar_exe.bat

# Opción 2: Comando directo
pyinstaller --onedir --windowed --name "GemeloDigital_APH" gemelo_digital_desktop.py
```

> **Nota:** Después de compilar, copia manualmente los archivos de datos (`accidentes_verificados_actualizados.csv` y la carpeta `MAPAS_VECTORIALES_MONTERIA_OFFLINE/`) dentro de la carpeta `dist/GemeloDigital_APH/` para que el ejecutable los encuentre.

---

## Solución de Problemas Frecuentes

| Error | Causa | Solución |
|-------|-------|----------|
| `Unable to move the cache: Acceso denegado` | GPU cache de QtWebEngine bloqueado | Ya corregido con env vars en líneas 5-7 del script |
| `No se encontró solución óptima` | Las capacidades de las bases son menores que la flota $p$ | Aumentar capacidades o reducir la flota |
| `Mapa no carga` | `temp_map.html` no encontrado | Verificar permisos de escritura en la carpeta del proyecto |
| `KMeans: n_samples < n_clusters` | CSV con menos filas que el número de nodos/bases | Reducir nodos/bases o verificar el CSV |
