import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
import pandas as pd
import shutil
import os

excel_paths = [
    'Nodos_y_Candidatos_Monteria.xlsx',
    'Nodos_y_Candidatos_Monteria_v2.xlsx'
]

# Leer sitios candidatos existentes del archivo actual
wb_orig = openpyxl.load_workbook('Nodos_y_Candidatos_Monteria.xlsx')
ws_cand = wb_orig['Sitios_Candidatos']
candidatos_data = list(ws_cand.iter_rows(values_only=True))

# 13 Zonas Definitivas con Coordenadas Geocodificadas Formales
zonas_data = [
    ('id_zona', 'barrio_zona', 'sector_general', 'lat', 'lon', 'accidentes_reales_asignados', 'justificacion_validacion'),
    ('ZC_01', 'Glorieta de Mocarí', 'Norte (Acceso Anillo Vial / Mocarí)', 8.800470, -75.855003, 4, 'Validada empíricamente (IDs 9, 56, 87, 94 dentro de radio 1.5 km). Intersección crítica de acceso norte y anillo vial.'),
    ('ZC_02', 'Los Garzones / Vía Cereté', 'Norte Periurbano (Corredor Aeropuerto)', 8.824900, -75.842290, 1, 'Validada empíricamente (ID 89 dentro de radio 1.5 km). Corredor suburbano de alta velocidad hacia el Aeropuerto Los Garzones.'),
    ('ZC_03', 'Universidad de Córdoba (Unicor)', 'Norte (Carrera 6 / Corredor Educativo)', 8.790424, -75.861793, 6, 'Validada empíricamente (IDs 9, 56, 87, 94, 133, 263 en radio 1.5 km). Flujo vehicular masivo de transporte público y motocicletas.'),
    ('ZC_04', 'Avenida Circunvalar / Calle 41', 'Centro Oriente (Arteria Principal / Alamedas)', 8.763296, -75.873706, 4, 'Validada empíricamente (IDs 152, 168, 171, 248 en radio 1.5 km). Eje arterial estructurante con mayor densidad de tráfico comercial.'),
    ('ZC_05', 'Sector Centro (Carreras 2 a 6)', 'Centro Histórico y Administrativo', 8.755898, -75.886984, 5, 'Validada empíricamente (IDs 77, 168, 171, 296, 297 en radio 1.5 km). Cuadrante central de alta densidad peatonal y comercial.'),
    ('ZC_06', 'Glorieta de las Vacas / Terminal', 'Centro Oriente (Anillo Vial / Calle 41)', 8.748558, -75.867643, 3, 'Validada empíricamente (IDs 168, 171, 248 en radio 1.5 km). Nodo crítico de conexión intermunicipal frente a la Terminal de Transportes.'),
    ('ZC_07', 'Cantaclaro', 'Oriente (Sector Residencial y Comercial)', 8.740323, -75.867316, 0, 'Sin mención específica en scraping dentro de 1.5 km. Incluida por conocimiento experto/local debido a su alta densidad poblacional y mototaxismo.'),
    ('ZC_08', 'La Granja (Diagonal 21 / Carrera 24F)', 'Sur Occidente (Núcleo Urbano Sur)', 8.737990, -75.894669, 0, 'Sin siniestros fidedignos en radio estricto de 1.5 km (ID 11 se ubica a 1.55 km en límite Mogambo). Corredor estructurante del suroccidente.'),
    ('ZC_09', 'Mogambo / Calle 4 Sur', 'Sur (Eje Residencial Sur Oriental)', 8.728639, -75.881794, 3, 'Validada empíricamente (IDs 11, 91, 233 en radio 1.5 km). Zona con alta tasa de siniestros graves de motociclistas en el sector sur.'),
    ('ZC_10', 'Rancho Grande (Margen Izquierda)', 'Centro Occidente (Margen Izquierda)', 8.752114, -75.907972, 0, 'Sin mención dentro de 1.5 km (ID 305 en El Dorado a 1.68 km). Incluida por conocimiento experto para garantizar cobertura occidental sobre puentes del Río Sinú.'),
    ('ZC_11', 'Pringamosa / El Dorado', 'Norte Occidente (Margen Izquierda)', 8.764055, -75.899484, 1, 'Validada empíricamente (ID 305 en radio 1.5 km). Cobertura estratégica del cuadrante noroccidental de la margen izquierda.'),
    ('ZC_12', 'Los Pericos / Troncal Oriental', 'Oriente Periurbano (Salida a Planeta Rica)', 8.742540, -75.834670, 0, 'Los siniestros registrados sobre la Troncal (IDs 131 y 231) se ubican a 2.3 km en el tramo suburbano. Incluida como nodo periurbano obligatorio de alta velocidad.'),
    ('ZC_13', 'Loma Grande', 'Sur Oriente Periurbano', 8.694447, -75.841499, 0, 'Corregimiento periurbano oficial de Montería (sede relleno sanitario). Incluida para garantizar cobertura en el eje periurbano suroriental.')
]

