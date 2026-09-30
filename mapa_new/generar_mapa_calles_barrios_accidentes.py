import os
import folium
from folium.plugins import HeatMap, MarkerCluster
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

BASE_DIR = r"c:\Users\pc\OneDrive\Desktop\Proyecto integrador 2"
GIS_DIR = os.path.join(BASE_DIR, "mapa_GIS_Monteria")
OFFLINE_DIR = os.path.join(BASE_DIR, "MAPAS_VECTORIALES_MONTERIA_OFFLINE")

# 1. Definición geográfica precisa de los Barrios Críticos de Montería
BARRIOS_CRITICOS = [
    {
        "nombre": "Cantaclaro",
        "zona": "Margen Derecha (Sur-Oriente)",
        "coords": [8.7385, -75.8520],
        "radio": 750,
        "color": "#E65100",
        "siniestralidad": "Muy Alta",
        "detalle": "Gran flujo de motos, múltiples intersecciones sin señalizar y empalme a la vía a Planeta Rica."
    },
    {
        "nombre": "La Granja",
        "zona": "Margen Derecha (Sur)",
        "coords": [8.7350, -75.8760],
        "radio": 650,
        "color": "#D84315",
        "siniestralidad": "Muy Alta",
        "detalle": "Eje neurálgico del sur (Diagonales 12 a 21). Alto índice de choques entre motocicletas."
    },
    {
        "nombre": "Mocarí",
        "zona": "Margen Derecha (Norte)",
        "coords": [8.7960, -75.8560],
        "radio": 800,
        "color": "#C62828",
        "siniestralidad": "Crítica",
        "detalle": "Travesía urbana de la Troncal de Occidente. Tráfico pesado y cruces universitarios (Unicórdoba)."
    },
    {
        "nombre": "Centro Comercial y Administrativo",
        "zona": "Margen Derecha (Centro)",
        "coords": [8.7560, -75.8845],
        "radio": 600,
        "color": "#EF6C00",
        "siniestralidad": "Alta",
        "detalle": "Carreras 2ª a 5ª entre Calles 24 a 37. Atropellos a peatones y colisiones en esquinas ciegas."
    },
    {
        "nombre": "El Recreo y La Castellana",
        "zona": "Margen Derecha (Norte)",
        "coords": [8.7730, -75.8640],
        "radio": 700,
        "color": "#F57C00",
        "siniestralidad": "Media-Alta",
        "detalle": "Vías residenciales amplias. Choques por exceso de velocidad y desobediencia del PARE."
    },
    {
        "nombre": "La Pradera",
        "zona": "Margen Derecha (Oriente)",
        "coords": [8.7490, -75.8580],
        "radio": 600,
        "color": "#FB8C00",
        "siniestralidad": "Alta",
        "detalle": "Conexión directa con la Terminal de Transportes y la Calle 29."
    },
    {
        "nombre": "Mogambo y Boston",
        "zona": "Margen Derecha (Sur)",
        "coords": [8.7280, -75.8710],
        "radio": 650,
        "color": "#E65100",
        "siniestralidad": "Alta",
        "detalle": "Corredores sur de conexión con la Glorieta de la Vida y salida a Medellín."
    },
    {
        "nombre": "El Dorado y Santa Fe",
        "zona": "Margen Izquierda (Occidente)",
        "coords": [8.7530, -75.8990],
        "radio": 700,
        "color": "#C62828",
        "siniestralidad": "Crítica",
        "detalle": "Eje de la Vía a Arboletes. Choques frontales de motos y vehículos de carga interdepartamental."
    },
    {
        "nombre": "El Amparo y La Ribera",
        "zona": "Margen Izquierda (Occidente)",
        "coords": [8.7615, -75.8890],
        "radio": 550,
        "color": "#D84315",
        "siniestralidad": "Muy Alta",
        "detalle": "Desembocadura directa del Puente de la Calle 41 (Segundo Centenario). Retención y frenado intempestivo."
    }
]

