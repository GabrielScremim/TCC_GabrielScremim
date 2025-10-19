import random
import time
import psutil
import os
import json
import statistics
import gc

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
    ultima_linha = tabela[-1][:-1]
    valor_min = min(ultima_linha)
    if valor_min >= 0:
        return -1
    return ultima_linha.index(valor_min)

def encontrar_linha_pivo(tabela, coluna_pivo):
    """Teste da razão mínima para encontrar a linha pivô"""
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
    """Executa as operações de pivoteamento"""
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

def simplex(tabela, verbose=False, max_iteracoes=1000000):
    """Algoritmo Simplex padrão - retorna número de iterações"""
    iteracao = 0
    
    while iteracao < max_iteracoes:
        iteracao += 1
        
        coluna_pivo = encontrar_coluna_pivo(tabela)
        if coluna_pivo == -1:
            return iteracao  # Retorna número de iterações
        
        linha_pivo = encontrar_linha_pivo(tabela, coluna_pivo)
        if linha_pivo == -1:
            print("Problema ilimitado")
            return -1
        
        pivotear(tabela, linha_pivo, coluna_pivo)
    
    print(f"ATENÇÃO: Limite de {max_iteracoes} iterações atingido!")
    return iteracao

def construir_tabela_transporte(oferta, demanda, custos):
    """Constrói a tabela simplex para o problema de transporte"""
    m = len(oferta)
    n = len(demanda)
    num_vars = m * n
    
    total_oferta = sum(oferta)
    total_demanda = sum(demanda)
    if abs(total_oferta - total_demanda) > 1e-6:
        print(f"ERRO: Problema desbalanceado!")
        return None
    
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

def extrair_solucao(tabela, m, n):
    """Extrai a solução da tabela simplex final"""
    num_vars = m * n
    valores = [0.0] * num_vars
    
    for j in range(num_vars):
        coluna = [tabela[i][j] for i in range(len(tabela) - 1)]
        
        if coluna.count(1) == 1 and coluna.count(0) == len(coluna) - 1:
            linha_base = coluna.index(1)
            valores[j] = max(0, tabela[linha_base][-1])
    
    custo_total = -tabela[-1][-1]
    
    return valores, custo_total

def gerar_problema_transporte(m, n, total=100000, semente=42):
    """Gera um problema de transporte balanceado"""
    random.seed(semente)
    
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

