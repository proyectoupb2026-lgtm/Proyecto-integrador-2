# Sistema de Web Scraping y Base de Datos de Accidentes de Tránsito (Montería y Córdoba)

> **Proyecto Integrador II:** Sistema Inteligente de Gestión de Atención Prehospitalaria.  
> **Especificación de Referencia:** [promptwebscraping.md](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/web_scraping/promptwebscraping.md)

---

## 1. Resumen de Componentes Creados

| Componente | Archivo | Descripción |
| :--- | :--- | :--- |
| **Inicialización DB** | [init_db.py](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/web_scraping/database/init_db.py) | Inicializa la base de datos SQLite `accidentes_monteria.db` con esquema e índices. |
| **Parsing & NLP** | [parsers.py](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/web_scraping/scrapers/parsers.py) | Algoritmo NLP para extracción de vehículos, fallecidos, heridos y barrios/vías de Montería. |
| **Engine de Scraping** | [news_scraper.py](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/web_scraping/scrapers/news_scraper.py) | Rastreador resiliente con rate limiting (1.5s), rotación de headers y deduplicación Hash SHA-256. |
| **Motor de Consulta** | [consultar_accidentes.py](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/web_scraping/consultar_accidentes.py) | Script CLI para realizar búsquedas avanzadas por lugar, vehículo, fecha y fallecidos. |
| **Pipeline Principal** | [ejecutar_scraping.py](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/web_scraping/ejecutar_scraping.py) | Ejecuta el ciclo completo de scraping, almacenamiento en SQLite y exportación a la carpeta GIS. |

---

## 2. Esquema de la Base de Datos SQLite (`accidentes_monteria.db`)

- `id`: Identificador único (INTEGER PRIMARY KEY)
- `hash_duplicados`: Hash SHA-256 único para evitar duplicados de noticias (TEXT UNIQUE)
- `titulo`: Titular de la noticia de accidente (TEXT)
- `fuente`: Periódico / Portal de origen (El Meridiano, Chica Noticias, El Propio, etc.)
- `url`: Enlace directo a la noticia (TEXT UNIQUE)
- `fecha_publicacion` / `fecha_accidente`: Fecha parseada (DATE YYYY-MM-DD)
- `direccion_lugar`: Ubicación o sector específico del siniestro en Montería/Córdoba (TEXT)
- `vehiculos_involucrados`: Motocicleta, Automóvil, Camión, Bus, Peatón, etc. (TEXT)
- `fallecidos_bool` / `cantidad_fallecidos`: Indicador y conteo de víctimas mortales
- `heridos_bool` / `cantidad_heridos`: Indicador y conteo de lesionados

---

## 3. Instrucciones de Ejecución

### 3.1. Ejecutar Rastreo y Actualización de Noticias
Para rastrear y extraer noticias recientes e históricas de los periódicos locales:
```bash
python web_scraping/ejecutar_scraping.py
```

### 3.2. Realizar Consultas e Informes desde la Línea de Comandos

1. **Buscar accidentes en una avenida o barrio específico de Montería:**
   ```bash
   python web_scraping/consultar_accidentes.py --lugar "Circunvalar"
   ```

2. **Buscar accidentes que involucraron motocicletas con víctimas mortales:**
   ```bash
   python web_scraping/consultar_accidentes.py --vehiculo "Motocicleta" --fallecidos
   ```

3. **Exportar resultados filtrados por rango de fechas a CSV:**
   ```bash
   python web_scraping/consultar_accidentes.py --desde 2021-01-01 --hasta 2026-08-01 --exportar "web_scraping/reporte_accidentes_2021_2026.csv"
   ```

---
*Módulo de Web Scraping e Inteligencia de Datos desarrollado para el Proyecto Integrador II.*
