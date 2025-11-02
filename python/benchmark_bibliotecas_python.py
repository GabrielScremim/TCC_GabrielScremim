"""
Benchmark de Bibliotecas Python para Problemas de Transporte
Compara: Implementação Manual, SciPy, PuLP, CVXPY, OR-Tools
"""

import random
import time
import psutil
import os
import json
import statistics
import gc
import numpy as np

# ========================================
# IMPORTAR BIBLIOTECAS (com tratamento de erro)
# ========================================

bibliotecas_disponiveis = {
    'manual': True,  # Nossa implementação sempre está disponível
    'scipy': True,
    'pulp': True,
    'cvxpy': True,
    'ortools': True
}

try:
    from scipy.optimize import linprog
    bibliotecas_disponiveis['scipy'] = True
    print("✓ SciPy disponível")
except ImportError:
    print("✗ SciPy não disponível (pip install scipy)")

try:
    import pulp
    bibliotecas_disponiveis['pulp'] = True
    print("✓ PuLP disponível")
except ImportError:
    print("✗ PuLP não disponível (pip install pulp)")

try:
    import cvxpy as cp
    bibliotecas_disponiveis['cvxpy'] = True
    print("✓ CVXPY disponível")
except ImportError:
    print("✗ CVXPY não disponível (pip install cvxpy)")

try:
    from ortools.linear_solver import pywraplp
    bibliotecas_disponiveis['ortools'] = True
    print("✓ OR-Tools disponível")
except ImportError:
    print("✗ OR-Tools não disponível (pip install ortools)")

print()

# ========================================
# GERADOR DE PROBLEMAS
# ========================================

def gerar_problema_transporte(m, n, total=100000, semente=42):
    """Gera um problema de transporte balanceado"""
    random.seed(semente)
    np.random.seed(semente)
    
    # Gerar oferta
    oferta = [random.randint(1000, 4000) for _ in range(m)]
    escala = total / sum(oferta)
    oferta = [int(x * escala) for x in oferta]
    oferta[-1] += total - sum(oferta)
    
    # Gerar demanda
    demanda = [random.randint(1000, 4000) for _ in range(n)]
    escala = total / sum(demanda)
    demanda = [int(x * escala) for x in demanda]
    demanda[-1] += total - sum(demanda)
    
    # Gerar custos
    custos = [[random.randint(1, 100) for _ in range(n)] for _ in range(m)]
    
    return oferta, demanda, custos

# ========================================
# IMPLEMENTAÇÃO MANUAL (do seu código)
# ========================================

def encontrar_coluna_pivo(tabela):
    ultima_linha = tabela[-1][:-1]
    valor_min = min(ultima_linha)
    if valor_min >= 0:
        return -1
    return ultima_linha.index(valor_min)

def encontrar_linha_pivo(tabela, coluna_pivo):
    menor_razao = float('inf')
    linha_pivo = -1
    
    for i in range(len(tabela) - 1):
        elemento_pivo = tabela[i][coluna_pivo]
        rhs = tabela[i][-1]
        
        if elemento_pivo > 0:
            razao = rhs / elemento_pivo
            if razao >= 0 and razao < menor_razao:
                menor_razao = razao
                linha_pivo = i
    
    return linha_pivo

def pivotear(tabela, linha_pivo, coluna_pivo):
    num_linhas = len(tabela)
    num_colunas = len(tabela[0])
    pivo = tabela[linha_pivo][coluna_pivo]
    
    for j in range(num_colunas):
        tabela[linha_pivo][j] /= pivo
    
    for i in range(num_linhas):
        if i != linha_pivo:
            multiplicador = tabela[i][coluna_pivo]
            for j in range(num_colunas):
                tabela[i][j] -= multiplicador * tabela[linha_pivo][j]

def simplex_manual(tabela, max_iteracoes=1000000):
    iteracao = 0
    
    while iteracao < max_iteracoes:
        iteracao += 1
        
        coluna_pivo = encontrar_coluna_pivo(tabela)
        if coluna_pivo == -1:
            return iteracao, -tabela[-1][-1]
        
        linha_pivo = encontrar_linha_pivo(tabela, coluna_pivo)
        if linha_pivo == -1:
            return -1, None
        
        pivotear(tabela, linha_pivo, coluna_pivo)
    
    return iteracao, None

