import random
import time
import psutil
import os

def mostrar_tabela(tabela):
    print("\nTabela Simplex:")
    for i, linha in enumerate(tabela):
        if i == len(tabela) - 1:
            print("Z:", end=" ")
        else:
            print(f"R{i+1}:", end=" ")
        print(["{:+8.2f}".format(x) for x in linha])
    print()

def encontrar_coluna_pivo(tabela):
    """Encontra a coluna com o menor valor negativo na linha objetivo"""
    ultima_linha = tabela[-1][:-1]  # Exclui a coluna RHS
    valor_min = min(ultima_linha)
    if valor_min >= 0:
        return -1  # Solução ótima encontrada
    return ultima_linha.index(valor_min)

def encontrar_linha_pivo(tabela, coluna_pivo):
    """Teste da razão mínima para encontrar a linha pivô"""
    menor_razao = float('inf')
    linha_pivo = -1
    
    for i in range(len(tabela) - 1):  # Exclui linha objetivo
        elemento_pivo = tabela[i][coluna_pivo]
        rhs = tabela[i][-1]
        
        # Só considera elementos positivos para evitar divisão por zero/negativo
        if elemento_pivo > 0:
            razao = rhs / elemento_pivo
            if razao >= 0 and razao < menor_razao:  # Razão não-negativa
                menor_razao = razao
                linha_pivo = i
    
    return linha_pivo

def pivotear(tabela, linha_pivo, coluna_pivo):
    """Executa as operações de pivoteamento"""
    num_linhas = len(tabela)
    num_colunas = len(tabela[0])
    pivo = tabela[linha_pivo][coluna_pivo]
    
    # Passo 1: Normalizar a linha do pivô
    for j in range(num_colunas):
        tabela[linha_pivo][j] /= pivo
    
    # Passo 2: Zerar os outros elementos da coluna pivô
    for i in range(num_linhas):
        if i != linha_pivo:
            multiplicador = tabela[i][coluna_pivo]
            for j in range(num_colunas):
                tabela[i][j] -= multiplicador * tabela[linha_pivo][j]

def simplex(tabela, verbose=False, max_iteracoes=1000000):
    """Algoritmo Simplex padrão"""
    print("Iniciando método Simplex...")
    inicio = time.time()
    iteracao = 0
    
    while iteracao < max_iteracoes:
        iteracao += 1
        
        if verbose or (iteracao % 10000 == 0):
            print(f"Iteração {iteracao}")
            if verbose:
                mostrar_tabela(tabela)
        
        # Passo 1: Encontrar coluna pivô
        coluna_pivo = encontrar_coluna_pivo(tabela)
        if coluna_pivo == -1:
            tempo_total = time.time() - inicio
            print(f"Solução ótima encontrada em {iteracao} iterações!")
            print(f"Tempo de execução: {tempo_total:.2f} segundos")
            break
        
        # Passo 2: Encontrar linha pivô
        linha_pivo = encontrar_linha_pivo(tabela, coluna_pivo)
        if linha_pivo == -1:
            print("Problema ilimitado - não há solução ótima finita.")
            break
        
        if verbose:
            print(f"Pivoteando: linha {linha_pivo + 1}, coluna {coluna_pivo + 1}")
            print(f"Elemento pivô: {tabela[linha_pivo][coluna_pivo]:.6f}")
        
        # Passo 3: Pivotear
        pivotear(tabela, linha_pivo, coluna_pivo)
    
    if iteracao >= max_iteracoes:
        print(f"ATENÇÃO: Limite de {max_iteracoes} iterações atingido!")
    
    return tabela

def construir_tabela_transporte(oferta, demanda, custos):
    """Constrói a tabela simplex para o problema de transporte"""
    m = len(oferta)  # número de origens
    n = len(demanda) # número de destinos
    num_vars = m * n  # variáveis x_ij
    
    print(f"Construindo tabela: {m} origens × {n} destinos = {num_vars} variáveis")
    print(f"Restrições: {m} (oferta) + {n} (demanda) = {m + n}")
    
    # Verificar balanceamento
    total_oferta = sum(oferta)
    total_demanda = sum(demanda)
    if abs(total_oferta - total_demanda) > 1e-6:
        print(f"ERRO: Problema desbalanceado!")
        print(f"Oferta total: {total_oferta}")
        print(f"Demanda total: {total_demanda}")
        return None
    
    tabela = []
    
    # Restrições de oferta: Σ(x_ij) = oferta_i para cada origem i
    for i in range(m):
        linha = [0.0] * num_vars
        for j in range(n):
            linha[i * n + j] = 1.0
        
        # Variáveis de folga para restrições de oferta
        folgas_oferta = [0.0] * m
        folgas_oferta[i] = 1.0
        
        # Variáveis de folga para restrições de demanda
        folgas_demanda = [0.0] * n
        
        linha += folgas_oferta + folgas_demanda
        linha.append(float(oferta[i]))
        tabela.append(linha)
    
    # Restrições de demanda: Σ(x_ij) = demanda_j para cada destino j
    for j in range(n):
        linha = [0.0] * num_vars
        for i in range(m):
            linha[i * n + j] = 1.0
        
        # Variáveis de folga para restrições de oferta
        folgas_oferta = [0.0] * m
        
        # Variáveis de folga para restrições de demanda
        folgas_demanda = [0.0] * n
        folgas_demanda[j] = 1.0
        
        linha += folgas_oferta + folgas_demanda
        linha.append(float(demanda[j]))
        tabela.append(linha)
    
    # Função objetivo: minimizar Σ(custo_ij × x_ij)
    # Como o Simplex maximiza, usamos -custo_ij
    linha_obj = []
    for i in range(m):
        for j in range(n):
            linha_obj.append(-float(custos[i][j]))
    
    # Coeficientes zero para variáveis de folga
    linha_obj += [0.0] * (m + n)
    linha_obj.append(0.0)  # RHS da função objetivo
    tabela.append(linha_obj)
    
    return tabela