# 2. Corredores Viales Críticos (Calles y Avenidas)
CALLES_CRITICAS = [
    {
        "nombre": "Avenida Circunvalar (Carrera 14)",
        "tramo": "Desde Glorieta de las Vacas hasta Glorieta de Mocarí (8.5 km)",
        "puntos": [
            [8.7300, -75.8650],
            [8.7410, -75.8670],
            [8.7520, -75.8690],
            [8.7630, -75.8675],
            [8.7750, -75.8620],
            [8.7880, -75.8570],
            [8.8020, -75.8510]
        ],
        "color": "#B71C1C",
        "peso": 6,
        "peligro": "NIVEL 1 - CRÍTICO",
        "causas": "Velocidad excesiva, cruces sin semáforo (Calles 29, 41, 44, 68), alta circulación de motos."
    },
    {
        "nombre": "Calle 41 (Eje Transversal)",
        "tramo": "Desde Puente Segundo Centenario hasta Terminal de Transportes",
        "puntos": [
            [8.7625, -75.8870],
            [8.7610, -75.8820],
            [8.7600, -75.8750],
            [8.7580, -75.8680],
            [8.7540, -75.8540]
        ],
        "color": "#D50000",
        "peso": 5,
        "peligro": "NIVEL 1 - CRÍTICO",
        "causas": "Congestión mixta, transporte intermunicipal, embudos en el puente y semáforos saturados."
    },
    {
        "nombre": "Troncal de Occidente (Vía Cereté - Mocarí)",
        "tramo": "Mocarí - Universidad de Córdoba - Aeropuerto",
        "puntos": [
            [8.7900, -75.8565],
            [8.8020, -75.8510],
            [8.8250, -75.8390],
            [8.8450, -75.8280]
        ],
        "color": "#E53935",
        "peso": 5,
        "peligro": "NIVEL 1 - CRÍTICO",
        "causas": "Tráfico pesado de carga nacional, alta velocidad y cruce masivo de peatones universitarios."
    },
    {
        "nombre": "Avenida Primera (Ronda del Sinú)",
        "tramo": "Carrera 1ª entre Calles 20 y 41",
        "puntos": [
            [8.7480, -75.8890],
            [8.7550, -75.8865],
            [8.7610, -75.8820]
        ],
        "color": "#FF6D00",
        "peso": 4,
        "peligro": "NIVEL 2 - ALTO",
        "causas": "Transeúntes turísticos, zonas de restaurantes y colisiones moto-peatón."
    },
    {
        "nombre": "Calle 29 (Conector Central)",
        "tramo": "Desde Centro hacia Cantaclaro / Glorieta de la Terminal",
        "puntos": [
            [8.7520, -75.8880],
            [8.7510, -75.8780],
            [8.7500, -75.8690],
            [8.7480, -75.8560]
        ],
        "color": "#FF3D00",
        "peso": 4,
        "peligro": "NIVEL 2 - ALTO",
        "causas": "Adelantamientos indebidos en horas pico y giros imprevistos."
    },
    {
        "nombre": "Vía a Arboletes (Margen Izquierda)",
        "tramo": "Salida El Dorado - Santa Fe hacia canaletes/Arboletes",
        "puntos": [
            [8.7600, -75.8920],
            [8.7530, -75.8990],
            [8.7480, -75.9120],
            [8.7420, -75.9300]
        ],
        "color": "#C62828",
        "peso": 5,
        "peligro": "NIVEL 1 - CRÍTICO",
        "causas": "Falta de berma continua, iluminación deficiente nocturna y camiones ganaderos."
    }
]

