oferta = [400, 700, 500]
demanda = [600, 500, 300, 200]
plantas = ["Planta 1", "Planta 2", "Planta 3", "Fictícia"]
custos = [
    [4, 7, 6, 0],
    [5, 5, 5, 0],
    [9, 5, 8, 0] 
]
fornecedores = ["A", "B", "C"]

# Mostrar tabela de custos
print(f"{'':12}", end="")
for p in plantas:
    print(f"{p:>10}", end="")
print()
for i, linha in enumerate(custos):
    print(f"Fornecedor {fornecedores[i]:<3}", end="")
    for valor in linha:
        print(f"{valor:>10}", end="")
    print()

print("\nTotal oferta:", sum(oferta))
print("Total demanda:", sum(demanda))

# ---------- MÉTODO DO CANTO NOROESTE ----------
x = [[0 for j in range(len(demanda))] for i in range(len(oferta))]

oferta_temp = oferta.copy()
demanda_temp = demanda.copy()

i = 0
j = 0
while i < len(oferta) and j < len(demanda):
    quantidade = min(oferta_temp[i], demanda_temp[j])
    x[i][j] = quantidade
    oferta_temp[i] -= quantidade
    demanda_temp[j] -= quantidade
    
    if oferta_temp[i] == 0:
        i += 1
    elif demanda_temp[j] == 0:
        j += 1

print("\nMatriz de transporte após Canto Noroeste:")
for linha in x:
    print(linha)

# ---------- CUSTO INICIAL ----------
custo_total = 0
for i in range(len(fornecedores)):
    for j in range(len(plantas)):
        custo_total += custos[i][j] * x[i][j]
print("\nCusto total da solução inicial:", custo_total)