def construir_tabela_transporte(oferta, demanda, custos):
    m = len(oferta)
    n = len(demanda)
    num_vars = m * n
    
    tabela = []
    
    # Restrições de oferta
    for i in range(m):
        linha = [0.0] * num_vars
        for j in range(n):
            linha[i * n + j] = 1.0
        
        folgas_oferta = [0.0] * m
        folgas_oferta[i] = 1.0
        folgas_demanda = [0.0] * n
        
        linha += folgas_oferta + folgas_demanda
        linha.append(float(oferta[i]))
        tabela.append(linha)
    
    # Restrições de demanda
    for j in range(n):
        linha = [0.0] * num_vars
        for i in range(m):
            linha[i * n + j] = 1.0
        
        folgas_oferta = [0.0] * m
        folgas_demanda = [0.0] * n
        folgas_demanda[j] = 1.0
        
        linha += folgas_oferta + folgas_demanda
        linha.append(float(demanda[j]))
        tabela.append(linha)
    
    # Função objetivo
    linha_obj = []
    for i in range(m):
        for j in range(n):
            linha_obj.append(-float(custos[i][j]))
    
    linha_obj += [0.0] * (m + n)
    linha_obj.append(0.0)
    tabela.append(linha_obj)
    
    return tabela

def resolver_manual(oferta, demanda, custos):
    """Resolve usando implementação manual do Simplex"""
    tabela = construir_tabela_transporte(oferta, demanda, custos)
    iteracoes, custo = simplex_manual(tabela)
    return custo, iteracoes

# ========================================
# SCIPY
# ========================================

def resolver_scipy(oferta, demanda, custos):
    """Resolve usando scipy.optimize.linprog"""
    m = len(oferta)
    n = len(demanda)
    
    # Vetor de custos (função objetivo)
    c = np.array([custos[i][j] for i in range(m) for j in range(n)])
    
    # Restrições de igualdade: A_eq * x = b_eq
    A_eq = []
    b_eq = []
    
    # Restrições de oferta
    for i in range(m):
        linha = [0] * (m * n)
        for j in range(n):
            linha[i * n + j] = 1
        A_eq.append(linha)
        b_eq.append(oferta[i])
    
    # Restrições de demanda
    for j in range(n):
        linha = [0] * (m * n)
        for i in range(m):
            linha[i * n + j] = 1
        A_eq.append(linha)
        b_eq.append(demanda[j])
    
    A_eq = np.array(A_eq)
    b_eq = np.array(b_eq)
    
    # Limites das variáveis (não-negatividade)
    bounds = [(0, None) for _ in range(m * n)]
    
    # Resolver
    resultado = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
    
    if resultado.success:
        return resultado.fun, resultado.nit if hasattr(resultado, 'nit') else 0
    else:
        return None, -1

# ========================================
# PULP
# ========================================

def resolver_pulp(oferta, demanda, custos):
    """Resolve usando PuLP"""
    m = len(oferta)
    n = len(demanda)
    
    # Criar problema
    prob = pulp.LpProblem("Transporte", pulp.LpMinimize)
    
    # Variáveis de decisão
    x = {}
    for i in range(m):
        for j in range(n):
            x[i, j] = pulp.LpVariable(f"x_{i}_{j}", lowBound=0)
    
    # Função objetivo
    prob += pulp.lpSum(custos[i][j] * x[i, j] for i in range(m) for j in range(n))
    
    # Restrições de oferta
    for i in range(m):
        prob += pulp.lpSum(x[i, j] for j in range(n)) == oferta[i]
    
    # Restrições de demanda
    for j in range(n):
        prob += pulp.lpSum(x[i, j] for i in range(m)) == demanda[j]
    
    # Resolver (silencioso)
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    if prob.status == pulp.LpStatusOptimal:
        return pulp.value(prob.objective), 0  # PuLP não retorna iterações facilmente
    else:
        return None, -1

# ========================================
# CVXPY
# ========================================

