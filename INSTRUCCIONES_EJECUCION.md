# Instrucciones de Ejecución - APH Montería

Este proyecto se ha dividido en dos partes principales: un **Backend (API en Python)** que procesa los modelos matemáticos y un **Frontend (Next.js)** que muestra la interfaz visual moderna.

Para que la aplicación funcione correctamente, **ambos servicios deben estar corriendo simultáneamente**.

---

## 1. Ejecutar el Backend (FastAPI - Modelos Matemáticos)

El backend es el encargado de correr el modelo MILP y calcular las asignaciones de las ambulancias. Está escrito en Python y usa FastAPI.

1. Abre una terminal.
2. Navega a la carpeta principal del proyecto:
   ```bash
   cd c:/Users/Laptop_Lenovo/Documents/GitHub/Proyecto-integrador-2
   ```
3. Activa tu entorno virtual (si no lo tienes activado por defecto):
   ```bash
   .\.venv\Scripts\activate
   ```
4. Ejecuta el servidor usando el script de Python:
   ```bash
   python app_ambulancias/api.py
   ```
5. El servidor estará corriendo en **http://localhost:8000**.
   > *Nota: Puedes ver la documentación automática de la API ingresando a http://localhost:8000/docs en tu navegador.*

---

## 2. Ejecutar el Frontend (Next.js - Interfaz de Usuario)

El frontend es la cara visual del proyecto (diseño tipo dashboard, botones, y mapa de Leaflet).

1. Abre **otra ventana** de terminal.
2. Navega a la carpeta del frontend:
   ```bash
   cd c:/Users/Laptop_Lenovo/Documents/GitHub/Proyecto-integrador-2/frontend
   ```
3. Inicia el servidor de desarrollo de Node/Next.js:
   ```bash
   npm run dev
   ```
4. El frontend estará corriendo en **http://localhost:3000**.
5. ¡Abre esa URL en tu navegador (Google Chrome, Edge, etc.) para ver y usar la aplicación!

---

## Solución de Problemas Comunes

- **Error al dar clic en "Ejecutar Modelo":**
  Asegúrate de que la terminal del Backend (FastAPI en el puerto 8000) no esté cerrada ni marcada con algún error. El Frontend necesita comunicarse con él.
  
- **El mapa no carga o sale en gris:**
  Asegúrate de estar conectado a Internet, ya que los recuadros del mapa (Tiles) se descargan de OpenStreetMap en tiempo real.

- **Si necesitas instalar dependencias de nuevo:**
  - Para el backend: `pip install fastapi uvicorn pydantic`
  - Para el frontend (dentro de la carpeta `/frontend`): `npm install`
