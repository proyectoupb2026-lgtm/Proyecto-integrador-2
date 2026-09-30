import urllib.request
import urllib.error
import base64
import json
import ssl
import os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

codigo_linaje = """
flowchart LR
    %% Origen de Datos
    subgraph Origen [1. Captura en Terreno]
        A[Sensores GPS<br>Ambulancias] --> C
        B[Ingreso Manual<br>Llamada Emergencia] --> C
    end

    %% Ingesta y Limpieza
    subgraph Ingesta [2. Ingesta y Preprocesamiento]
        C(Servidor / API) --> D{Validación de Calidad}
        D -- "Datos Incorrectos" --> E[Tabla de Anomalías<br>Cuarentena]
        D -- "Datos Válidos" --> F[(Base de Datos<br>PostgreSQL/SQLite)]
    end

    %% Transformación Analítica
    subgraph Transformacion [3. Procesamiento Analítico]
        F --> G[Cálculo de Tiempos T_ij<br>con OSMnx]
        G --> H[Motor de Optimización<br>MILP / PuLP]
    end

    %% Consumo Final
    subgraph Consumo [4. Visualización y Uso]
        H --> I[Dashboard Operativo<br>Streamlit]
        I --> J((Centro Regulador:<br>Toma de Decisión))
    end

    %% Estilos
    classDef origin fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef ingest fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef transform fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef consume fill:#f8d7da,stroke:#721c24,stroke-width:2px;
    
    A:::origin; B:::origin;
    C:::ingest; D:::ingest; F:::ingest;
    G:::transform; H:::transform;
    I:::consume; J:::consume;
"""

out_dir = r"C:\Users\Laptop_Lenovo\Documents\GitHub\Proyecto-integrador-2\Entrega corte 2"
os.makedirs(out_dir, exist_ok=True)

payload = {
    "code": codigo_linaje.strip(),
    "mermaid": {"theme": "default"}
}
json_payload = json.dumps(payload).encode('utf-8')
b64_encoded = base64.urlsafe_b64encode(json_payload).decode('utf-8')

url = f"https://mermaid.ink/img/{b64_encoded}?type=png&bgColor=!white"
print("Downloading Linaje_Datos...")

req = urllib.request.Request(
    url, 
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'image/png,*/*;q=0.8'
    }
)

try:
    with urllib.request.urlopen(req, timeout=15, context=ctx) as response:
        with open(os.path.join(out_dir, 'Linaje_Datos.png'), 'wb') as out_file:
            out_file.write(response.read())
    print('Successfully downloaded Linaje_Datos.png')
except Exception as e:
    print(f'Failed to download: {e}')