def executar_benchmark(m, n, num_repeticoes=10):
    """Executa benchmark para um tamanho específico"""
    print(f"\n{'='*60}")
    print(f"BENCHMARK: {m}×{n} - {num_repeticoes} repetições")
    print(f"{'='*60}")
    
    resultados = {
        'tamanho': f"{m}x{n}",
        'm': m,
        'n': n,
        'num_repeticoes': num_repeticoes,
        'execucoes': []
    }
    
    for i in range(num_repeticoes):
        print(f"\nExecução {i+1}/{num_repeticoes}...", end=" ")
        
        # Forçar coleta de lixo antes de medir memória
        gc.collect()
        
        processo = psutil.Process(os.getpid())
        
        # Medir memória ANTES - usar working set (Windows) ou RSS (Linux/Mac)
        try:
            # Windows: usa working set
            mem_antes = processo.memory_info().wset / (1024 * 1024)
        except AttributeError:
            # Linux/Mac: usa RSS
            mem_antes = processo.memory_info().rss / (1024 * 1024)
        
        # Gerar problema
        tempo_inicio_total = time.time()
        oferta, demanda, custos = gerar_problema_transporte(m, n, semente=42+i)
        
        # Construir tabela
        tempo_inicio_construcao = time.time()
        tabela = construir_tabela_transporte(oferta, demanda, custos)
        tempo_construcao = time.time() - tempo_inicio_construcao
        
        # Resolver
        tempo_inicio_simplex = time.time()
        iteracoes = simplex(tabela, verbose=False)
        tempo_simplex = time.time() - tempo_inicio_simplex
        
        # Extrair solução
        valores, custo_total = extrair_solucao(tabela, m, n)
        
        tempo_total = time.time() - tempo_inicio_total
        
        # Medir memória DEPOIS
        try:
            # Windows: usa working set
            mem_depois = processo.memory_info().wset / (1024 * 1024)
        except AttributeError:
            # Linux/Mac: usa RSS
            mem_depois = processo.memory_info().rss / (1024 * 1024)
        
        # Calcular diferença - garantir que seja positiva ou zero
        memoria_usada = max(0, mem_depois - mem_antes)
        
        # Se a memória for muito pequena ou negativa, usar memória total atual
        # (acontece quando o garbage collector libera memória durante a execução)
        if memoria_usada < 0.1:
            try:
                memoria_usada = processo.memory_info().wset / (1024 * 1024)
            except AttributeError:
                memoria_usada = processo.memory_info().rss / (1024 * 1024)
        
        exec_resultado = {
            'execucao': i + 1,
            'tempo_total': tempo_total,
            'tempo_construcao': tempo_construcao,
            'tempo_simplex': tempo_simplex,
            'memoria_mb': memoria_usada,
            'memoria_antes_mb': mem_antes,
            'memoria_depois_mb': mem_depois,
            'iteracoes': iteracoes,
            'custo_total': custo_total
        }
        
        resultados['execucoes'].append(exec_resultado)
        print(f"OK - {tempo_total:.4f}s - {iteracoes} iterações - {memoria_usada:.2f} MB")
        
        # Limpar memória após cada execução
        del tabela, valores, oferta, demanda, custos
        gc.collect()
    
    # Calcular estatísticas
    tempos = [e['tempo_total'] for e in resultados['execucoes']]
    tempos_simplex = [e['tempo_simplex'] for e in resultados['execucoes']]
    memorias = [e['memoria_mb'] for e in resultados['execucoes']]
    iteracoes_list = [e['iteracoes'] for e in resultados['execucoes']]
    
    resultados['estatisticas'] = {
        'tempo_medio': statistics.mean(tempos),
        'tempo_mediano': statistics.median(tempos),
        'tempo_desvio': statistics.stdev(tempos) if len(tempos) > 1 else 0,
        'tempo_min': min(tempos),
        'tempo_max': max(tempos),
        
        'tempo_simplex_medio': statistics.mean(tempos_simplex),
        'tempo_simplex_mediano': statistics.median(tempos_simplex),
        
        'memoria_media': statistics.mean(memorias),
        'memoria_mediana': statistics.median(memorias),
        'memoria_max': max(memorias),
        'memoria_min': min(memorias),
        
        'iteracoes_media': statistics.mean(iteracoes_list),
        'iteracoes_min': min(iteracoes_list),
        'iteracoes_max': max(iteracoes_list)
    }
    
    # Mostrar resumo
    print(f"\n{'='*60}")
    print("ESTATÍSTICAS:")
    print(f"Tempo médio: {resultados['estatisticas']['tempo_medio']:.4f}s ± {resultados['estatisticas']['tempo_desvio']:.4f}s")
    print(f"Tempo Simplex médio: {resultados['estatisticas']['tempo_simplex_medio']:.4f}s")
    print(f"Memória média: {resultados['estatisticas']['memoria_media']:.2f} MB")
    print(f"Memória mediana: {resultados['estatisticas']['memoria_mediana']:.2f} MB")
    print(f"Iterações médias: {resultados['estatisticas']['iteracoes_media']:.0f}")
    print(f"{'='*60}")
    
    return resultados

# ======================
# EXECUÇÃO PRINCIPAL
# ======================

if __name__ == "__main__":
    print("="*60)
    print("BENCHMARK SIMPLEX - PYTHON (Versão Corrigida)")
    print("="*60)
    
    # Informações do sistema
    processo = psutil.Process(os.getpid())
    print(f"\nSistema Operacional: {os.name}")
    print(f"CPUs disponíveis: {psutil.cpu_count()}")
    print(f"Memória RAM total: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    
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
    nome_arquivo = f"benchmark_python_{timestamp}.json"
    
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(todos_resultados, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"Resultados salvos em: {nome_arquivo}")
    print(f"{'='*60}")
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO GERAL:")
    print("="*60)
    print(f"{'Tamanho':<12} {'Tempo Médio':<15} {'Iterações':<12} {'Memória (MB)'}")
    print("-"*60)
    for r in todos_resultados:
        print(f"{r['tamanho']:<12} {r['estatisticas']['tempo_medio']:<15.4f} "
              f"{r['estatisticas']['iteracoes_media']:<12.0f} "
              f"{r['estatisticas']['memoria_media']:.2f}")
    print("="*60)