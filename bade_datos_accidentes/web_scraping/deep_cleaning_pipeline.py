import os
import sys
import sqlite3
import pandas as pd
import json
import re

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_RIGUROSO = os.path.join(BASE_DIR, "accidentes_extraidos_riguroso.csv")
CSV_ESTANDAR = os.path.join(BASE_DIR, "accidentes_extraidos.csv")
DB_PATH = os.path.join(BASE_DIR, "accidentes_monteria.db")

OUT_CSV = os.path.join(BASE_DIR, "accidentes_limpios_deep_cleaned.csv")
OUT_JSON = os.path.join(BASE_DIR, "accidentes_limpios_deep_cleaned.json")
OUT_MD = os.path.join(BASE_DIR, "catalogo_verificacion_accidentes.md")

def fix_utf8_double(val):
    if not isinstance(val, str) or pd.isna(val):
        return ""
    try:
        fixed = val.encode('latin-1').decode('utf-8')
    except Exception:
        fixed = val
        
    # Limpieza de espacios múltiples y guiones no estándar
    fixed = fixed.replace('', '').replace('\ufeff', '')
    fixed = re.sub(r'\s+', ' ', fixed).strip()
    return fixed

def deep_clean_pipeline():
    print("==========================================================")
    print(" DEEP CLEANING PIPELINE DE ACCIDENTES DE TRÁNSITO ")
    print("==========================================================")
    
    # 1. Cargar dataset en latin-1 para revertir doble codificación UTF-8
    df = pd.read_csv(CSV_RIGUROSO, encoding='latin-1')
    df.columns = [c.replace('\ufeff', '').replace('ï»¿', '').strip() for c in df.columns]
    print(f"Cargados {len(df)} registros desde {CSV_RIGUROSO}")

    
    # 2. Reparar todas las columnas de texto
    for col in df.select_dtypes(include=['object', 'string']).columns:
        df[col] = df[col].apply(fix_utf8_double)
        
    # 3. Tratar columnas numéricas y nulas
    df['cantidad_fallecidos'] = df['cantidad_fallecidos'].fillna(0).astype(int)
    df['cantidad_heridos'] = df['cantidad_heridos'].fillna(0).astype(int)
    df['fallecidos_bool'] = df['fallecidos_bool'].fillna(0).astype(int)
    df['heridos_bool'] = df['heridos_bool'].fillna(0).astype(int)
    
    # Eliminar columna nula 100% vacía
    if 'personas_involucradas' in df.columns:
        df = df.drop(columns=['personas_involucradas'])
        
    # 4. Clasificar estado de precisión y verificación de dirección
    def clasificar_estado(row):
        d_esp = str(row.get('direccion_especifica', '')).strip()
        d_lug = str(row.get('direccion_lugar', '')).strip()
        prec = str(row.get('precision_geo', '')).strip()
        
        genericos = ['Casco Urbano', 'Sector en investigación', 'Municipio de', 'General Montería', 'Desconocido']
        es_generica = any(g in d_esp or g in d_lug for g in genericos) or prec.startswith('Baja')
        
        # Verificar si posee hito o dirección específica real
        tiene_especifica = any(k in d_esp for k in ['Barrio', 'Calle', 'Carrera', 'Avenida', 'Glorieta', 'km', 'Vía', 'Troncal', 'Sector/Barrio']) and not ('Casco Urbano' in d_esp)
        
        if es_generica and not tiene_especifica:
            return '🟡 Pendiente (Verificar Noticia)'
        return '🟢 Verificada / Específica'

    df['estado_verificacion'] = df.apply(clasificar_estado, axis=1)
    
    # 5. Generar celda de enlace interactivo para el usuario
    df['link_noticia_html'] = df['url'].apply(lambda u: f'<a href="{u}" target="_blank" class="btn-link">🔗 Abrir Noticia</a>' if u and str(u).startswith('http') else 'Sin enlace')
    df['link_noticia_md'] = df['url'].apply(lambda u: f'[🔗 Abrir Noticia]({u})' if u and str(u).startswith('http') else 'Sin enlace')

    # Ordenar columnas lógicamente
    cols_order = [
        'id', 'estado_verificacion', 'fecha_accidente', 'fecha_publicacion', 'fuente',
        'titulo', 'direccion_lugar', 'direccion_especifica', 'barrio_sector', 'municipio',
        'vehiculos_involucrados', 'cantidad_fallecidos', 'cantidad_heridos',
        'precision_geo', 'latitud', 'longitud', 'url', 'link_noticia_html', 'link_noticia_md',
        'descripcion_contexto', 'hash_duplicados', 'fecha_extraccion'
    ]
    
    cols_exist = [c for c in cols_order if c in df.columns]
    df = df[cols_exist]
    
    # Exportar CSV Limpio
    df.to_csv(OUT_CSV, index=False, encoding='utf-8-sig')
    print(f"[OK] CSV Limpio exportado a: {OUT_CSV}")
    
    # Exportar JSON para Web App
    json_data = df.to_dict(orient='records')
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] JSON exportado para Web Dashboard a: {OUT_JSON}")
    
    # Exportar JS para la carga directa local en navegador (file://)
    OUT_JS = os.path.join(BASE_DIR, "accidentes_data.js")
    with open(OUT_JS, 'w', encoding='utf-8') as f:
        f.write("window.ACCIDENTES_DATA = " + json.dumps(json_data, ensure_ascii=False, indent=2) + ";")
    print(f"[OK] JS para Visor Web exportado a: {OUT_JS}")

    
    # Actualizar SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('accidentes_limpios', conn, if_exists='replace', index=False)
        conn.close()
        print(f"[OK] Tabla 'accidentes_limpios' actualizada en SQLite: {DB_PATH}")
    except Exception as e:
        print(f"[AVISO] Error al actualizar SQLite: {e}")
        
    # Generar Catálogo Markdown
    generar_catalogo_markdown(df)
    
    print("\n--- RESUMEN DE LIMPIEZA PROFUNDA ---")
    print(f"Total registros: {len(df)}")
    print(df['estado_verificacion'].value_counts())

