import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "accidentes_monteria.db")

def init_database(db_path=DB_PATH):
    """Inicializa la base de datos SQLite con el esquema estructurado para accidentes de tránsito."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear Tabla Principal de Accidentes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accidentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash_duplicados TEXT UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        fuente TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        fecha_publicacion DATE,
        fecha_accidente DATE,
        direccion_lugar TEXT NOT NULL,
        vehiculos_involucrados TEXT,
        fallecidos_bool INTEGER DEFAULT 0,
        cantidad_fallecidos INTEGER DEFAULT 0,
        heridos_bool INTEGER DEFAULT 0,
        cantidad_heridos INTEGER DEFAULT 0,
        personas_involucradas TEXT,
        descripcion_contexto TEXT,
        fecha_extraccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Crear Índices de Optimización de Consulta
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_direccion ON accidentes(direccion_lugar);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fecha ON accidentes(fecha_accidente);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehiculos ON accidentes(vehiculos_involucrados);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_fallecidos ON accidentes(fallecidos_bool);")
    
    conn.commit()
    conn.close()
    print(f"Base de datos SQLite inicializada exitosamente en: {db_path}")

if __name__ == "__main__":
    init_database()
