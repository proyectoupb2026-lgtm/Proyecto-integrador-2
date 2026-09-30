```python
# Algoritmo de Web Scraping - Noticias de Accidentes de Tránsito Montería, Córdoba

Necesito que desarrolles un algoritmo de web scraping que:

## Objetivo Principal
Extraer noticias de accidentes de tránsito ocurridos en Montería y el departamento de Córdoba durante los últimos 5 años, estructurar los datos en una base de datos y hacerlos consultables.

## Fuentes a Rastrear
- El Meridiano (periódico local de Córdoba)
- El Propio (periódico local)
- Chica Noticias
- Portales de noticias locales y regionales de Córdoba
- Cualquier otra fuente de noticias local o regional relevante que encuentres

## Datos Críticos a Extraer
Para cada noticia de accidente, extrae:
- **Tipo de vehículo(s) involucrado(s)** (automóvil, moto, camión, bus, etc.)
- **Personas involucradas** (cantidad, nombres si están disponibles)
- **Dirección/Sitio del siniestro** (esta es la prioridad máxima — debe ser lo más específica posible)
- **Fallecidos** (sí/no, cantidad si aplica)
- **Fecha del accidente**
- **Descripción del accidente** (contexto general)

## Especificaciones Técnicas
- Alcance temporal: Mínimo 5 años hacia atrás desde la fecha actual
- Almacenamiento: Base de datos estructurada (SQL o NoSQL, según sea apropiado) con campos claramente definidos para cada dato extraído
- Manejo de duplicados: Implementa lógica para detectar y evitar duplicar registros de un mismo accidente
- Resiliencia: El scraper debe manejar cambios en la estructura HTML de los sitios y errores de conexión

## Requisitos del Código
- Implementa rate limiting para no sobrecargar los servidores (respetar robots.txt)
- Incluye manejo de errores robusto y logging
- Proporciona un script para inicializar la base de datos con el esquema correcto
- Genera un script de consulta que permita buscar accidentes por dirección, tipo de vehículo, rango de fechas, etc.

Entregar:
1. Código del scraper completo
2. Esquema y script de inicialización de la base de datos
3. Script de ejemplo para consultar la base de datos
4. Instrucciones claras para ejecutar el proyecto
```