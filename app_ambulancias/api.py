import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import random

# Configurar path e importar módulos sin problemas de caché
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

try:
    from utils.data_loader import calculate_clusters, generate_t_ij, load_candidatos, load_zonas_demanda
    from models.milp import solve_milp
except ImportError:
    from app_ambulancias.utils.data_loader import calculate_clusters, generate_t_ij, load_candidatos, load_zonas_demanda
    from app_ambulancias.models.milp import solve_milp

app = FastAPI(title="APH Montería API")

# Habilitar CORS para que el frontend Next.js pueda hacer peticiones
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se debe restringir al dominio de Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OptimizeRequest(BaseModel):
    num_ambulances: int
    num_nodes: int = 0
    num_bases: int = 0
    t_max: float = 10.0
    alpha: float = 0.5
    strategy: str = "todas"  # "todas" (Hospitales + Puntos de Espera Táctica en Ciudad) o "hospitales"

@app.get("/")
def read_root():
    return {"message": "API Backend de APH Montería en línea"}

@app.post("/api/optimize")
async def optimize_fleet(req: OptimizeRequest):
    try:
        # Cargar datos reales del Excel
        df_bases = load_candidatos()
        df_nodos = load_zonas_demanda()
        
        if df_bases.empty or df_nodos.empty:
            raise Exception("No se encontraron los datos en el Excel Nodos_y_Candidatos_Monteria.xlsx")
            
        # Filtrar por estrategia seleccionada
        if req.strategy == "hospitales":
            df_bases = df_bases[df_bases['tipo'].astype(str).str.contains('Hospital|Clínica', case=False, na=False)]
        elif req.num_bases > 0:
            df_bases = df_bases.iloc[:req.num_bases]

        base_coords = df_bases[['lat', 'lon']].values.tolist()
        base_names = df_bases['nombre'].tolist()
        base_types = df_bases['tipo'].tolist() if 'tipo' in df_bases.columns else ['Hospital/Clínica'] * len(df_bases)
        
        n_nodos = req.num_nodes if req.num_nodes and req.num_nodes > 0 else len(df_nodos)
        node_coords = df_nodos[['lat', 'lon']].values.tolist()[:n_nodos]
        node_names = df_nodos['barrio_zona'].tolist()[:n_nodos]

        t_ij = generate_t_ij(node_coords, base_coords)
        
        # Demanda ponderada y capacidad por base
        demands = [random.randint(15, 60) for _ in range(len(node_coords))]
        capacities = [max(2, (req.num_ambulances // max(1, len(base_coords))) + 2) for _ in range(len(base_coords))]
        
        # Ejecutar MILP (El modelo matemático)
        opt_res = solve_milp(len(node_coords), len(base_coords), req.num_ambulances, req.t_max, req.alpha, demands, capacities, t_ij)
        
        if "error" in opt_res:
            raise HTTPException(status_code=400, detail=opt_res["error"])
            
        return {
            "status": "success",
            "allocation": opt_res["allocation"],
            "coverage": opt_res.get("coverage", 0),
            "avg_time": opt_res.get("avg_time", 0),
            "base_coords": base_coords,
            "base_names": base_names,
            "base_types": base_types,
            "node_coords": node_coords,
            "node_names": node_names
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    speed_kmh: float = 30.0
    traffic_factor: float = 1.0

@app.post("/api/route")
async def get_route(req: RouteRequest):
    try:
        try:
            from utils.route_calculator import calculate_routes_with_alternatives
        except ImportError:
            from app_ambulancias.utils.route_calculator import calculate_routes_with_alternatives
        res = calculate_routes_with_alternatives(
            req.start_lat, req.start_lon, req.end_lat, req.end_lon, 
            speed_kmh=req.speed_kmh, traffic_factor=req.traffic_factor
        )
        return {
            "status": "success",
            "primary_route": res["primary_route"],
            "alternative_routes": res["alternative_routes"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SnapRequest(BaseModel):
    lat: float
    lon: float

class ZoneData(BaseModel):
    id: str | None = None
    name: str
    lat: float
    lon: float

class SaveZonesRequest(BaseModel):
    zones: list[ZoneData]

import pandas as pd
from datetime import datetime
import subprocess

gdf_roads = None

def load_road_network():
    global gdf_roads
    if gdf_roads is None:
        try:
            import geopandas as gpd
            path = os.path.join(APP_DIR, "..", "mapa_GIS_Monteria", "monteria_road_network.geojson")
            if os.path.exists(path):
                gdf_roads = gpd.read_file(path)
                gdf_roads = gdf_roads.to_crs(epsg=32618)
        except Exception:
            pass

@app.get("/api/zonas")
def get_zonas():
    try:
        df_nodos = load_zonas_demanda()
        ids = df_nodos['id_zona'].tolist() if 'id_zona' in df_nodos.columns else [f"ZC_{i+1:02d}" for i in range(len(df_nodos))]
        return {
            "status": "success",
            "node_ids": ids,
            "node_coords": df_nodos[['lat', 'lon']].values.tolist(),
            "node_names": df_nodos['barrio_zona'].tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/snap")
async def snap_location(req: SnapRequest):
    load_road_network()
    
    # Intento 1: buscar si es una glorieta vía Overpass
    import requests
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    way(around:50, {req.lat}, {req.lon})["junction"="roundabout"];
    out center;
    """
    try:
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=4)
        if response.status_code == 200:
            data = response.json()
            if data['elements']:
                element = data['elements'][0]
                if 'center' in element:
                    return {
                        "status": "success",
                        "lat": element['center']['lat'],
                        "lon": element['center']['lon'],
                        "street": element.get('tags', {}).get('name', 'Glorieta')
                    }
    except Exception:
        pass
        
    # Intento 2: Snap al GeoJSON local
    global gdf_roads
    if gdf_roads is not None and not gdf_roads.empty:
        import geopandas as gpd
        from shapely.geometry import Point
        pt = gpd.GeoSeries([Point(req.lon, req.lat)], crs="EPSG:4326").to_crs(epsg=32618).iloc[0]
        distances = gdf_roads.distance(pt)
        nearest_idx = distances.idxmin()
        nearest_geom = gdf_roads.loc[nearest_idx].geometry
        nearest_pt_projected = nearest_geom.interpolate(nearest_geom.project(pt))
        
        nearest_pt_ll = gpd.GeoSeries([nearest_pt_projected], crs="EPSG:32618").to_crs(epsg=4326).iloc[0]
        
        street_name = gdf_roads.loc[nearest_idx].get('name', 'Vía sin nombre')
        if not isinstance(street_name, str):
            street_name = 'Vía sin nombre'
            
        return {
            "status": "success",
            "lat": nearest_pt_ll.y,
            "lon": nearest_pt_ll.x,
            "street": street_name
        }
    
    return {"status": "success", "lat": req.lat, "lon": req.lon, "street": "Vía desconocida"}

@app.post("/api/zonas/save")
async def save_zonas(req: SaveZonesRequest):
    try:
        excel_path = os.path.join(APP_DIR, "..", "Nodos_y_Candidatos_Monteria.xlsx")
        df_all = pd.read_excel(excel_path, sheet_name=None)
        df_zonas = df_all['Zonas_Calientes_Demanda']
        
        log_entries = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Registrar zonas eliminadas
        req_ids = {z.id for z in req.zones if z.id}
        if 'id_zona' in df_zonas.columns:
            for _, row in df_zonas.iterrows():
                if row['id_zona'] not in req_ids:
                    log_entries.append({
                        "zona": str(row['barrio_zona']),
                        "coordenada_anterior": f"{row['lat']},{row['lon']}",
                        "coordenada_nueva": "ELIMINADA",
                        "metros_desplazados": 0.0,
                        "metodo": "eliminación manual de zona",
                        "fecha": now_str
                    })
        
        # 2. Construir la nueva lista de zonas
        new_rows = []
        for i, z in enumerate(req.zones):
            zid = z.id if z.id else f"ZC_{i+1:02d}"
            existing = pd.DataFrame()
            if 'id_zona' in df_zonas.columns and zid in df_zonas['id_zona'].values:
                existing = df_zonas[df_zonas['id_zona'] == zid]
            elif 'barrio_zona' in df_zonas.columns and z.name in df_zonas['barrio_zona'].values:
                existing = df_zonas[df_zonas['barrio_zona'] == z.name]
                
            if not existing.empty:
                old_row = existing.iloc[0]
                old_lat = float(old_row['lat'])
                old_lon = float(old_row['lon'])
                old_name = str(old_row['barrio_zona'])
                
                # Chequear cambio de nombre
                if old_name != z.name:
                    log_entries.append({
                        "zona": f"{old_name} -> {z.name}",
                        "coordenada_anterior": f"{old_lat},{old_lon}",
                        "coordenada_nueva": f"{z.lat},{z.lon}",
                        "metros_desplazados": 0.0,
                        "metodo": "cambio de nombre de zona",
                        "fecha": now_str
                    })
                    
                # Chequear desplazamiento
                dist_m = ((old_lat - z.lat)**2 + (old_lon - z.lon)**2)**0.5 * 111000
                if dist_m > 0.5:
                    log_entries.append({
                        "zona": z.name,
                        "coordenada_anterior": f"{old_lat},{old_lon}",
                        "coordenada_nueva": f"{z.lat},{z.lon}",
                        "metros_desplazados": round(dist_m, 2),
                        "metodo": "verificación manual sobre mapa",
                        "fecha": now_str
                    })
                
                row_dict = old_row.to_dict()
                row_dict['id_zona'] = zid
                row_dict['barrio_zona'] = z.name
                row_dict['lat'] = z.lat
                row_dict['lon'] = z.lon
                new_rows.append(row_dict)
            else:
                # Nueva zona agregada
                log_entries.append({
                    "zona": z.name,
                    "coordenada_anterior": "NUEVA",
                    "coordenada_nueva": f"{z.lat},{z.lon}",
                    "metros_desplazados": 0.0,
                    "metodo": "incorporación nueva zona",
                    "fecha": now_str
                })
                new_rows.append({
                    'id_zona': zid,
                    'barrio_zona': z.name,
                    'sector_general': 'Sector Urbano',
                    'lat': z.lat,
                    'lon': z.lon,
                    'accidentes_reales_asignados': 0,
                    'justificacion_validacion': 'Agregada manualmente'
                })
                
        df_new_zonas = pd.DataFrame(new_rows)
        df_all['Zonas_Calientes_Demanda'] = df_new_zonas
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet, df_sheet in df_all.items():
                df_sheet.to_excel(writer, sheet_name=sheet, index=False)
                
        if log_entries:
            log_df = pd.DataFrame(log_entries)
            log_path = os.path.join(APP_DIR, "..", "calibracion_bitacora.csv")
            if os.path.exists(log_path):
                log_df.to_csv(log_path, mode='a', header=False, index=False)
            else:
                log_df.to_csv(log_path, index=False)
                
        script_path = os.path.join(APP_DIR, "..", "mapa_GIS_Monteria", "recalcular_asignaciones_definitivas.py")
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path], check=False)
            
        return {"status": "success", "total_zonas": len(df_new_zonas)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bases")
def get_bases():
    try:
        df_bases = load_candidatos()
        return {
            "status": "success",
            "base_names": df_bases['nombre'].tolist(),
            "base_types": df_bases['tipo'].tolist(),
            "base_coords": df_bases[['lat', 'lon']].values.tolist(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class BaseItemData(BaseModel):
    name: str
    lat: float
    lon: float
    tipo: str = "Punto Táctico"

class SaveBasesRequest(BaseModel):
    bases: list[BaseItemData]

@app.post("/api/bases/save")
async def save_bases(req: SaveBasesRequest):
    try:
        excel_path = os.path.join(APP_DIR, "..", "Nodos_y_Candidatos_Monteria.xlsx")
        df_all = pd.read_excel(excel_path, sheet_name=None)
        df_bases = df_all['Sitios_Candidatos']
        
        for b in req.bases:
            mask = df_bases['nombre'] == b.name
            if mask.any():
                df_bases.loc[mask, 'lat'] = b.lat
                df_bases.loc[mask, 'lon'] = b.lon
            else:
                # Si es una nueva base agregada
                new_row = {
                    'nombre': b.name,
                    'tipo': b.tipo,
                    'direccion': 'Monteria',
                    'lat': b.lat,
                    'lon': b.lon,
                    'fuente': 'Calibración Manual'
                }
                df_bases = pd.concat([df_bases, pd.DataFrame([new_row])], ignore_index=True)
                
        df_all['Sitios_Candidatos'] = df_bases
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet, df_sheet in df_all.items():
                df_sheet.to_excel(writer, sheet_name=sheet, index=False)
                
        return {"status": "success", "total_bases": len(df_bases)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
