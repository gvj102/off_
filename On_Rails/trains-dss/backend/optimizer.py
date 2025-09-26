from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

def solve_precedence(trains, weights=None):
    n = len(trains)
    idx = {t:i for i,t in enumerate(trains)}

    prob = LpProblem('precedence', LpMinimize)
    x = {}
    for i in range(n):
        for j in range(n):
            if i==j: continue
            x[(i,j)] = LpVariable(f'x_{i}_{j}', cat='Binary')

    for i in range(n):
        for j in range(i+1,n):
            prob += x[(i,j)] + x[(j,i)] == 1

    for i in range(n):
        for j in range(n):
            for k in range(n):
                if i==j or j==k or i==k: continue
                prob += x[(i,j)] + x[(j,k)] - x[(i,k)] <= 1

    if weights is None:
        weights = {t:1.0 for t in trains}
    positions = {i: lpSum([x[(j,i)] for j in range(n) if j!=i]) for i in range(n)}
    prob += lpSum([weights[trains[i]] * positions[i] for i in range(n)])

    prob.solve()
    order = sorted(trains, key=lambda t: sum(int(x[(j,idx[t])].value()) for j in range(n) if j!=idx[t]))
    return order, LpStatus[prob.status]

if __name__ == '_main_':
    trains = ['T1','T2','T3','T4']
    weights = {'T1':2,'T2':1,'T3':3,'T4':1}
    order, status = solve_precedence(trains, weights)
    print('Status', status)
    print('Order', order)