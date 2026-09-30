import pulp

def solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij):
    """
    Resuelve el modelo MILP de ubicación de ambulancias usando PuLP.
    """
    prob = pulp.LpProblem("MILP_Ambulancias", pulp.LpMaximize)
    I = range(num_nodes)
    J = range(num_bases)
    K = range(p_ambulances)

    # Variables
    x = pulp.LpVariable.dicts("x", ((j, k) for j in J for k in K), cat='Binary')
    y = pulp.LpVariable.dicts("y", (i for i in I), cat='Binary')
    z = pulp.LpVariable.dicts("z", ((i, j) for i in I for j in J), lowBound=0, cat='Continuous')
    v = pulp.LpVariable.dicts("v", ((i, j) for i in I for j in J), lowBound=0, cat='Continuous')

    # Función objetivo
    prob += (
        pulp.lpSum(demands[i] * y[i] for i in I) - 
        alpha * pulp.lpSum(demands[i] * v[i, j] for i in I for j in J)
    )

    # R1: Conservación de flota
    prob += pulp.lpSum(x[j, k] for j in J for k in K) == p_ambulances

    # R2: Capacidad de bases
    for j in J:
        prob += pulp.lpSum(x[j, k] for k in K) <= capacities[j]

    # R3: Cobertura
    for i in I:
        valid_bases = [j for j in J if t_ij[i][j] <= T_max]
        if valid_bases:
            prob += y[i] <= pulp.lpSum(x[j, k] for j in valid_bases for k in K)
        else:
            prob += y[i] == 0

    # R4: Balance de asignación
    for i in I:
        prob += pulp.lpSum(z[i, j] for j in J) == 1

    # R5: Acoplamiento de asignación
    for i in I:
        for j in J:
            prob += z[i, j] <= pulp.lpSum(x[j, k] for k in K)

    # R6: Linealización de holgura
    for i in I:
        for j in J:
            prob += v[i, j] >= (t_ij[i][j] - T_max) * z[i, j]

    prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[prob.status] != 'Optimal':
        return {"error": f"Sin solución óptima: {pulp.LpStatus[prob.status]}"}

    allocation = {j: 0 for j in J}
    for j in J:
        for k in K:
            val = pulp.value(x[j, k])
            if val is not None and round(val) == 1:
                allocation[j] += 1

    return {
        "allocation": allocation,
        "objective": pulp.value(prob.objective)
    }
