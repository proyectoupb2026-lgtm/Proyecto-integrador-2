import sqlite3
import pandas as pd
import argparse
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accidentes_monteria.db")

def consultar_accidentes(lugar=None, vehiculo=None, desde=None, hasta=None, solo_fallecidos=False, db_path=DB_PATH):
    """Realiza consultas estructuradas y filtradas en la base de datos de accidentes."""
    if not os.path.exists(db_path):
        print(f"Error: La base de datos {db_path} no existe. Ejecuta primero 'init_db.py' o 'ejecutar_scraping.py'.")
        return None

    conn = sqlite3.connect(db_path)
    query = "SELECT * FROM accidentes WHERE 1=1"
    params = []

    if lugar:
        query += " AND (direccion_lugar LIKE ? OR titulo LIKE ? OR descripcion_contexto LIKE ?)"
        params.extend([f"%{lugar}%", f"%{lugar}%", f"%{lugar}%"])
        
    if vehiculo:
        query += " AND vehiculos_involucrados LIKE ?"
        params.append(f"%{vehiculo}%")
        
    if desde:
        query += " AND fecha_accidente >= ?"
        params.append(desde)
        
    if hasta:
        query += " AND fecha_accidente <= ?"
        params.append(hasta)
        
    if solo_fallecidos:
        query += " AND fallecidos_bool = 1"

    query += " ORDER BY fecha_accidente DESC"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def imprimir_resumen(df):
    """Muestra estadísticas descriptivas de la consulta."""
    if df is None or len(df) == 0:
        print("\n[RESULTADO] No se encontraron accidentes registrados con los criterios de búsqueda especificados.")
        return

    print(f"\n========================================================")
    print(f"   RESULTADOS DE LA CONSULTA ({len(df)} accidentes encontrados)")
    print(f"========================================================")
    
    total_fallecidos = df['cantidad_fallecidos'].sum()
    total_heridos = df['cantidad_heridos'].sum()
    
    print(f"• Total Siniestros Encontrados: {len(df)}")
    print(f"• Total Fallecidos Registrados: {total_fallecidos}")
    print(f"• Total Heridos Registrados:     {total_heridos}")
    print(f"--------------------------------------------------------\n")
    
    for idx, row in df.head(10).iterrows():
        print(f"[{row['id']}] Fecha: {row['fecha_accidente']} | Fuente: {row['fuente']}")
        print(f"    Título:     {row['titulo']}")
        print(f"    Ubicación:  {row['direccion_lugar']}")
        print(f"    Vehículos:  {row['vehiculos_involucrados']}")
        print(f"    Víctimas:   Fallecidos: {row['cantidad_fallecidos']} | Heridos: {row['cantidad_heridos']}")
        print(f"    URL:        {row['url']}")
        print("-" * 60)
        
    if len(df) > 10:
        print(f"... y {len(df) - 10} resultados más. (Usa --exportar para guardarlos en CSV).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta de Consulta de Accidentes en Montería y Córdoba")
    parser.add_argument("--lugar", type=str, help="Filtrar por dirección, barrio o sector (ej. Circunvalar, Mocarí)")
    parser.add_argument("--vehiculo", type=str, help="Filtrar por tipo de vehículo (ej. Motocicleta, Camión)")
    parser.add_argument("--desde", type=str, help="Fecha inicial (YYYY-MM-DD)")
    parser.add_argument("--hasta", type=str, help="Fecha final (YYYY-MM-DD)")
    parser.add_argument("--fallecidos", action="store_true", help="Mostrar solo accidentes con víctimas mortales")
    parser.add_argument("--exportar", type=str, help="Nombre del archivo CSV donde exportar resultados")

    args = parser.parse_args()

    resultados_df = consultar_accidentes(
        lugar=args.lugar,
        vehiculo=args.vehiculo,
        desde=args.desde,
        hasta=args.hasta,
        solo_fallecidos=args.fallecidos
    )

    imprimir_resumen(resultados_df)

    if args.exportar and resultados_df is not None and len(resultados_df) > 0:
        resultados_df.to_csv(args.exportar, index=False, encoding='utf-8-sig')
        print(f"\n✔ Resultados exportados exitosamente a: {args.exportar}")