# Metodología Actualizada y Unificada
metodologia_data = [
    ('Aspecto Metodológico', 'Detalle Técnico y Justificación'),
    ('1. Delimitación Espacial y Alcance', 'El proyecto se circunscribe estrictamente al municipio de Montería, Córdoba. De los 338 registros consolidados por web scraping de portales de noticias locales, exactamente 293 corresponden al municipio de Montería. Se excluyeron los 45 registros de otros municipios de Córdoba (Cereté: 22, Montelíbano: 6, Chinú: 3, Ciénaga de Oro: 2, etc.) para mantener absoluta coherencia territorial con el modelo de respuesta de emergencias de Montería.'),
    ('2. Definición Híbrida de Zonas de Demanda (Conjunto I)', 'Las zonas de demanda no se derivaron exclusivamente de un algoritmo de agrupamiento no supervisado, debido a las limitaciones intrínsecas de georreferenciación de las noticias. Se adoptó un enfoque híbrido: definición de 13 nodos de demanda mediante conocimiento experto/local de la morfología vial y urbana de Montería, geocodificadas formalmente mediante Nominatim (OpenStreetMap) y ArcGIS, y validadas con point-in-polygon contra el límite municipal oficial de Montería (OSM relación 1343449).'),
    ('3. Auditoría de Datos de Siniestralidad y Cifras Oficiales', 'En los 293 registros de Montería: el 92.15% (270 eventos) presenta únicamente mención general de la ciudad, habiéndoseles asignado la coordenada centroide municipal (8.7508, -75.8814). Solo 23 eventos (7.85%) cuentan con georreferenciación fidedigna de alta precisión a nivel de dirección, barrio o hito verificable.'),
    ('4. Criterio de No Contaminación Espacial', 'Los 270 registros con precisión centroidal no se asignaron a ninguna zona caliente ni se dispersaron artificialmente al azar. Asignar puntos genéricos a una zona específica introduciría un sesgo espurio de densidad. Dichos registros se conservan únicamente como estimador agregado del volumen global de incidentes de la ciudad para el parámetro lambda del proceso estocástico de Poisson en la simulación temporal SimPy.'),
    ('5. Validación Empírica con Siniestros Precisos', 'Sobre los 23 accidentes fidedignos de Montería, se calcularon las distancias geodésicas (fórmula de Haversine) a cada zona: 20 de ellos se localizan dentro del área de influencia urbana (radio de 1.5 km), mientras que los 3 restantes corresponden a vías rurales dispersas del municipio (ID 160 Mateo Gómez, ID 163 Leticia, ID 245 Vía Planeta Rica). Las zonas con conteo empírico cero se mantuvieron en cero con debida justificación cualitativa, garantizando que el modelo MILP las reconozca como nodos de cobertura obligatoria por su relevancia urbana real y poblacional.'),
    ('6. Resolución de Discrepancias Previas (Unificación 293 y 23)', 'Se corrigió el error de versiones preliminares donde se sumaban erróneamente los 270 centroides de Montería con los 24 eventos de precisión alta de todo el departamento de Córdoba (270 + 24 = 294), originado porque el registro ID 21 pertenecía a Tierralta. El conteo oficial, unificado y verificado es: 293 accidentes en Montería = 270 centroidales genéricos + 23 fidedignos verificados.')
]

def format_excel(wb):
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    border_thin = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        ws.views.sheetView[0].showGridLines = True
        
        # Formato encabezado
        for col_num in range(1, ws.max_column + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            
        # Formato filas de datos
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                cell.border = border_thin
                cell.font = Font(name="Calibri", size=10)
                if isinstance(cell.value, float):
                    if 'lat' in str(ws.cell(row=1, column=cell.column).value).lower() or 'lon' in str(ws.cell(row=1, column=cell.column).value).lower():
                        cell.number_format = '0.000000'
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                elif isinstance(cell.value, int):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(vertical="center", wrap_text=True)
                    
        # Ancho automático de columnas
        for col in ws.columns:
            max_len = 0
            col_letter = col[0].column_letter
            for cell in col:
                val = str(cell.value or '')
                if len(val) > max_len:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 60)

for path in excel_paths:
    wb = openpyxl.Workbook()
    # 1. Sitios Candidatos
    ws1 = wb.active
    ws1.title = 'Sitios_Candidatos'
    for r in candidatos_data:
        ws1.append(r)
        
    # 2. Zonas Calientes Demanda
    ws2 = wb.create_sheet(title='Zonas_Calientes_Demanda')
    for r in zonas_data:
        ws2.append(r)
        
    # 3. Metodología Zonas
    ws3 = wb.create_sheet(title='Metodologia_Zonas')
    for r in metodologia_data:
        ws3.append(r)
        
    format_excel(wb)
    wb.save(path)
    print(f"Archivo Excel '{path}' guardado y formateado con éxito.")
