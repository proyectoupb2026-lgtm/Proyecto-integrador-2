import urllib.request
import urllib.error
import base64
import json
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

diagramas = {
    "DFD_Nivel_0": """
flowchart TD
    %% Entidades Externas
    E1["Base de Datos de Accidentes (Histórico)"]:::external
    E2["APIs de Mapas y Tráfico (OSMnx/GIS)"]:::external
    E3["Operador / Centro Regulador"]:::external

    %% Sistema Principal
    S1(("Sistema de Sugerencia<br>de Ubicación de<br>Ambulancias")):::system

    %% Flujos de datos
    E1 -- "Registros de accidentes<br>(Latitud, Longitud, Severidad)" --> S1
    E2 -- "Red vial y tiempos<br>de viaje" --> S1
    S1 -- "Sugerencias de puntos<br>estratégicos y KPIs" --> E3
    E3 -- "Parámetros de consulta<br>y restricciones operativas" --> S1

    %% Estilos
    classDef external fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef system fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#000;
""",
    "DFD_Nivel_1": """
flowchart TD
    %% Entidades Externas y Almacenes
    E1["Bases de Datos (CSV/SQLite)"]:::external
    E2["Operador"]:::external
    D1[("Almacén: Datos Espaciales")]:::storage
    D2[("Almacén: Zonas Hot")]:::storage
    D3[("Almacén: Sugerencias")]:::storage

    %% Procesos
    P1(("1.0<br>Recopilar y<br>Limpiar Datos")):::process
    P2(("2.0<br>Identificar<br>Zonas Hot (GIS)")):::process
    P3(("3.0<br>Generar Sugerencias<br>de Ubicación (MILP)")):::process
    P4(("4.0<br>Validar y Simular<br>Tiempos")):::process

    %% Flujos
    E1 -- "Datos crudos de<br>accidentes y red vial" --> P1
    P1 -- "Datos procesados" --> D1
    D1 -- "Coordenadas" --> P2
    P2 -- "Clusters de alta<br>accidentalidad" --> D2
    D2 -- "Demanda focalizada" --> P3
    D1 -- "Tiempos de viaje (T_ij)" --> P3
    E2 -- "Restricciones (Cant. ambulancias)" --> P3
    P3 -- "Coordenadas sugeridas" --> D3
    D3 -- "Ubicaciones" --> P4
    D1 -- "Tiempos de viaje reales" --> P4
    P4 -- "Tiempos de respuesta<br>estimados vs históricos" --> E2

    %% Estilos
    classDef external fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef process fill:#cce5ff,stroke:#004085,stroke-width:2px,color:#000;
    classDef storage fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#000;
""",
    "DFD_Nivel_2": """
flowchart TD
    %% Almacenes de entrada
    D2[("Almacén: Zonas Hot<br>(Demanda)")]:::storage
    D1[("Almacén: Datos Espaciales<br>(Tiempos de viaje T_ij)")]:::storage
    D3[("Almacén: Sugerencias")]:::storage

    %% Procesos Nivel 2
    P31(("3.1<br>Construir Matriz<br>de Tiempos")):::process
    P32(("3.2<br>Formular Modelo<br>Matemático")):::process
    P33(("3.3<br>Ejecutar Solver<br>(PuLP)")):::process
    P34(("3.4<br>Extraer y Formatear<br>Resultados")):::process

    %% Flujos
    D1 -- "Nodos viales" --> P31
    D2 -- "Puntos de demanda" --> P31
    P31 -- "Matriz T_ij" --> P32
    D2 -- "Demanda (d_i)" --> P32
    P32 -- "Restricciones y<br>Función Objetivo" --> P33
    P33 -- "Solución óptima local" --> P34
    P34 -- "Sugerencias de puntos estratégicos" --> D3

    %% Estilos
    classDef process fill:#e2e3e5,stroke:#383d41,stroke-width:2px,color:#000;
    classDef storage fill:#fff3cd,stroke:#856404,stroke-width:2px,color:#000;
"""
}

out_dir = r"C:\Users\Laptop_Lenovo\Documents\GitHub\Proyecto-integrador-2\DFD_de_niveles"
os.makedirs(out_dir, exist_ok=True)

for name, code in diagramas.items():
    payload = {
        "code": code.strip(),
        "mermaid": {"theme": "default"}
    }
    json_payload = json.dumps(payload).encode('utf-8')
    b64_encoded = base64.urlsafe_b64encode(json_payload).decode('utf-8')
    
    url = f"https://mermaid.ink/img/{b64_encoded}?type=png&bgColor=!white"
    print(f"Downloading {name}...")
    
    req = urllib.request.Request(
        url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'image/png,*/*;q=0.8'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
            with open(os.path.join(out_dir, f'{name}.png'), 'wb') as out_file:
                out_file.write(response.read())
        print(f'Successfully downloaded {name}.png')
    except Exception as e:
        print(f'Failed to download {name}.png: {e}')
