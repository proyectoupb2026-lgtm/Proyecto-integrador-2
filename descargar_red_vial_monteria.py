"""
Script para descargar, procesar y exportar la red vial de Montería, Córdoba, Colombia.
Genera formatos GeoJSON y Shapefile (.shp) para QGIS, además de mapas preliminares (PNG y HTML interactivo).
"""

import os
import sys
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import osmnx as ox
import folium

# Configuración de OSMnx para mostrar logs y optimizar descargas
ox.settings.log_console = True
ox.settings.use_cache = True

def main():
    print("=" * 60, flush=True)
    print("Iniciando descarga de la red vial de Montería, Córdoba...", flush=True)
    print("=" * 60, flush=True)

    lugar = "Montería, Córdoba, Colombia"
    
    # 1. Descarga del grafo vial desde OpenStreetMap
    print(f"\n[1/5] Descargando red vial ('drive') para: {lugar}...", flush=True)
    G = ox.graph_from_place(lugar, network_type="drive", simplify=True)
    print(f" -> Grafo descargado exitosamente: {len(G.nodes):,} nodos y {len(G.edges):,} tramos de vía.", flush=True)

    # 2. Conversión a GeoDataFrames
    print("\n[2/5] Convirtiendo grafo a GeoDataFrames (nodos y aristas)...", flush=True)
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
    print(f" -> GeoDataFrame de vías (aristas): {gdf_edges.shape[0]} registros", flush=True)
    print(f" -> GeoDataFrame de intersecciones (nodos): {gdf_nodes.shape[0]} registros", flush=True)

    # Crear directorio de salida
    salida_dir = Path("./datos_viales_monteria")
    salida_dir.mkdir(exist_ok=True)
    shp_dir = salida_dir / "shapefiles"
    shp_dir.mkdir(exist_ok=True)

    # 3. Exportar a GeoJSON
    print("\n[3/5] Guardando archivos en formato GeoJSON...", flush=True)
    geojson_edges_path = salida_dir / "monteria_red_vial_drive.geojson"
    geojson_nodes_path = salida_dir / "monteria_nodos_drive.geojson"
    
    gdf_edges.to_file(geojson_edges_path, driver="GeoJSON")
    print(f" -> Vías guardadas en: {geojson_edges_path}", flush=True)
    gdf_nodes.to_file(geojson_nodes_path, driver="GeoJSON")
    print(f" -> Nodos guardados en: {geojson_nodes_path}", flush=True)

    # 4. Preparar y exportar a Shapefile (.shp)
    # Shapefile tiene restricciones: nombres de columnas max 10 caracteres y no soporta tipos complejos (listas)
    print("\n[4/5] Procesando y guardando archivos en formato Shapefile (.shp)...", flush=True)
    
    def preparar_para_shapefile(gdf):
        gdf_shp = gdf.copy()
        # Convertir columnas de tipo lista o diccionarios a strings
        for col in gdf_shp.columns:
            if col == "geometry":
                continue
            gdf_shp[col] = gdf_shp[col].apply(
                lambda val: ", ".join(map(str, val)) if isinstance(val, (list, tuple, set)) else (str(val) if isinstance(val, dict) else val)
            )
            # Asegurar tipo compatible para columnas 'object'
            if gdf_shp[col].dtype == "object":
                gdf_shp[col] = gdf_shp[col].astype(str)
        return gdf_shp

    edges_shp = preparar_para_shapefile(gdf_edges)
    nodes_shp = preparar_para_shapefile(gdf_nodes)

    shp_edges_path = shp_dir / "monteria_red_vial_drive.shp"
    shp_nodes_path = shp_dir / "monteria_nodos_drive.shp"

    edges_shp.to_file(shp_edges_path, driver="ESRI Shapefile", encoding="utf-8")
    print(f" -> Shapefile de vías guardado en: {shp_edges_path}", flush=True)
    nodes_shp.to_file(shp_nodes_path, driver="ESRI Shapefile", encoding="utf-8")
    print(f" -> Shapefile de nodos guardado en: {shp_nodes_path}", flush=True)

    # 5. Generar visualización preliminar (Matplotlib y Folium)
    print("\n[5/5] Generando mapas preliminares de verificación...", flush=True)
    
    # 5.1 Mapa en Matplotlib (PNG de alta resolución)
    png_path = salida_dir / "mapa_red_vial_monteria.png"
    print(" -> Creando mapa estático en alta resolución (Matplotlib)...", flush=True)
    
    # Clasificación de vías para estilos
    def get_color_and_width(highway_type):
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        highway_type = str(highway_type)
        if highway_type in ["motorway", "trunk", "motorway_link", "trunk_link"]:
            return "#ff3366", 2.2, 5  # Primaria rápida / Troncal
        elif highway_type in ["primary", "primary_link"]:
            return "#ffaa00", 1.6, 4  # Primaria
        elif highway_type in ["secondary", "secondary_link"]:
            return "#00d4ff", 1.2, 3  # Secundaria
        elif highway_type in ["tertiary", "tertiary_link"]:
            return "#2ecc71", 0.9, 2  # Terciaria
        elif highway_type in ["residential", "living_street"]:
            return "#ffffff", 0.5, 1  # Residencial
        else:
            return "#8899aa", 0.4, 0  # Otras (rurales/unclassified)

    fig, ax = plt.subplots(figsize=(14, 14), facecolor="#0e1117")
    ax.set_facecolor("#0e1117")

    # Mapear estilos según columna 'highway'
    if "highway" in gdf_edges.columns:
        # Agrupamos por categoría para renderizar por capas
        gdf_plot = gdf_edges.copy()
        gdf_plot["hw_base"] = gdf_plot["highway"].apply(
            lambda x: x[0] if isinstance(x, list) else str(x)
        )
        
        # Dibujar por grupos de jerarquía para buen orden visual
        categorias = [
            ("Otras / Sin clasificar", ["unclassified", "service", "road"], "#5c6b73", 0.4),
            ("Vías Residenciales", ["residential", "living_street"], "#c0c6c9", 0.6),
            ("Vías Terciarias", ["tertiary", "tertiary_link"], "#2ecc71", 1.0),
            ("Vías Secundarias", ["secondary", "secondary_link"], "#00c4ff", 1.4),
            ("Vías Primarias", ["primary", "primary_link"], "#ffaa00", 1.8),
            ("Autovías / Troncales", ["motorway", "trunk", "motorway_link", "trunk_link"], "#ff3366", 2.4),
        ]

        for label, tipos, color, width in categorias:
            sub_gdf = gdf_plot[gdf_plot["hw_base"].isin(tipos)]
            if not sub_gdf.empty:
                sub_gdf.plot(ax=ax, color=color, linewidth=width, label=label, alpha=0.9)
                
        # Resto que no haya entrado en categorías
        rest_types = [t for cat in categorias for t in cat[1]]
        resto_gdf = gdf_plot[~gdf_plot["hw_base"].isin(rest_types)]
        if not resto_gdf.empty:
            resto_gdf.plot(ax=ax, color="#7f8c8d", linewidth=0.5, alpha=0.5)
    else:
        gdf_edges.plot(ax=ax, color="#00e5ff", linewidth=0.7, alpha=0.8)

    ax.set_title("RED VIAL DE MONTERÍA, CÓRDOBA (COLOMBIA)\nNetwork Type: Drive | OpenStreetMap & OSMnx",
                 color="#ffffff", fontsize=16, fontweight="bold", pad=20, loc="left")
    
    # Subtítulo con estadísticas
    ax.text(0.01, 0.02,
            f"Vías (aristas): {len(gdf_edges):,} | Nodos (intersecciones): {len(gdf_nodes):,}\nCRS: EPSG:4326 (WGS 84)",
            transform=ax.transAxes, color="#8b9bb4", fontsize=10, verticalalignment="bottom")

    ax.legend(loc="lower right", facecolor="#1a1f2c", edgecolor="#2d3748",
              fontsize=9, labelcolor="#e2e8f0", title="Jerarquía Vial", title_fontsize=10)
    
    # Estética de ejes
    ax.tick_params(colors="#718096", labelsize=8)
    ax.grid(color="#1f2937", linestyle="--", linewidth=0.5, alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color("#2d3748")

    plt.tight_layout()
    plt.savefig(png_path, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f" -> Mapa estático guardado en: {png_path}", flush=True)

    # 5.2 Mapa Interactivo en Folium (HTML)
    html_path = salida_dir / "mapa_red_vial_monteria.html"
    print(" -> Creando mapa interactivo (Folium)...", flush=True)
    
    # Calcular centro
    bounds = gdf_edges.total_bounds  # minx, miny, maxx, maxy
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=13,
        tiles="CartoDB dark_matter",
        control_scale=True
    )

    # Preparar subset limpio para Folium interactivo
    gdf_folium = gdf_edges[["geometry", "name", "highway", "length"]].copy()
    gdf_folium["name"] = gdf_folium["name"].apply(lambda x: ", ".join(map(str, x)) if isinstance(x, list) else (str(x) if x is not None else "Sin nombre"))
    gdf_folium["highway"] = gdf_folium["highway"].apply(lambda x: ", ".join(map(str, x)) if isinstance(x, list) else str(x))
    gdf_folium["length"] = gdf_folium["length"].apply(lambda x: f"{float(x):.1f} m" if x is not None else "")

    folium.GeoJson(
        gdf_folium.to_json(),
        name="Red Vial Montería",
        style_function=lambda feature: {
            "color": "#00f2fe",
            "weight": 1.5,
            "opacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "highway", "length"],
            aliases=["Nombre:", "Tipo:", "Longitud:"],
            localize=True
        )
    ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(str(html_path))
    print(f" -> Mapa interactivo guardado en: {html_path}", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("¡PROCESO COMPLETADO EXITOSAMENTE!", flush=True)
    print(f"Archivos disponibles en: {salida_dir.resolve()}", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
