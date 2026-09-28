import re
import hashlib
from datetime import datetime

# Patrones Regex para vehículos
VEHICLE_PATTERNS = {
    "Motocicleta": r"\b(moto|motocicleta|motocarro|bici-moto|ciclomotor)\b",
    "Automóvil": r"\b(carro|automóvil|automovil|vehículo particular|camioneta|campero|taxi)\b",
    "Camión / Carga": r"\b(camión|camion|furgón|tractomula|mula|volqueta|tractocamión)\b",
    "Bus / Transporte Público": r"\b(bus|buseta|microbús|colectivo|transporte público)\b",
    "Bicicleta": r"\b(bicicleta|ciclista|bici)\b",
    "Peatón": r"\b(peatón|peaton|transeúnte|transeunte)\b"
}

# Barrios y Sectores clave de Montería y Córdoba
LUGARES_MONTERIA_CORDOBA = [
    "Mocarí", "Mocari", "Cantaclaro", "La Granja", "El Recreo", "Centro", "Rancho Grande",
    "P5", "La Castellana", "Pasatiempo", "Monteverde", "Pradera", "Sucre", "Garzones",
    "Avenida Circunvalar", "Calle 27", "Calle 41", "Carrera 3", "Carrera 2", "Puente Metálico",
    "Puente Segundo Centenario", "Puente Bicentenario", "Vía a Cereté", "Vía a Planeta Rica",
    "Vía a Ciénaga de Oro", "Vía a Sahagún", "Vía a Arboletes", "Troncal del Caribe",
    "Glorieta de Mocarí", "Glorieta de las Vacas", "Bateas", "Leticia", "Kilómetro 15",
    "Cereté", "Sahagún", "Lorica", "Planeta Rica", "Ciénaga de Oro", "Montelíbano", "Tierralta"
]

def hash_accidente(titulo, fecha_str=""):
    """Genera un Hash SHA256 único para detectar y evitar duplicados de un mismo noticia/evento."""
    cadena = f"{titulo.strip().lower()}_{fecha_str.strip()}"
    return hashlib.sha256(cadena.encode('utf-8')).hexdigest()

def extraer_vehiculos(texto):
    """Identifica los tipos de vehículos involucrados a partir del texto."""
    texto_lower = texto.lower()
    involucrados = []
    for tipo, patron in VEHICLE_PATTERNS.items():
        if re.search(patron, texto_lower):
            involucrados.append(tipo)
    return ", ".join(involucrados) if involucrados else "No especificado"

def extraer_fallecidos(texto):
    """Extrae si hubo fallecidos y la cantidad estimada."""
    texto_lower = texto.lower()
    patron_muertos = r"\b(falleció|fallecieron|muerto|muertos|víctima mortal|víctimas mortales|perdió la vida|perdieron la vida|murió|murieron|fallecido|fallecida)\b"
    
    match = re.search(patron_muertos, texto_lower)
    if not match:
        return False, 0
        
    # Intentar extraer número si antecede a la palabra muerto/fallecido
    num_match = re.search(r"\b(\d+|un|una|dos|tres|cuatro|cinco)\s+(persona[s]?\s+)?(fallecida|fallecido|muerto|fallecieron)\b", texto_lower)
    cant = 1
    if num_match:
        val = num_match.group(1)
        mapa_num = {"un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
        cant = mapa_num.get(val, int(val) if val.isdigit() else 1)
        
    return True, cant

def extraer_heridos(texto):
    """Extrae si hubo heridos y la cantidad estimada."""
    texto_lower = texto.lower()
    patron_heridos = r"\b(herido|heridos|lesionado|lesionados|herida|heridas)\b"
    
    match = re.search(patron_heridos, texto_lower)
    if not match:
        return False, 0
        
    num_match = re.search(r"\b(\d+|un|una|dos|tres|cuatro|cinco)\s+(persona[s]?\s+)?(herida|heridas|lesionada|lesionados)\b", texto_lower)
    cant = 1
    if num_match:
        val = num_match.group(1)
        mapa_num = {"un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
        cant = mapa_num.get(val, int(val) if val.isdigit() else 1)
        
    return True, cant

def extraer_direccion_lugar(texto):
    """Extrae la ubicación específica de Montería o Córdoba mencionada en la noticia."""
    texto_lower = texto.lower()
    encontrados = []
    
    for lugar in LUGARES_MONTERIA_CORDOBA:
        if re.search(rf"\b{re.escape(lugar.lower())}\b", texto_lower):
            encontrados.append(lugar)
            
    # Búsqueda genérica por patrones de dirección (ej: "barrio X", "sector Y", "vía a Z", "calle N")
    match_sector = re.search(r"\b(barrio|sector|vía|via|avenida|calle|carrera|km|kilómetro)\s+([A-ZÁÉÍÓÚa-záéíóú0-9\s]{3,20})\b", texto)
    if match_sector:
        encontrados.append(match_sector.group(0).strip())
        
    if encontrados:
        # Retornar el lugar más específico hallado
        return ", ".join(list(set(encontrados))[:3])
    return "Montería (Sector sin especificar)"

def parsear_fecha_espanol(fecha_str):
    """Convierte cadenas de fecha en español a formato YYYY-MM-DD."""
    if not fecha_str:
        return datetime.now().strftime("%Y-%m-%d")
        
    meses = {
        "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
        "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
        "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
    }
    
    try:
        fecha_lower = fecha_str.lower()
        for mes_nombre, mes_num in meses.items():
            if mes_nombre in fecha_lower:
                match = re.search(r"(\d{1,2})\s+de\s+" + mes_nombre + r"\s+de\s+(\d{4})", fecha_lower)
                if match:
                    dia = match.group(1).zfill(2)
                    anio = match.group(2)
                    return f"{anio}-{mes_num}-{dia}"
    except Exception:
        pass
        
    return datetime.now().strftime("%Y-%m-%d")
