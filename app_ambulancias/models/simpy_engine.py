import simpy
import random

def run_simulation(allocation, t_ij, demands, sim_time_hours=720):
    """
    Ejecuta simulación de eventos discretos.
    """
    env = simpy.Environment()
    bases = {j: simpy.Resource(env, capacity=count) for j, count in allocation.items() if count > 0}
    
    if not bases:
        return []

    response_times = []

    def incident_gen(env, node_id, freq):
        if freq <= 0: return
        mtbi = sim_time_hours / freq
        while True:
            yield env.timeout(random.expovariate(1.0 / mtbi))
            env.process(handle_inc(env, node_id))

    def handle_inc(env, node_id):
        start = env.now
        active = sorted(bases.keys(), key=lambda j: t_ij[node_id][j])
        
        dispatched = False
        for j in active:
            if bases[j].count < bases[j].capacity:
                with bases[j].request() as req:
                    yield req
                    travel = t_ij[node_id][j] / 60.0
                    yield env.timeout(travel)
                    response_times.append((env.now - start) * 60.0)
                    yield env.timeout((30.0 + t_ij[node_id][j]) / 60.0)
                dispatched = True
                break
                
        if not dispatched and active:
            c = active[0]
            with bases[c].request() as req:
                yield req
                travel = t_ij[node_id][c] / 60.0
                yield env.timeout(travel)
                response_times.append((env.now - start) * 60.0)
                yield env.timeout((30.0 + t_ij[node_id][c]) / 60.0)

    for i, freq in enumerate(demands):
        env.process(incident_gen(env, i, freq))

    env.run(until=sim_time_hours)
    return response_times
