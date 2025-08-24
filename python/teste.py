import numpy as np
from scipy.optimize import linprog
import time

# Gerar um grande problema de transporte
np.random.seed(42)
n_sources = 500
n_destinations = 500

supply = np.random.randint(100, 1000, size=n_sources)
demand = np.random.randint(100, 1000, size=n_destinations)
costs = np.random.randint(1, 100, size=(n_sources, n_destinations))

# Ajustar supply e demand para serem iguais (problema balanceado)
total_supply = supply.sum()
total_demand = demand.sum()
if total_supply > total_demand:
    supply[-1] -= (total_supply - total_demand)
elif total_demand > total_supply:
    demand[-1] -= (total_demand - total_supply)

# Flatten costs para o vetor c do linprog
c = costs.flatten()

# Criar matriz de restrições para supply
A_eq = []
b_eq = []

# Restrição de oferta
for i in range(n_sources):
    row = np.zeros(n_sources * n_destinations)
    row[i * n_destinations:(i + 1) * n_destinations] = 1
    A_eq.append(row)
    b_eq.append(supply[i])

# Restrição de demanda
for j in range(n_destinations):
    row = np.zeros(n_sources * n_destinations)
    row[j::n_destinations] = 1
    A_eq.append(row)
    b_eq.append(demand[j])

A_eq = np.array(A_eq)
b_eq = np.array(b_eq)

# Rodar o método simplex e medir tempo
start = time.time()
result = linprog(c, A_eq=A_eq, b_eq=b_eq, method='highs')
end = time.time()

print(f"Tempo de execução: {end - start:.2f} segundos")
print(f"Status: {result.message}")
if result.success and result.fun is not None:
    print(f"Custo mínimo: {result.fun:.2f}")
else:
    print("Não foi possível encontrar uma solução viável para o problema.")