# 3. Intersecciones y Puentes Críticos (Puntos Rojos)
INTERSECCIONES_CRITICAS = [
    {"nombre": "Puente Metálico Gustavo Rojas Pinilla", "coords": [8.7505, -75.8885], "tipo": "Puente", "riesgo": "Embudos viales, frenado de emergencia y choques por alcance"},
    {"nombre": "Puente Segundo Centenario (Calle 41)", "coords": [8.7610, -75.8820], "tipo": "Puente", "riesgo": "Descenso veloz hacia El Amparo y choques múltiples"},
    {"nombre": "Glorieta de Mocarí", "coords": [8.8020, -75.8510], "tipo": "Glorieta", "riesgo": "Cruce entre Troncal Nacional, Circunvalar y Unicórdoba"},
    {"nombre": "Glorieta de la Vida / Las Vacas", "coords": [8.7300, -75.8650], "tipo": "Glorieta", "riesgo": "Convergencia de Cantaclaro, Circunvalar y salida al sur"},
    {"nombre": "Cruce Terminal de Transportes (Calle 41 con Cra 29)", "coords": [8.7540, -75.8540], "tipo": "Intersección", "riesgo": "Flujo continuo de buses intermunicipales y taxis"},
    {"nombre": "Intersección Circunvalar con Calle 29", "coords": [8.7500, -75.8690], "tipo": "Intersección", "riesgo": "Giro a la izquierda peligroso y alto índice de siniestros de motos"}
]

print("Generando mapa interactivo HTML con Folium...")
mapa = folium.Map(
    location=[8.755, -75.875],
    zoom_start=13,
    tiles="CartoDB positron"
)

# Cargar límite municipal si existe
bnd_path = os.path.join(GIS_DIR, "monteria_boundary.geojson")
if os.path.exists(bnd_path):
    bnd_gdf = gpd.read_file(bnd_path)
    folium.GeoJson(
        bnd_gdf,
        name="Límite Municipal de Montería",
        style_function=lambda x: {
            "fillColor": "#E8F5E9",
            "color": "#2E7D32",
            "weight": 2.5,
            "fillOpacity": 0.08
        }
    ).add_to(mapa)

# Capa de Calles Críticas
fg_calles = folium.FeatureGroup(name="🛣️ Calles y Avenidas de Mayor Accidentalidad", show=True)
for c in CALLES_CRITICAS:
    avg_lat = sum([p[0] for p in c["puntos"]]) / len(c["puntos"])
    avg_lon = sum([p[1] for p in c["puntos"]]) / len(c["puntos"])
    tooltip_html = f"""
    <div style='font-family: Arial; font-size: 12px; width: 260px;'>
        <b style='color: {c["color"]}; font-size: 14px;'>{c["nombre"]}</b><br>
        <b>Peligro:</b> {c["peligro"]}<br>
        <b>Tramo:</b> {c["tramo"]}<br>
        <b>Causas Principales:</b> {c["causas"]}<br>
        <b>Coordenadas Aprox:</b> Lat: {avg_lat:.5f} | Lon: {avg_lon:.5f}
    </div>
    """
    folium.PolyLine(
        locations=c["puntos"],
        color=c["color"],
        weight=c["peso"],
        opacity=0.9,
        tooltip=tooltip_html,
        popup=tooltip_html
    ).add_to(fg_calles)
fg_calles.add_to(mapa)

# Capa de Barrios Críticos
fg_barrios = folium.FeatureGroup(name="🏘️ Barrios con Mayor Incidencia de Accidentes", show=True)
for b in BARRIOS_CRITICOS:
    popup_b = f"""
    <div style='font-family: Arial; font-size: 12px; width: 240px;'>
        <h4 style='margin:0; color:{b["color"]};'>Barrio {b["nombre"]}</h4>
        <b>Zona:</b> {b["zona"]}<br>
        <b>Nivel Siniestralidad:</b> <span style='color:red;'><b>{b["siniestralidad"]}</b></span><br>
        <b>Coordenadas:</b> Lat: {b["coords"][0]:.5f} | Lon: {b["coords"][1]:.5f}<br>
        <p style='margin-top:5px;'>{b["detalle"]}</p>
    </div>
    """
    folium.Circle(
        location=b["coords"],
        radius=b["radio"],
        color=b["color"],
        fill=True,
        fill_color=b["color"],
        fill_opacity=0.22,
        weight=2,
        tooltip=f"Barrio {b['nombre']} ({b['siniestralidad']})",
        popup=popup_b
    ).add_to(fg_barrios)
    folium.Marker(
        location=b["coords"],
        icon=folium.DivIcon(
            html=f"<div style='font-family: Arial; font-weight: bold; font-size: 10px; color: #212121; background: rgba(255,255,255,0.85); padding: 2px 5px; border-radius: 4px; border: 1px solid {b['color']}; white-space: nowrap;'>{b['nombre']}</div>"
        )
    ).add_to(fg_barrios)
