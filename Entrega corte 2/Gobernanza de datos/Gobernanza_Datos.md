# Marco de Gobernanza de Datos (Estándar DAMA-DMBOK)

Este documento contiene las políticas de gobernanza de la información para el Sistema de Sugerencia de Ubicación de Ambulancias en Montería.

## 1. Catálogo y Diccionario de Datos
Esta tabla define todos los atributos técnicos capturados en la base de datos de accidentes de la ciudad.

| Nombre Técnico | Tipo de Dato | Longitud | Descripción Operativa | Reglas de Integridad / Validación | Fuente de Captura |
|---|---|---|---|---|---|
| `id_accidente` | INT | 11 | Identificador único del siniestro vial. | Llave primaria (PK), autoincremental, NOT NULL. | Generado por sistema. |
| `latitud` | FLOAT | 10,8 | Coordenada geográfica (Y) del incidente. | Rango válido para Montería: [8.70, 8.85]. | Sensores GPS / Ingreso manual. |
| `longitud` | FLOAT | 10,8 | Coordenada geográfica (X) del incidente. | Rango válido para Montería: [-75.95, -75.80]. | Sensores GPS / Ingreso manual. |
| `tipo_accidente`| VARCHAR | 50 | Clasificación del evento (ej. Atropello, Choque). | Debe pertenecer al catálogo maestro de siniestros. | Registro de la autoridad de tránsito. |
| `gravedad` | VARCHAR | 20 | Nivel de daño del incidente (ej. Con Heridos). | Opciones: [Solo Daños, Con Heridos, Con Muertos]. | Reporte paramédico/tránsito. |
| `fallecidos` | INT | 3 | Cantidad de víctimas mortales en el sitio. | Entero positivo o cero (>= 0). Si es > 0, gravedad = 'Con Muertos'. | Confirmación forense/médica. |
| `heridos` | INT | 3 | Cantidad de personas lesionadas. | Entero positivo o cero (>= 0). | Reporte prehospitalario. |
| `fecha` | DATETIME | N/A | Fecha y hora exacta del suceso. | Formato `YYYY-MM-DD HH:MM:SS`. No puede ser fecha futura. | Sello de tiempo automático (Timestamp). |

## 2. Métricas y Políticas de Calidad de Datos
Para asegurar que el modelo MILP reciba información veraz, se monitorean las siguientes dimensiones de calidad:
* **Completitud (% de datos no nulos):** Se exige un 100% de completitud en `latitud`, `longitud` y `fecha`. Si faltan estos datos, el registro es rechazado (aislado en tabla temporal).
* **Exactitud (Tolerancia de error):** La ubicación GPS debe tener una precisión mínima de 15 metros. Coordenadas por fuera del polígono urbano de Montería generan alerta de anomalía.
* **Consistencia (Reglas relacionales):** Si el campo `fallecidos` > 0, el sistema fuerza automáticamente que `gravedad` cambie a "Con Muertos". No puede haber discrepancias lógicas.
* **Oportunidad (Latencia de actualización):** El tiempo máximo permitido desde que el centro regulador captura la llamada hasta que se almacena en la base de datos es de 2 minutos.

## 3. Seguridad, Privacidad y Ciclo de Vida
* **Control de Accesos (RBAC - Role Based Access Control):**
  * *Paramédicos en campo:* Permiso de solo lectura/escritura (INSERT) para nuevos incidentes a través de la app.
  * *Operador / Centro Regulador:* Permiso de ejecución (EXECUTE) para simular ubicaciones y leer KPIs.
  * *Administrador de Datos (Data Steward):* Acceso total (CRUD) para auditoría de tablas.
* **Privacidad y Anonimización:** Por regulaciones de salud (HIPAA/Habeas Data), los datos de las víctimas (nombres, documentos) no se capturan en el modelo geográfico. La tabla de accidentes está anonimizada enfocándose solo en la ubicación y gravedad espacial.
* **Respaldo y Retención:** *Backups* incrementales diarios cada 12 horas. Los datos históricos se conservan 5 años en la base de datos operativa, luego pasan a almacenamiento en frío (Cold Storage) para investigación bibliométrica.