def generar_catalogo_markdown(df):
    verificados = df[df['estado_verificacion'] == '🟢 Verificada / Específica']
    pendientes = df[df['estado_verificacion'] == '🟡 Pendiente (Verificar Noticia)']
    
    md_content = f"""# Catálogo de Verificación de Direcciones de Accidentes de Tránsito
> **Proyecto Integrador II** | Base de Datos Procesada y Limpia  
> **Total de Registros:** {len(df)} | **Direcciones Verificadas:** {len(verificados)} | **Pendientes de Verificación Manual:** {len(pendientes)}

---

## 🟢 1. Registros con Dirección Específica Verificada ({len(verificados)})

Estos registros contienen detalles precisos de la ubicación (barrios, calles, avenidas o hitos).

| ID | Fecha | Periódico | Titular / Noticia | Dirección Registrada | Enlace Directo |
|---|---|---|---|---|---|
"""
    for _, r in verificados.iterrows():
        md_content += f"| `{r['id']}` | {r['fecha_accidente']} | {r['fuente']} | {str(r['titulo'])[:60]}... | **{r['direccion_especifica']}** | {r['link_noticia_md']} |\n"
        
    md_content += f"""

---

## 🟡 2. Registros Pendientes de Verificación Manual ({len(pendientes)})

Estos registros actualmente tienen direcciones genéricas (ej: casco urbano o nivel municipal). **Usa el enlace directo para leer la noticia original e ingresar la dirección específica.**

| ID | Fecha | Periódico | Titular Noticia | Dirección Actual | Verificación Manual |
|---|---|---|---|---|---|
"""
    for _, r in pendientes.iterrows():
        md_content += f"| `{r['id']}` | {r['fecha_accidente']} | {r['fuente']} | {str(r['titulo'])[:65]}... | `{r['direccion_lugar']}` | {r['link_noticia_md']} |\n"

    with open(OUT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"[OK] Catálogo Markdown creado en: {OUT_MD}")

if __name__ == "__main__":
    deep_clean_pipeline()