def extrair_solucao(tabela, m, n):
    """Extrai a solução da tabela simplex final"""
    num_vars = m * n
    valores = [0.0] * num_vars
    
    # Para cada variável original x_ij
    for j in range(num_vars):
        coluna = [tabela[i][j] for i in range(len(tabela) - 1)]
        
        # Se a variável é básica (coluna tem exatamente um 1 e o resto zeros)
        if coluna.count(1) == 1 and coluna.count(0) == len(coluna) - 1:
            linha_base = coluna.index(1)
            valores[j] = max(0, tabela[linha_base][-1])  # Garante não-negatividade
    
    # O custo total é o negativo do valor da função objetivo
    custo_total = -tabela[-1][-1]
    
    return valores, custo_total

def gerar_problema_transporte_grande(m=15, n=15, semente=42):
    """Gera um problema de transporte balanceado"""
    random.seed(semente)
    total = 100000
    
    # Gerar oferta
    oferta = [random.randint(1000, 4000) for _ in range(m)]
    escala = total / sum(oferta)
    oferta = [int(x * escala) for x in oferta]
    oferta[-1] += total - sum(oferta)  # Ajuste para balanceamento exato
    
    # Gerar demanda
    demanda = [random.randint(1000, 4000) for _ in range(n)]
    escala = total / sum(demanda)
    demanda = [int(x * escala) for x in demanda]
    demanda[-1] += total - sum(demanda)  # Ajuste para balanceamento exato
    
    # Gerar custos
    custos = [[random.randint(1, 100) for _ in range(n)] for _ in range(m)]
    
    return oferta, demanda, custos

# ------------------------------------------
# Execução principal
# ------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("MÉTODO SIMPLEX PADRÃO PARA PROBLEMAS DE TRANSPORTE")
    print("=" * 60)
    
    processo = psutil.Process(os.getpid())
    
    inicio = time.time()
    
    # ALTERE AQUI O TAMANHO DO PROBLEMA
    m = 20   # número de origens
    n = 20   # número de destinos
    
    print(f"\nGerando problema de transporte: {m}×{n}")
    
    # Gerar problema
    oferta, demanda, custos = gerar_problema_transporte_grande(m, n)
    
    print(f"\nOferta: {oferta}")
    print(f"Demanda: {demanda}")
    print(f"Soma oferta: {sum(oferta)}")
    print(f"Soma demanda: {sum(demanda)}")
    
    print("\nMatriz de custos:")
    for i, linha in enumerate(custos):
        print(f"Origem {i+1}: {linha}")
    
    # Construir tabela simplex
    print("\n" + "-" * 40)
    tabela = construir_tabela_transporte(oferta, demanda, custos)
    
    if tabela is None:
        print("Erro na construção da tabela!")
        exit(1)
    
    print(f"Tabela construída: {len(tabela)}×{len(tabela[0])}")
    
    # Resolver com Simplex
    print("\n" + "-" * 40)
    tabela_final = simplex(tabela, verbose=False)
    
    # Extrair e mostrar solução
    print("\n" + "-" * 40)
    valores, custo_total = extrair_solucao(tabela_final, m, n)
    
    print("SOLUÇÃO ÓTIMA:")
    print("-" * 20)
    
    fim = time.time()
    
    # Medidas de consumo
    tempo_execucao = fim - inicio
    memoria = processo.memory_info().rss / (1024 * 1024)  # MB
    cpu_percent = processo.cpu_percent(interval=1.0)  # % CPU
    
    print("\n--- MÉTRICAS PYTHON ---")
    print(f"Tempo de execução: {tempo_execucao:.2f} segundos")
    print(f"Memória usada: {memoria:.2f} MB")
    print(f"Uso médio de CPU: {cpu_percent:.2f}%")
    
    solucao_encontrada = False
    for i in range(m):
        for j in range(n):
            x = valores[i * n + j]
            if x > 1e-6:  # Mostrar apenas valores significativos
                print(f"x_{i+1},{j+1} = {x:>10.2f}  (custo unitário: {custos[i][j]})")
                solucao_encontrada = True
    
    if not solucao_encontrada:
        print("Nenhuma variável com valor positivo encontrada.")
    
    print(f"\nCUSTO TOTAL MÍNIMO: {custo_total:.2f}")
    
    # Verificação das restrições
    print("\n" + "-" * 40)
    print("VERIFICAÇÃO DAS RESTRIÇÕES:")
    
    # Verificar oferta
    for i in range(m):
        soma_linha = sum(valores[i * n + j] for j in range(n))
        print(f"Origem {i+1}: {soma_linha:.2f} = {oferta[i]} ✓" if abs(soma_linha - oferta[i]) < 1e-6 else f"Origem {i+1}: {soma_linha:.2f} ≠ {oferta[i]} ✗")
    
    # Verificar demanda  
    for j in range(n):
        soma_coluna = sum(valores[i * n + j] for i in range(m))
        print(f"Destino {j+1}: {soma_coluna:.2f} = {demanda[j]} ✓" if abs(soma_coluna - demanda[j]) < 1e-6 else f"Destino {j+1}: {soma_coluna:.2f} ≠ {demanda[j]} ✗")