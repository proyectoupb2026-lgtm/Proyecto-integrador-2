# 04 — Flujo de Procesos BPMN

## Comparación AS-IS vs TO-BE

### Estado Actual (AS-IS): Despacho Reactivo Estático

```mermaid
flowchart TD
    A([🚨 Ocurre Accidente Vial]) --> B[Ciudadano llama 123]
    B --> C[Operador recibe llamada]
    C --> D{¿Ambulancia disponible\ncerca?}
    D -- Sí --> E[Despacha unidad\nmás cercana disponible]
    D -- No --> F[Espera hasta\nliberar unidad]
    F --> E
    E --> G[Ambulancia viaja\nsin ruta optimizada]
    G --> H{¿Tiempo de llegada\n≤ 10 min?}
    H -- No --> I[❌ Tiempo excedido\nPaciente en riesgo]
    H -- Sí --> J[✅ Atención oportuna]
    I --> K([Fin del incidente])
    J --> K

    style I fill:#ff6b6b,color:#fff
    style J fill:#51cf66,color:#fff
    style A fill:#ff922b,color:#fff
```

---

### Estado Propuesto (TO-BE): Despacho Inteligente con Gemelo Digital

```mermaid
flowchart TD
    subgraph PRE["🔁 Pre-despacho (Optimización Proactiva)"]
        P1[Cargar CSV de accidentes históricos]
        P2[Calcular centros de cluster KMeans]
        P3[Construir matriz T_ij de tiempos]
        P4[Resolver MILP → Asignación óptima X_jk]
        P5[Pre-posicionar ambulancias en bases óptimas]
        P1 --> P2 --> P3 --> P4 --> P5
    end

    subgraph OP["⚡ Operación en Tiempo Real (SimPy)"]
        O1([🚨 Evento: Accidente generado\npor proceso Poisson])
        O2[Consultar estado de flota]
        O3{¿Base óptima\ndisponible?}
        O4[Despachar ambulancia\nmás cercana disponible]
        O5[Cola de espera\nen base más cercana]
        O6[Ambulancia en ruta]
        O7[Registrar tiempo de respuesta]
        O8[Atender y regresar a base]
        O1 --> O2 --> O3
        O3 -- Sí --> O4
        O3 -- No --> O5 --> O4
        O4 --> O6 --> O7 --> O8
        O8 -->|"Ambulancia libre"| O2
    end

    subgraph KPI["📊 Análisis de Resultados"]
        K1[Calcular T_resp promedio]
        K2[Calcular % cobertura ≤ T_max]
        K3[Actualizar mapa y KPIs]
        K4{¿Resultados\nsatisfactorios?}
        K5[Ajustar parámetros\ny re-ejecutar]
        K6([✅ Configuración aprobada])
        K1 --> K2 --> K3 --> K4
        K4 -- No --> K5 --> P4
        K4 -- Sí --> K6
    end

    P5 --> O1
    O7 --> K1

    style PRE fill:#e3f2fd
    style OP fill:#fff3e0
    style KPI fill:#e8f5e9
```

---

## Diagrama de Secuencia: Ciclo de Vida de un Incidente

```mermaid
sequenceDiagram
    participant U as 👤 Operador
    participant UI as 🖥️ Interfaz PyQt5
    participant W as ⚙️ SimWorker (QThread)
    participant M as 📐 MILP Solver
    participant S as ⏱️ SimPy Engine
    participant G as 🗺️ Folium Map

    U->>UI: Ingresa parámetros (p, T_max, α)
    U->>UI: Clic "Ejecutar Simulación"
    UI->>UI: Valida inputs
    UI->>W: Inicia hilo con parámetros
    UI-->>U: Muestra barra de progreso

    W->>M: solve_milp(n, bases, p, T_max, ...)
    M->>M: Construye variables x, y, z, v
    M->>M: PuLP CBC solver → encuentra x*_jk
    M-->>W: allocation = {j: count}

    W->>G: generar_mapa(allocation, num_bases)
    G->>G: Carga CSV accidentes → HeatMap
    G->>G: Carga GeoJSON red vial
    G->>G: Pinta bases y ambulancias óptimas
    G-->>W: temp_map.html guardado

    W->>S: run_simulation(allocation, t_ij, demands)
    loop Cada incidente generado (Poisson)
        S->>S: Genera evento en nodo i
        S->>S: Busca base más cercana disponible
        S->>S: Despacha ambulancia (viaje + atención)
        S->>S: Registra T_resp
    end
    S-->>W: Lista de tiempos de respuesta

    W-->>UI: emit finished(results)
    UI->>UI: Actualiza labels KPI
    UI->>UI: browser.setUrl(temp_map.html)
    UI-->>U: Muestra resultados y mapa actualizado
```
