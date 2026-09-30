# Documentación UI/UX - Gemelo Digital de Ambulancias

## 1. Visión General de la Interfaz

La aplicación se dividirá en una estructura moderna de "Dashboard de Pantalla Completa", priorizando la visualización del mapa y los datos en tiempo real.

### Estructura Principal (Wireframe Conceptual)

```text
+-----------------------------------------------------------------------------------+
| [Logo] Gemelo Digital APH Montería                 | [KPI: T. Resp Promedio: 8m]  |
+-------------------------+---------------------------------------------------------+
| PARÁMETROS (Sidebar)    | MAPA INTERACTIVO (Principal)                            |
|                         |                                                         |
| [>] Configuración MILP  |  +---------------------------------------------------+  |
| - Nodos Demanda: [4]    |  |                                                   |  |
| - Bases: [4]            |  |             [ MAPA DE MONTERÍA ]                  |  |
| - Ambulancias: [6]      |  |             (Animaciones de rutas en vivo)        |  |
| - T_max (min): [10]     |  |                                                   |  |
|                         |  |  +-- Capas -----+                                 |  |
| [>] Simulación SimPy    |  |  | [x] Red Vial |                                 |  |
| - Días a simular: [30]  |  |  | [x] Heatmap  |                                 |  |
| - Velocidad anim: [1x]  |  |  | [x] Bases    |                                 |  |
|                         |  |  | [x] Ambulan. |                                 |  |
| [ EJECUTAR SIMULACIÓN ] |  |  +--------------+                                 |  |
|                         |  +---------------------------------------------------+  |
|-------------------------|                                                         |
| RESULTADOS & KPIs       |  +---------------------------------------------------+  |
| - Cobertura: 85%        |  | Línea de Tiempo:  |==O==================|         |  |
| - Llamadas: 1204        |  | [ |< ] [ || ] [ > ] [ >| ]  14/05/2026 14:30:00   |  |
| (Gráfico de barras)     |  +---------------------------------------------------+  |
+-------------------------+---------------------------------------------------------+
```

## 2. Diagrama de Flujo de Usuario (BPMN / User Flow)

```mermaid
flowchart TD
    A([Inicio de Sesión / Carga de App]) --> B[Visualizar Mapa Base de Montería]
    B --> C[Configurar Parámetros en Sidebar]
    C --> D{¿Configuración Completa?}
    D -- No --> C
    D -- Sí --> E[Hacer clic en 'Ejecutar Simulación']
    
    E --> F[Backend: Optimización MILP]
    F --> G[Backend: Simulación SimPy]
    G --> H[Backend: Generar Trayectorias (Rutas)]
    
    H --> I[Frontend: Cargar Datos de Simulación]
    I --> J[Animar Mapa y Línea de Tiempo]
    
    J --> K{¿Interacción del Usuario?}
    K -- "Pausa/Reproducir" --> L[Controlar Animación]
    K -- "Cambiar Capas" --> M[Mostrar/Ocultar Heatmap, Nodos]
    K -- "Analizar KPIs" --> N[Revisar Panel de Resultados]
    
    L --> J
    M --> J
    N --> O{¿Nueva Simulación?}
    O -- Sí --> C
    O -- No --> P([Fin del Flujo])
```

## 3. Paleta de Colores y Tipografía
- **Tema:** Modo Oscuro (Dark Mode) por defecto para resaltar los colores del mapa de calor y las rutas brillantes de las ambulancias.
- **Primario:** Azul Médico (`#0ea5e9`) para elementos interactivos.
- **Éxito (Cobertura < T_max):** Verde Esmeralda (`#10b981`).
- **Peligro (Heatmap / Tiempos Excedidos):** Rojo Carmesí (`#ef4444`).
- **Tipografía:** `Inter` o `Roboto` (Sans-serif, moderna, altamente legible para dashboards).

## 4. Tecnologías Elegidas
- **Frontend (UI/UX):** React.js (con Vite), TailwindCSS para estilos, Lucide-React para iconos.
- **Mapas:** `React-Leaflet` para el mapa base y capas estáticas, integrando lógica de animación mediante interpolación de coordenadas a lo largo de las rutas de OSMnx.
- **Estado de Simulación:** Zustand o Context API para manejar la línea de tiempo.
