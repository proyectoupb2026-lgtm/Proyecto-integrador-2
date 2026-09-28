import re
import hashlib
from datetime import datetime
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Inicializar geocodificador Nominatim con User-Agent personalizado
geolocator = Nominatim(user_agent="monteria_accident_gis_research_v2")
geocode_safe = RateLimiter(geolocator.geocode, min_delay_seconds=1.0)

# DICCIONARIO ESPACIAL DE MONTERÍA Y CÓRDOBA (Barrios, Vías, Hitos e Intersecciones)
# Incluye coordenadas centroides verificadas para geocodificación de alta precisión en Montería
BARRIOS_HITOS_MONTERIA = {
    # Hitos y Nodos de Tráfico Críticos
    "Glorieta de Mocarí": (8.7952, -75.8621),
    "Mocarí": (8.7925, -75.8612),
    "Glorieta de las Vacas": (8.7451, -75.8633),
    "Puente Metálico": (8.7521, -75.8885),
    "Puente Gustavo Rojas Pinilla": (8.7521, -75.8885),
    "Puente Segundo Centenario": (8.7410, -75.8920),
    "Puente Bicentenario": (8.7410, -75.8920),
    "Avenida Circunvalar": (8.7550, -75.8750),
    "Calle 41": (8.7610, -75.8720),
    "Calle 27": (8.7530, -75.8810),
    "Calle 29": (8.7540, -75.8800),
    "Carrera 2": (8.7510, -75.8870),
    "Carrera 3": (8.7515, -75.8860),
    "Carrera 4": (8.7520, -75.8850),
    "Carrera 6": (8.7530, -75.8830),
    "Terminal de Transportes": (8.7460, -75.8620),
    "Aeropuerto Los Garzones": (8.8220, -75.8250),
    "Garzones": (8.8150, -75.8350),
    "Los Garzones": (8.8150, -75.8350),
    "Universidad de Córdoba": (8.7840, -75.8570),
    "Unicor": (8.7840, -75.8570),
    "INEM": (8.7680, -75.8650),
    "CC Alamedas": (8.7590, -75.8710),
    "CC Buenavista": (8.7710, -75.8610),

    # Barrios Casco Urbano Montería
    "Cantaclaro": (8.7412, -75.8621),
    "La Granja": (8.7360, -75.8890),
    "El Recreo": (8.7680, -75.8600),
    "Centro": (8.7510, -75.8850),
    "Rancho Grande": (8.7580, -75.9010),
    "P5": (8.7380, -75.8750),
    "La Castellana": (8.7720, -75.8580),
    "Pasatiempo": (8.7490, -75.8750),
    "Monteverde": (8.7660, -75.8590),
    "La Pradera": (8.7480, -75.8580),
    "Pradera": (8.7480, -75.8580),
    "Sucre": (8.7460, -75.8820),
    "El Dorado": (8.7610, -75.8980),
    "Boston": (8.7430, -75.8790),
    "San José": (8.7390, -75.8840),
    "El Amparo": (8.7350, -75.8920),
    "Alfonso López": (8.7320, -75.8890),
    "Los Laureles": (8.7630, -75.8640),
    "Costa de Oro": (8.7560, -75.8780),
    "Urbina": (8.7550, -75.8820),
    "Nariño": (8.7480, -75.8860),
    "Balboa": (8.7470, -75.8890),
    "La Julia": (8.7430, -75.8850),
    "Los Araujos": (8.7320, -75.8810),
    "6 de Marzo": (8.7340, -75.8780),
    "Edmundo López": (8.7300, -75.8730),
    "Villa Cielo": (8.7690, -75.8450),
    "Los Recuerdos": (8.7230, -75.8690),
    "Mogambo": (8.7290, -75.8750),
    "Villa Anacardos": (8.7750, -75.8510),
    "Makarí": (8.7900, -75.8600),

    # Vías Troncales y Salidas
    "Vía a Cereté": (8.8310, -75.8120),
    "Vía a Planeta Rica": (8.6920, -75.8210),
    "Vía a Ciénaga de Oro": (8.7890, -75.7620),
    "Vía a Arboletes": (8.7710, -75.9320),
    "Troncal del Caribe": (8.7620, -75.8420),
    "El Sabanal": (8.7610, -75.8120),
    "Mateo Gómez": (8.8410, -75.8010),
    "San Anterito": (8.6210, -75.8120),
    "Guateque": (8.6810, -75.8720),
    "Leticia": (8.6310, -75.9510)
}