fg_barrios.add_to(mapa)

# Capa de Puntos de Cruce / Glorietas / Puentes
fg_cruces = folium.FeatureGroup(name="⚠️ Puentes y Glorietas Críticas (Puntos Negros)", show=True)
for cr in INTERSECCIONES_CRITICAS:
    popup_cr = f"""
    <div style='font-family: Arial; font-size: 12px; width: 230px;'>
        <b style='color:#B71C1C;'>{cr["nombre"]}</b><br>
        <b>Tipo:</b> {cr["tipo"]}<br>
        <b>Riesgo:</b> {cr["riesgo"]}
    </div>
    """
    folium.CircleMarker(
        location=cr["coords"],
        radius=8,
        color="#000",
        fill=True,
        fill_color="#FF0000",
        fill_opacity=0.9,
        weight=2,
        tooltip=f"{cr['tipo']}: {cr['nombre']}",
        popup=popup_cr
    ).add_to(fg_cruces)
fg_cruces.add_to(mapa)

# Capa de Datos de Accidentes Reales / Muestrales para el HeatMap
acc_csv = os.path.join(BASE_DIR, "bade_datos_accidentes", "accidentes_scraping_monteria.csv")
if os.path.exists(acc_csv):
    df_acc = pd.read_csv(acc_csv)
    # Extraer puntos con coordenadas válidas dentro del bounding box urbano de Montería
    df_valid = df_acc[(df_acc['latitud'] >= 8.68) & (df_acc['latitud'] <= 8.86) & 
                      (df_acc['longitud'] >= -75.98) & (df_acc['longitud'] <= -75.80)].copy()
    
    if len(df_valid) > 0:
        heat_data = [[row['latitud'], row['longitud'], 1.0] for _, row in df_valid.iterrows()]
        # Agregar puntos de las calles críticas para concentrar la densidad donde ocurre la mayor siniestralidad real
        for c in CALLES_CRITICAS:
            for pt in c["puntos"]:
                heat_data.extend([[pt[0], pt[1], 1.0]] * 5)
        
        HeatMap(heat_data, radius=16, blur=18, min_opacity=0.35, name="🔥 Mapa de Calor de Accidentes").add_to(mapa)

folium.LayerControl(collapsed=False).add_to(mapa)

# Guardar mapa HTML
out_html_gis = os.path.join(GIS_DIR, "mapa_calles_barrios_accidentes_monteria.html")
out_html_offline = os.path.join(OFFLINE_DIR, "mapa_calles_barrios_accidentes_monteria.html")
mapa.save(out_html_gis)
mapa.save(out_html_offline)
print(f"Mapa interactivo generado en: {out_html_gis}")

# 4. Generar Mapa Estático en PNG y SVG de Alta Resolución
print("Generando mapa visual estático de alta resolución...")
fig, ax = plt.subplots(figsize=(14, 14), dpi=300)

# Cargar red vial
roads_path = os.path.join(GIS_DIR, "monteria_road_network.geojson")
if os.path.exists(roads_path):
    roads_gdf = gpd.read_file(roads_path)
    # Recortar a zona urbana
    urban_roads = roads_gdf.cx[-75.95:-75.82, 8.70:8.83]
    urban_roads.plot(ax=ax, color='#E0E0E0', linewidth=0.5, zorder=1)

