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
    from utils.data_loader import calculate_clusters, generate_t_ij
    from models.milp import solve_milp
except ImportError:
    from app_ambulancias.utils.data_loader import calculate_clusters, generate_t_ij
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
    num_nodes: int = 13
    num_bases: int = 7
    t_max: float = 10.0
    alpha: float = 0.5

@app.get("/")
def read_root():
    return {"message": "API Backend de APH Montería en línea"}

@app.post("/api/optimize")
async def optimize_fleet(req: OptimizeRequest):
    try:
        # Usamos los clusters para generar ubicaciones si no estamos cargando el CSV completo
        centros = calculate_clusters(req.num_nodes)
        base_coords = centros[:req.num_bases]
        node_coords = centros[:req.num_nodes]
        t_ij = generate_t_ij(node_coords, base_coords)
        
        # Demanda simulada
        demands = [random.randint(10, 60) for _ in range(req.num_nodes)]
        capacities = [max(2, req.num_ambulances // req.num_bases + 1) for _ in range(req.num_bases)]
        
        # Ejecutar MILP (El modelo matemático)
        opt_res = solve_milp(req.num_nodes, req.num_bases, req.num_ambulances, req.t_max, req.alpha, demands, capacities, t_ij)
        
        if "error" in opt_res:
            raise HTTPException(status_code=400, detail=opt_res["error"])
            
        return {
            "status": "success",
            "allocation": opt_res["allocation"],
            "coverage": opt_res.get("coverage", 0),
            "avg_time": opt_res.get("avg_time", 0),
            "base_coords": base_coords,
            "node_coords": node_coords
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
