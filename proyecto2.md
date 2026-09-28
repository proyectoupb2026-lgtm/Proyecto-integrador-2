# Clarificación y Enfoque del Proyecto

## 1. Jerarquía clara
- **Objetivo central**: Disminuir los tiempos de respuesta prehospitalaria en Montería ante accidentes vehiculares.
- **Medios para lograrlo**: 
  1. Análisis de zonas hot de accidentalidad vehicular.
  2. Sugerir puntos estratégicos de ubicación de ambulancias basados en dicho análisis.
- **Cualquier mención a evaluación de la calidad de atención** debe quedar como un **aspecto secundario** y solo incluirse si directamente alimenta la reducción de tiempos.

## 2. Rigidez conceptual
- El proyecto **sugiere** (no optimiza) ubicaciones estratégicas; la palabra *optimizar* implica búsqueda de la solución “máxima”, lo cual está fuera del alcance definido y ha sido rechazada por el docente.
- El modelo matemático es **una herramienta** para generar esas sugerencias, no para demostrar la “mejor” solución absoluta.
- El enfoque debe limitarse estrictamente a: *análisis de accidentalidad → sugerencia de ubicaciones → reducción de tiempos*.

## 3. Confusiones a eliminar
| Frase encontrada | Por qué confunde el enfoque | Reencuadre / Eliminación |
|------------------|----------------------------|--------------------------|
| “Evaluar la calidad de atención” | Introduce un objetivo de desempeño que no está ligado directamente a la reducción de tiempos. | Eliminar o relegar a sección de **perspectivas futuras**. |
| “Optimizar recursos” | La palabra *optimizar* sugiere una búsqueda global de la mejor solución, lo cual excede la meta de “sugerir” ubicaciones. | Reemplazar por “sugerir ubicaciones estratégicas basadas en análisis”. |
| “Mejorar aspectos amplios del servicio” | Amplía el alcance a áreas no contempladas (ej. gestión de personal, equipamiento). | Limitar la descripción a la **ubicación de ambulancias** y su vínculo con el tiempo de respuesta. |

## 4. Propuesta reformulada
### Problema específico
Los tiempos de respuesta actuales en Montería frente a accidentes vehiculares son elevados, lo que incrementa la mortalidad y la gravedad de los traumas.

### Objetivo principal
Disminuir dichos tiempos de respuesta mediante la **sugerencia** de puntos estratégicos de ubicación de ambulancias, basándose en el análisis de zonas hot de accidentalidad.

### Método
1. **Recolección y análisis de datos** de accidentalidad vehicular (historiales, noticias, bases de datos). 
2. **Identificación de zonas hot** mediante técnicas de GIS y análisis espacial.
3. **Aplicación de un modelo de Programación Lineal Entera Mixta (MILP)** para generar sugerencias de ubicaciones que cubran eficientemente las zonas identificadas.
4. **Validación** comparando los tiempos de respuesta simulados con los históricos.

### Qué NO forma parte del proyecto
- Evaluación integral de la calidad de atención médica.
- Optimización global de recursos del sistema de salud.
- Mejora de procesos operacionales ajenos a la ubicación de ambulancias.

> **Nota**: Mantener esta delimitación durante la redacción garantizará claridad conceptual y evitará desviaciones del objetivo central.