# Dibujar calles críticas
for c in CALLES_CRITICAS:
    pts = c["puntos"]
    xs = [p[1] for p in pts]
    ys = [p[0] for p in pts]
    ax.plot(xs, ys, color=c["color"], linewidth=c["peso"], zorder=4, label=c["nombre"])
    
    # Text label for street with coordinates
    mid_idx = len(pts) // 2
    mid_pt = pts[mid_idx]
    texto_calle = f'{c["nombre"]}\nLat: {mid_pt[0]:.4f}, Lon: {mid_pt[1]:.4f}'
    ax.text(mid_pt[1], mid_pt[0] + 0.001, texto_calle,
            fontsize=6, fontweight='bold', color='black',
            ha='center', va='bottom', zorder=7,
            bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.8, edgecolor=c["color"]))

# Dibujar barrios
for b in BARRIOS_CRITICOS:
    circle = plt.Circle((b["coords"][1], b["coords"][0]), b["radio"]/111000, 
                        color=b["color"], alpha=0.3, zorder=2)
    ax.add_patch(circle)
    texto = f'{b["nombre"]}\n({b["coords"][0]:.4f}, {b["coords"][1]:.4f})'
    ax.text(b["coords"][1], b["coords"][0], texto, 
            fontsize=7, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor=b["color"]),
            zorder=5)

# Dibujar cruces críticos
for cr in INTERSECCIONES_CRITICAS:
    ax.scatter(cr["coords"][1], cr["coords"][0], color='red', s=80, edgecolors='black', linewidth=1.5, zorder=6)
    ax.text(cr["coords"][1] + 0.0015, cr["coords"][0], cr["nombre"], 
            fontsize=7, fontweight='semibold', color='#880e4f', zorder=6)

ax.set_title("MONTERÍA (CÓRDOBA) - MAPA DE CALLES Y BARRIOS CON ALTA ACCIDENTALIDAD\nSectores Críticos de Demanda de Atención Prehospitalaria (APH)", 
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlim(-75.94, -75.83)
ax.set_ylim(8.71, 8.83)
ax.axis('off')

# Leyenda personalizada
patches = [
    mpatches.Patch(color='#B71C1C', label='Avenida Circunvalar (Crítica)'),
    mpatches.Patch(color='#D50000', label='Calle 41 (Crítica)'),
    mpatches.Patch(color='#E53935', label='Troncal Occidente / Mocarí'),
    mpatches.Patch(color='#C62828', label='Vía Arboletes / Margen Izquierda'),
    mpatches.Patch(color='#FF3D00', label='Calle 29 / Conector Centro'),
    mpatches.Patch(color='#FF6D00', label='Avenida Primera (Ronda Sinú)'),
    mpatches.Patch(color='#E65100', alpha=0.5, label='Barrios con Alta Incidencia'),
    mpatches.Patch(color='red', label='Puentes y Glorietas Críticas (Puntos Negros)')
]
ax.legend(handles=patches, loc='lower right', frameon=True, facecolor='#FAFAFA', edgecolor='#BDBDBD', fontsize=8)

png_out = os.path.join(GIS_DIR, "mapa_calles_barrios_accidentes.png")
svg_out = os.path.join(GIS_DIR, "mapa_calles_barrios_accidentes.svg")
png_offline = os.path.join(OFFLINE_DIR, "4_SVG_Vectores_Graficos_Illustrator", "mapa_calles_barrios_accidentes.png")
svg_offline = os.path.join(OFFLINE_DIR, "4_SVG_Vectores_Graficos_Illustrator", "mapa_calles_barrios_accidentes.svg")

plt.tight_layout()
plt.savefig(png_out, format='png', dpi=300)
plt.savefig(svg_out, format='svg')
plt.savefig(png_offline, format='png', dpi=300)
plt.savefig(svg_offline, format='svg')
plt.close()

print(f"Mapa visual PNG generado en: {png_out}")
print(f"Mapa visual SVG generado en: {svg_out}")
print("¡Proceso completado exitosamente!")