def resolver_cvxpy(oferta, demanda, custos):
    """Resolve usando CVXPY"""
    m = len(oferta)
    n = len(demanda)
    
    # Variáveis de decisão
    x = cp.Variable((m, n), nonneg=True)
    
    # Matriz de custos
    C = np.array(custos)
    
    # Função objetivo
    objective = cp.Minimize(cp.sum(cp.multiply(C, x)))
    
    # Restrições
    constraints = []
    
    # Restrições de oferta
    for i in range(m):
        constraints.append(cp.sum(x[i, :]) == oferta[i])
    
    # Restrições de demanda
    for j in range(n):
        constraints.append(cp.sum(x[:, j]) == demanda[j])
    
    # Resolver
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.ECOS, verbose=False)
    
    if prob.status == cp.OPTIMAL:
        return prob.value, 0
    else:
        return None, -1

# ========================================
# OR-TOOLS
# ========================================

def resolver_ortools(oferta, demanda, custos):
    """Resolve usando Google OR-Tools"""
    m = len(oferta)
    n = len(demanda)
    
    # Criar solver
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return None, -1
    
    # Variáveis de decisão
    x = {}
    for i in range(m):
        for j in range(n):
            x[i, j] = solver.NumVar(0, solver.infinity(), f'x_{i}_{j}')
    
    # Função objetivo
    objective = solver.Objective()
    for i in range(m):
        for j in range(n):
            objective.SetCoefficient(x[i, j], custos[i][j])
    objective.SetMinimization()
    
    # Restrições de oferta
    for i in range(m):
        constraint = solver.Constraint(oferta[i], oferta[i])
        for j in range(n):
            constraint.SetCoefficient(x[i, j], 1)
    
    # Restrições de demanda
    for j in range(n):
        constraint = solver.Constraint(demanda[j], demanda[j])
        for i in range(m):
            constraint.SetCoefficient(x[i, j], 1)
    
    # Resolver
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        return solver.Objective().Value(), solver.iterations()
    else:
        return None, -1

# ========================================
# BENCHMARK
# ========================================

def executar_benchmark(m, n, num_repeticoes=10):
    """Executa benchmark comparando todas as bibliotecas"""
    print(f"\n{'='*80}")
    print(f"BENCHMARK: {m}×{n} - {num_repeticoes} repetições")
    print(f"{'='*80}")
    
    resultados = {
        'tamanho': f"{m}x{n}",
        'm': m,
        'n': n,
        'num_repeticoes': num_repeticoes,
        'bibliotecas': {}
    }
    
    # Lista de bibliotecas a testar
    bibliotecas = {
        'manual': ('Implementação Manual', resolver_manual),
        'scipy': ('SciPy (linprog)', resolver_scipy),
        'pulp': ('PuLP', resolver_pulp),
        'cvxpy': ('CVXPY', resolver_cvxpy),
        'ortools': ('OR-Tools', resolver_ortools)
    }
    
    for nome_bib, (descricao, funcao_resolver) in bibliotecas.items():
        if not bibliotecas_disponiveis[nome_bib]:
            continue
        
        print(f"\n--- {descricao} ---")
        resultados['bibliotecas'][nome_bib] = {
            'nome': descricao,
            'execucoes': []
        }
        
        for i in range(num_repeticoes):
            print(f"Execução {i+1}/{num_repeticoes}...", end=" ")
            
            # Coleta de lixo
            gc.collect()
            
            processo = psutil.Process(os.getpid())
            
            # Memória antes
            try:
                mem_antes = processo.memory_info().wset / (1024 * 1024)
            except AttributeError:
                mem_antes = processo.memory_info().rss / (1024 * 1024)
            
            # Gerar problema
            oferta, demanda, custos = gerar_problema_transporte(m, n, semente=42+i)
            
            # Resolver
            try:
                tempo_inicio = time.time()
                custo, iteracoes = funcao_resolver(oferta, demanda, custos)
                tempo_total = time.time() - tempo_inicio
                
                # Memória depois
                try:
                    mem_depois = processo.memory_info().wset / (1024 * 1024)
                except AttributeError:
                    mem_depois = processo.memory_info().rss / (1024 * 1024)
                
                memoria_usada = max(0.1, mem_depois - mem_antes)
                
                if custo is not None:
                    exec_resultado = {
                        'execucao': i + 1,
                        'tempo_total': tempo_total,
                        'memoria_mb': memoria_usada,
                        'iteracoes': iteracoes if iteracoes else 0,
                        'custo_total': custo,
                        'sucesso': True
                    }
                    print(f"OK - {tempo_total:.4f}s - Custo: {custo:.2f}")
                else:
                    exec_resultado = {
                        'execucao': i + 1,
                        'tempo_total': tempo_total,
                        'memoria_mb': 0,
                        'iteracoes': 0,
                        'custo_total': 0,
                        'sucesso': False
                    }
                    print("FALHOU")
                
                resultados['bibliotecas'][nome_bib]['execucoes'].append(exec_resultado)
                
            except Exception as e:
                print(f"ERRO: {str(e)}")
                resultados['bibliotecas'][nome_bib]['execucoes'].append({
                    'execucao': i + 1,
                    'tempo_total': 0,
                    'memoria_mb': 0,
                    'iteracoes': 0,
                    'custo_total': 0,
                    'sucesso': False,
                    'erro': str(e)
                })
            
            # Limpar memória
            del oferta, demanda, custos
            gc.collect()
        
        # Calcular estatísticas
        execucoes_sucesso = [e for e in resultados['bibliotecas'][nome_bib]['execucoes'] if e['sucesso']]
        
        if execucoes_sucesso:
            tempos = [e['tempo_total'] for e in execucoes_sucesso]
            memorias = [e['memoria_mb'] for e in execucoes_sucesso]
            iteracoes_list = [e['iteracoes'] for e in execucoes_sucesso]
            
            resultados['bibliotecas'][nome_bib]['estatisticas'] = {
                'tempo_medio': statistics.mean(tempos),
                'tempo_mediano': statistics.median(tempos),
                'tempo_desvio': statistics.stdev(tempos) if len(tempos) > 1 else 0,
                'tempo_min': min(tempos),
                'tempo_max': max(tempos),
                'memoria_media': statistics.mean(memorias),
                'iteracoes_media': statistics.mean(iteracoes_list) if iteracoes_list else 0,
                'taxa_sucesso': len(execucoes_sucesso) / num_repeticoes * 100
            }
            
            print(f"\nEstatísticas {descricao}:")
            print(f"  Tempo médio: {resultados['bibliotecas'][nome_bib]['estatisticas']['tempo_medio']:.4f}s")
            print(f"  Memória média: {resultados['bibliotecas'][nome_bib]['estatisticas']['memoria_media']:.2f} MB")
            print(f"  Taxa de sucesso: {resultados['bibliotecas'][nome_bib]['estatisticas']['taxa_sucesso']:.0f}%")
    
    return resultados

# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    print("="*80)
    print("BENCHMARK COMPARATIVO: BIBLIOTECAS PYTHON PARA SIMPLEX")
    print("="*80)
    
    # Informações do sistema
    processo = psutil.Process(os.getpid())
    print(f"\nSistema Operacional: {os.name}")
    print(f"CPUs disponíveis: {psutil.cpu_count()}")
    print(f"Memória RAM total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print()
    
    # Configurações de teste
    tamanhos = [
        (50, 50),
        (60, 60),
        (70, 70),
        (80, 80),
        (90, 90),
        (100, 100)
    ]
    
    num_repeticoes = 10
    
    todos_resultados = []
    
    for m, n in tamanhos:
        resultado = executar_benchmark(m, n, num_repeticoes)
        todos_resultados.append(resultado)
    
    # Salvar resultados em JSON
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"benchmark_bibliotecas_{timestamp}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(todos_resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"Resultados salvos em: {nome_arquivo}")
    print(f"{'='*80}")
    
    # Resumo comparativo
    print("\n" + "="*80)
    print("RESUMO COMPARATIVO:")
    print("="*80)
    
    for resultado in todos_resultados:
        print(f"\n{resultado['tamanho']}:")
        print(f"{'Biblioteca':<20} {'Tempo (s)':<15} {'Memória (MB)':<15} {'Taxa Sucesso'}")
        print("-"*80)
        
        for nome_bib, dados in resultado['bibliotecas'].items():
            if 'estatisticas' in dados:
                est = dados['estatisticas']
                print(f"{dados['nome']:<20} {est['tempo_medio']:<15.4f} "
                      f"{est['memoria_media']:<15.2f} {est['taxa_sucesso']:.0f}%")
    
    print("\n" + "="*80)
    print("BENCHMARK COMPLETO!")
    print("="*80)