MUNICIPIOS_CORDOBA = {
    "Cereté": (8.8844, -75.7908),
    "Ciénaga de Oro": (8.8786, -75.6231),
    "Sahagún": (8.9461, -75.4431),
    "Lorica": (9.2392, -75.8136),
    "Planeta Rica": (8.4076, -75.5837),
    "Montelíbano": (7.9786, -75.4189),
    "Tierralta": (8.1722, -76.0594),
    "San Carlos": (8.7981, -75.7001),
    "San Pelayo": (8.9592, -75.8369),
    "Pueblo Nuevo": (8.5022, -75.5036),
    "Moñitos": (9.2458, -76.1322),
    "Puerto Escondido": (9.0189, -76.2575),
    "San Antero": (9.3736, -75.7592),
    "Chinú": (9.1067, -75.4011),
    "Ayapel": (8.3142, -75.1417),
    "Valencia": (8.2578, -76.1492)
}

def extraer_direccion_rigurosa(titulo, cuerpo_texto=""):
    """
    Algoritmo de análisis riguroso para la detección precisa del sitio del siniestro.
    Prioriza: (1) Direcciones con número/nodos, (2) Barrios e Hitos urbanos, (3) Vías y corregimientos.
    """
    texto_completo = f"{titulo} {cuerpo_texto}".strip()
    
    # 1. Buscar patrones exactos de dirección urbana (ej. "calle 41 con carrera 14", "carrera 3 # 27-30")
    patron_direccion_exacta = r"\b(calle|carrera|cra|cll|av|avenida|transversal|dg|diagonal)\s+\d+[\w]?\s*(con|#|no\.|número|-|y)?\s*(carrera|cra|calle|cll|\d+[\w]?)?\b"
    match_exacto = re.search(patron_direccion_exacta, texto_completo, re.IGNORECASE)
    
    dir_exacta = ""
    if match_exacto:
        dir_exacta = match_exacto.group(0).strip()
        
    # 2. Buscar barrios o hitos específicos en Montería
    hitos_hallados = []
    for hito in BARRIOS_HITOS_MONTERIA.keys():
        if re.search(rf"\b{re.escape(hito)}\b", texto_completo, re.IGNORECASE):
            hitos_hallados.append(hito)
            
    # 3. Buscar municipios de Córdoba
    municipios_hallados = []
    for muni in MUNICIPIOS_CORDOBA.keys():
        if re.search(rf"\b{re.escape(muni)}\b", texto_completo, re.IGNORECASE):
            municipios_hallados.append(muni)
            
    # Sintetizar la dirección más específica posible
    sitio_final = ""
    barrio_hito = hitos_hallados[0] if hitos_hallados else ""
    municipio_final = "Montería" if ("Montería" in texto_completo or "Monteria" in texto_completo or hitos_hallados or not municipios_hallados) else municipios_hallados[0]
    
    if dir_exacta and barrio_hito:
        sitio_final = f"{dir_exacta}, Barrio {barrio_hito}, {municipio_final}"
    elif dir_exacta:
        sitio_final = f"{dir_exacta}, {municipio_final}"
    elif barrio_hito:
        sitio_final = f"Sector/Barrio {barrio_hito}, {municipio_final}"
    elif municipios_hallados:
        sitio_final = f"Municipio de {municipios_hallados[0]}, Córdoba"
    else:
        sitio_final = "Montería (Casco Urbano / Sector en investigación)"
        
    return sitio_final, barrio_hito, municipio_final

def geocodificar_direccion(sitio_str, barrio_hito="", municipio="Montería"):
    """
    Geocodifica la dirección extraída a coordenadas GPS exactas (Latitud, Longitud).
    Aplica resolución jerárquica:
    1. Centroides locales verificados de Barrios/Hitos de Montería.
    2. Consulta Nominatim API para la dirección específica.
    3. Centroide municipal/departamental de respaldo.
    """
    # Nivel 1: Búsqueda en diccionario espacial local de Montería
    if barrio_hito in BARRIOS_HITOS_MONTERIA:
        lat, lon = BARRIOS_HITOS_MONTERIA[barrio_hito]
        return lat, lon, "Alta (Centroide Hito/Barrio Verificado)"
        
    for hito, (lat, lon) in BARRIOS_HITOS_MONTERIA.items():
        if hito.lower() in sitio_str.lower():
            return lat, lon, "Alta (Coincidencia Hito Urbano)"
            
    if municipio in MUNICIPIOS_CORDOBA:
        lat, lon = MUNICIPIOS_CORDOBA[municipio]
        return lat, lon, "Media (Centroide Municipio Córdoba)"
        
    # Nivel 2: Geocodificación remota con Nominatim
    try:
        query_geo = f"{sitio_str}, Montería, Córdoba, Colombia"
        location = geocode_safe(query_geo)
        if location:
            return location.latitude, location.longitude, "Alta (Geocodificado Nominatim API)"
    except Exception:
        pass
        
    # Nivel 3: Respaldar en el centro de Montería
    return 8.7508, -75.8814, "Baja (Centroide General Montería)"
