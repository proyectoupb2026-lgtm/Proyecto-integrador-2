from flask import Flask, request, jsonify, render_template
import pulp
import simpy
import random
import numpy as np
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

def solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij):
    # Definir el problema
    prob = pulp.LpProblem("Localizacion_Ambulancias", pulp.LpMaximize)
    
    # Conjuntos e índices
    I = range(num_nodes)  # Nodos de demanda
    J = range(num_bases)  # Bases
    K = range(p_ambulances) # Ambulancias
    
    # Variables de decisión
    x = pulp.LpVariable.dicts("x", ((j, k) for j in J for k in K), cat='Binary')
    y = pulp.LpVariable.dicts("y", (i for i in I), cat='Binary')
    z = pulp.LpVariable.dicts("z", ((i, j) for i in I for j in J), lowBound=0, cat='Continuous')
    v = pulp.LpVariable.dicts("v", ((i, j) for i in I for j in J), lowBound=0, cat='Continuous')
    
    # Función Objetivo: Maximizar Z = sum(d_i * y_i) - alpha * sum(d_i * v_ij)
    prob += pulp.lpSum(demands[i] * y[i] for i in I) - alpha * pulp.lpSum(demands[i] * v[i, j] for i in I for j in J)
    
    # Restricciones operativas
    # 1. Total de ambulancias es p
    prob += pulp.lpSum(x[j, k] for j in J for k in K) == p_ambulances
    
    # 2. Capacidad física de las bases
    for j in J:
        prob += pulp.lpSum(x[j, k] for k in K) <= capacities[j]
        
    # 3. Cobertura del nodo (y_i = 1 si al menos una base con tiempo <= T_max tiene una ambulancia)
    for i in I:
        valid_bases = [j for j in J if t_ij[i][j] <= T_max]
        prob += y[i] <= pulp.lpSum(x[j, k] for j in valid_bases for k in K)
        
    # 4. Balance de asignación de demanda
    for i in I:
        prob += pulp.lpSum(z[i, j] for j in J) == 1
        
    # 5. Acoplamiento lógico
    for i in I:
        for j in J:
            prob += z[i, j] <= pulp.lpSum(x[j, k] for k in K)
            
    # 6. Linearización de holgura
    for i in I:
        for j in J:
            prob += v[i, j] >= t_ij[i][j] * z[i, j] - T_max * z[i, j]
            
    # Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Extraer resultados
    status = pulp.LpStatus[prob.status]
    if status != 'Optimal':
        return {"error": "No se encontró solución óptima", "status": status}
        
    allocation = {j: 0 for j in J}
    for j in J:
        for k in K:
            if pulp.value(x[j, k]) == 1.0:
                allocation[j] += 1
                
    obj_value = pulp.value(prob.objective)
    
    return {
        "status": status,
        "allocation": allocation,
        "objective": obj_value
    }


# SIMPY SIMULATION
def run_simulation(allocation, t_ij, demands, sim_time_hours=720): # 30 days
    env = simpy.Environment()
    
    # Crear recursos para bases
    bases = {}
    for j, count in allocation.items():
        if count > 0:
            bases[j] = simpy.Resource(env, capacity=count)
            
    if not bases:
        return {"error": "No hay ambulancias asignadas"}

    # Tiempos de respuesta recopilados
    response_times = []
    
    def incident_generator(env, node_id, freq, bases, t_ij, response_times):
        # freq is incidents per month (e.g. 720 hours)
        # convert to mean time between incidents (hours)
        if freq <= 0:
            return
        mtbi = sim_time_hours / freq
        
        while True:
            # Poisson process = exponential interarrival times
            yield env.timeout(random.expovariate(1.0 / mtbi))
            
            # Incident occurs, request closest available ambulance
            env.process(handle_incident(env, node_id, bases, t_ij, response_times))
            
    def handle_incident(env, node_id, bases, t_ij, response_times):
        start_time = env.now
        
        # Encontrar base más cercana con ambulancias
        # (Para simplificar, asignamos a la más cercana, pero consideramos disponibilidad)
        closest_bases_sorted = sorted(bases.keys(), key=lambda j: t_ij[node_id][j])
        
        assigned = False
        for j in closest_bases_sorted:
            # check availability (queue length vs capacity, etc. - in a simple greedy way)
            if bases[j].count < bases[j].capacity:
                with bases[j].request() as req:
                    yield req
                    # wait for travel time to scene
                    yield env.timeout(t_ij[node_id][j] / 60.0) # assuming t_ij is minutes, env in hours
                    response_time = (env.now - start_time) * 60.0 # minutes
                    response_times.append(response_time)
                    # wait for attention and return time
                    yield env.timeout((30.0 + t_ij[node_id][j]) / 60.0) # 30 mins attention + return
                assigned = True
                break
                
        if not assigned:
            # Queue at the absolute closest base if all are busy
            closest = closest_bases_sorted[0]
            with bases[closest].request() as req:
                yield req
                # travel
                yield env.timeout(t_ij[node_id][closest] / 60.0)
                response_time = (env.now - start_time) * 60.0 # minutes
                response_times.append(response_time)
                # attention
                yield env.timeout((30.0 + t_ij[node_id][closest]) / 60.0)
                
    # Iniciar procesos
    for node_id, freq in enumerate(demands):
        env.process(incident_generator(env, node_id, freq, bases, t_ij, response_times))
        
    env.run(until=sim_time_hours)
    
    return response_times

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/simulate', methods=['POST'])
def simulate():
    try:
        data = request.json
        num_nodes = int(data.get('num_nodes', 3))
        num_bases = int(data.get('num_bases', 2))
        p_ambulances = int(data.get('num_ambulances', 3))
        T_max = float(data.get('T_max', 10.0))
        alpha = float(data.get('alpha', 0.5))
        
        demands = data.get('demands')
        capacities = data.get('capacities')
        t_ij = data.get('t_ij')
        
        # 1. Optimización (MILP)
        opt_res = solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij)
        
        if 'error' in opt_res:
            return jsonify(opt_res), 400
            
        allocation = opt_res['allocation']
        
        # 2. Simulación (SimPy)
        sim_res = run_simulation(allocation, t_ij, demands)
        
        # Calcular KPIs
        avg_resp_time = np.mean(sim_res) if sim_res else 0
        max_resp_time = np.max(sim_res) if sim_res else 0
        coverage = len([t for t in sim_res if t <= T_max]) / len(sim_res) * 100 if sim_res else 0
        
        return jsonify({
            'optimisation': opt_res,
            'simulation': {
                'avg_response_time': avg_resp_time,
                'max_response_time': max_resp_time,
                'coverage_percent': coverage,
                'total_incidents_simulated': len(sim_res)
            }
        })
        
    except Exception as e:
        logging.error(f"Error during simulation: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
