# Resumen y Estructura de la Metodología

La propuesta metodológica completa para el desarrollo del proyecto se encuentra estructurada en el documento [Metodologia_Proyecto.md](file:///c:/Users/pc/OneDrive/Desktop/Proyecto%20integrador%202/metodologia/Metodologia_Proyecto.md).

### Resumen del Enfoque:
- **Enfoque:** Cuantitativo, Explicativo-Aplicado, bajo el marco de **Design Science Research (DSR)** e **Investigación de Operaciones Híbrida**.
- **Fase 1 (Diagnóstico):** Caracterización espacial (OSMnx/GIS) y temporal (Procesos de Poisson) de la demanda en Montería.
- **Fase 2 (Optimización Estática PLE):** Modelo matemático MALP/MCLP resuelto en GUROBI/PuLP para ubicar bases óptimas.
- **Fase 3 (Control Dinámico RL):** Algoritmo Deep Q-Network (DQN) / PPO para reubicación preventiva y enrutamiento con tráfico en tiempo real.
- **Fase 4 (Evaluación y Simulación):** Simulación de tráfico en **SUMO** comparando el sistema híbrido vs. políticas tradicionales (FIFO / unidad más cercana).
