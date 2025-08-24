import random

def mostrar_tabela(tabela):
    print("\nTabela Simplex:")
    for linha in tabela:
        print(["{:+8.2f}".format(x) for x in linha])
    print()

def encontrar_coluna_pivo(tabela):
    ultima_linha = tabela[-1][:-1]
    valor_min = min(ultima_linha)
    if valor_min >= 0:
        return -1
    return ultima_linha.index(valor_min)

def encontrar_linha_pivo(tabela, coluna_pivo):
    menor = float('inf')
    linha_pivo = -1
    for i in range(len(tabela) - 1):
        elemento = tabela[i][coluna_pivo]
        if elemento > 0:
            razao = tabela[i][-1] / elemento
            if razao < menor:
                menor = razao
                linha_pivo = i
    return linha_pivo

def pivotear(tabela, linha_pivo, coluna_pivo):
    pivo = tabela[linha_pivo][coluna_pivo]
    tabela[linha_pivo] = [x / pivo for x in tabela[linha_pivo]]
    for i in range(len(tabela)):
        if i != linha_pivo:
            multiplicador = tabela[i][coluna_pivo]
            tabela[i] = [
                tabela[i][j] - multiplicador * tabela[linha_pivo][j]
                for j in range(len(tabela[0]))
            ]

def simplex(tabela, verbose=False):
    while True:
        if verbose:
            mostrar_tabela(tabela)
        coluna_pivo = encontrar_coluna_pivo(tabela)
        if coluna_pivo == -1:
            print("Solução ótima encontrada.")
            break
        linha_pivo = encontrar_linha_pivo(tabela, coluna_pivo)
        if linha_pivo == -1:
            print("Problema ilimitado.")
            break
        if verbose:
            print(f"Pivoteando na linha {linha_pivo + 1}, coluna {coluna_pivo + 1}")
        pivotear(tabela, linha_pivo, coluna_pivo)
    return tabela

def construir_tabela_transporte(oferta, demanda, custos):
    m = len(oferta)
    n = len(demanda)
    num_vars = m * n
    tabela = []

    # Restrições de oferta
    for i in range(m):
        linha = [0] * num_vars
        for j in range(n):
            linha[i * n + j] = 1
        folgas = [0] * (m + n)
        folgas[i] = 1
        linha += folgas
        linha.append(oferta[i])
        tabela.append(linha)

    # Restrições de demanda
    for j in range(n):
        linha = [0] * num_vars
        for i in range(m):
            linha[i * n + j] = 1
        folgas = [0] * (m + n)
        folgas[m + j] = 1
        linha += folgas
        linha.append(demanda[j])
        tabela.append(linha)

    # Função objetivo (minimizar → max -Z)
    obj = []
    for i in range(m):
        for j in range(n):
            obj.append(-custos[i][j])
    obj += [0] * (m + n)
    obj.append(0)
    tabela.append(obj)

    return tabela

def extrair_solucao(tabela, m, n):
    num_vars = m * n
    valores = [0] * num_vars
    for j in range(num_vars):
        col = [tabela[i][j] for i in range(len(tabela))]
        if col.count(1) == 1 and col.count(0) == len(tabela) - 1:
            linha_base = col.index(1)
            valores[j] = tabela[linha_base][-1]
    return valores, -tabela[-1][-1]  # Negar porque maximizamos -Z

def gerar_problema_transporte_grande(m=15, n=15, semente=42):
    random.seed(semente)
    total = 100000

    oferta = [random.randint(1000, 4000) for _ in range(m)]
    escala = total / sum(oferta)
    oferta = [int(x * escala) for x in oferta]
    oferta[-1] += total - sum(oferta)

    demanda = [random.randint(1000, 4000) for _ in range(n)]
    escala = total / sum(demanda)
    demanda = [int(x * escala) for x in demanda]
    demanda[-1] += total - sum(demanda)

    custos = [[random.randint(1, 100) for _ in range(n)] for _ in range(m)]

    return oferta, demanda, custos

# ------------------------------------------
# Execução principal
# ------------------------------------------

# Altere os valores abaixo para testar com problemas maiores
m = 1000  # número de fontes
n = 1000 # número de destinos

# Gerar problema balanceado grande
oferta, demanda, custos = gerar_problema_transporte_grande(m, n)

# Construir a tabela simplex
tabela = construir_tabela_transporte(oferta, demanda, custos)

# Resolver usando simplex padrão
tabela_final = simplex(tabela, verbose=False)

# Obter solução
valores, custo_total = extrair_solucao(tabela_final, m, n)

# Mostrar solução
print("\nSolução ótima encontrada:")
for i in range(m):
    for j in range(n):
        x = valores[i * n + j]
        if x > 0:
            print(f"x{i+1}{j+1} = {x:.2f}")
print(f"\nCusto total mínimo: {custo_total:.2f}")
