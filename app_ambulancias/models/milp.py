import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
import pulp

def solve_milp(num_nodes, num_bases, p_ambulances, T_max, alpha, demands, capacities, t_ij):
    """
    Resuelve el modelo MILP de ubicación de ambulancias usando SciPy MILP (HiGHS) con fallback.
    """
    try:
        # Indexación de variables
        def idx_x(j, k): return j * p_ambulances + k
        def idx_y(i): return num_bases * p_ambulances + i
        def idx_z(i, j): return num_bases * p_ambulances + num_nodes + i * num_bases + j
        def idx_v(i, j): return num_bases * p_ambulances + num_nodes + num_nodes * num_bases + i * num_bases + j

        n_vars = num_bases * p_ambulances + num_nodes + num_nodes * num_bases + num_nodes * num_bases

        # Coeficientes para MINIMIZACIÓN en SciPy (c = -objetivo)
        c = np.zeros(n_vars)
        for i in range(num_nodes):
            c[idx_y(i)] = -float(demands[i])
            for j in range(num_bases):
                c[idx_v(i, j)] = float(alpha) * float(demands[i])

        # Integridad (1 = binario/entero, 0 = continuo)
        integrality = np.zeros(n_vars)
        for j in range(num_bases):
            for k in range(p_ambulances):
                integrality[idx_x(j, k)] = 1
        for i in range(num_nodes):
            integrality[idx_y(i)] = 1

        # Límites (Bounds)
        lb = np.zeros(n_vars)
        ub = np.ones(n_vars) * np.inf
        for j in range(num_bases):
            for k in range(p_ambulances):
                ub[idx_x(j, k)] = 1
        for i in range(num_nodes):
            ub[idx_y(i)] = 1

        bounds = Bounds(lb, ub)

        # Restricciones
        rows = []
        lhs = []
        rhs = []

        # R1: Conservación de flota
        r1 = np.zeros(n_vars)
        for j in range(num_bases):
            for k in range(p_ambulances):
                r1[idx_x(j, k)] = 1.0
        rows.append(r1); lhs.append(float(p_ambulances)); rhs.append(float(p_ambulances))

        # R2: Capacidad de bases
        for j in range(num_bases):
            r2 = np.zeros(n_vars)
            for k in range(p_ambulances):
                r2[idx_x(j, k)] = 1.0
            rows.append(r2); lhs.append(-np.inf); rhs.append(float(capacities[j]))

        # R3: Cobertura dentro de T_max
        for i in range(num_nodes):
            r3 = np.zeros(n_vars)
            r3[idx_y(i)] = 1.0
            valid_bases = [j for j in range(num_bases) if t_ij[i][j] <= T_max]
            for j in valid_bases:
                for k in range(p_ambulances):
                    r3[idx_x(j, k)] -= 1.0
            rows.append(r3); lhs.append(-np.inf); rhs.append(0.0)

        # R4: Balance de asignación de demanda
        for i in range(num_nodes):
            r4 = np.zeros(n_vars)
            for j in range(num_bases):
                r4[idx_z(i, j)] = 1.0
            rows.append(r4); lhs.append(1.0); rhs.append(1.0)

        # R5: Acoplamiento lógico
        for i in range(num_nodes):
            for j in range(num_bases):
                r5 = np.zeros(n_vars)
                r5[idx_z(i, j)] = 1.0
                for k in range(p_ambulances):
                    r5[idx_x(j, k)] -= 1.0
                rows.append(r5); lhs.append(-np.inf); rhs.append(0.0)

        # R6: Linealización de holgura de tiempo
        for i in range(num_nodes):
            for j in range(num_bases):
                r6 = np.zeros(n_vars)
                r6[idx_v(i, j)] = 1.0
                diff = t_ij[i][j] - T_max
                if diff > 0:
                    r6[idx_z(i, j)] -= float(diff)
                rows.append(r6); lhs.append(0.0); rhs.append(np.inf)

        A = np.array(rows)
        constraints = LinearConstraint(A, lhs, rhs)

        sol = milp(c=c, integrality=integrality, bounds=bounds, constraints=constraints)

        if sol.success:
            allocation = {j: 0 for j in range(num_bases)}
            for j in range(num_bases):
                for k in range(p_ambulances):
                    if round(sol.x[idx_x(j, k)]) == 1:
                        allocation[j] += 1

            return {
                "allocation": allocation,
                "objective": float(-sol.fun)
            }
    except Exception as e:
        print(f"SciPy MILP fallback error: {e}")

    # Fallback heurístico si no hay solver
    allocation = {j: 0 for j in range(num_bases)}
    for k in range(p_ambulances):
        b = k % num_bases
        allocation[b] += 1
    return {"allocation": allocation, "objective": 0.0}
