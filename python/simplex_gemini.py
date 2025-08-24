import math

def solve_simplex_from_scratch(c, A, b, inequality_types, objective='min'):
    """
    Resolve um problema de Programação Linear usando o Método Simplex de Duas Fases, sem bibliotecas externas.

    Args:
        c (list): Coeficientes da função objetivo.
        A (list of lists): Matriz de coeficientes das restrições.
        b (list): Vetor do lado direito das restrições.
        inequality_types (list): Lista de strings ('<=', '>=', '=') para cada restrição.
        objective (str): 'min' para minimização ou 'max' para maximização.

    Returns:
        dict: Um dicionário contendo o status da solução, o valor ótimo e os valores das variáveis.
    """
    
    # --- Passo 0: Preparação Inicial ---
    
    # Se for um problema de minimização, o convertemos para maximização invertendo os sinais da função objetivo.
    # Maximizar Z é o mesmo que minimizar -Z.
    if objective == 'min':
        c = [-x for x in c]

    num_original_vars = len(c)
    num_constraints = len(A)
    
    # Rastreia os nomes das variáveis para facilitar a leitura dos resultados
    var_names = [f'x{i+1}' for i in range(num_original_vars)]
    
    slack_vars_added = 0
    artificial_vars_added = 0
    
    # Listas para guardar os índices das variáveis artificiais
    artificial_indices = []
    
    # --- Passo 1: Converter para a Forma Padrão e Criar Tableau ---
    
    # A base inicial conterá as variáveis de folga e artificiais
    basis = [0] * num_constraints
    
    # Construir a matriz aumentada (tableau)
    tableau = [([0] * num_original_vars) for _ in range(num_constraints)]
    
    for i in range(num_constraints):
        tableau[i] = A[i][:]
        
        # Adicionar variáveis de folga, excesso e artificiais
        if inequality_types[i] == '<=':
            slack_vars_added += 1
            # Adiciona uma coluna para a nova variável de folga
            for row in tableau:
                row.append(0)
            tableau[i][-1] = 1
            var_names.append(f'f{slack_vars_added}')
            basis[i] = len(var_names) - 1 # O índice da variável de folga
            
        elif inequality_types[i] == '>=':
            # Adiciona variável de excesso (surplus)
            slack_vars_added += 1
            for row in tableau:
                row.append(0)
            tableau[i][-1] = -1
            var_names.append(f's{slack_vars_added}')

            # Adiciona variável artificial
            artificial_vars_added += 1
            artificial_indices.append(len(var_names))
            for row in tableau:
                row.append(0)
            tableau[i][-1] = 1
            var_names.append(f'a{artificial_vars_added}')
            basis[i] = len(var_names) - 1 # O índice da variável artificial
            
        elif inequality_types[i] == '=':
            # Adiciona variável artificial
            artificial_vars_added += 1
            artificial_indices.append(len(var_names))
            for row in tableau:
                row.append(0)
            tableau[i][-1] = 1
            var_names.append(f'a{artificial_vars_added}')
            basis[i] = len(var_names) - 1 # O índice da variável artificial

    # Adicionar a coluna de resultados (RHS)
    for i in range(num_constraints):
        tableau[i].append(b[i])

    # --- Fase 1: Encontrar uma Solução Viável ---
    if artificial_vars_added > 0:
        # Criar a função objetivo da Fase 1: Maximizar W = - (soma das vars artificiais)
        phase1_c = [0] * (len(var_names))
        for idx in artificial_indices:
            phase1_c[idx] = -1

        # Adicionar a linha da função objetivo da Fase 1 ao tableau
        tableau.append(phase1_c + [0])
        
        # Corrigir a linha Z para a base inicial (deve ter zeros nas colunas das variáveis básicas)
        z_row_idx = len(tableau) - 1
        for i in range(num_constraints):
            if basis[i] in artificial_indices:
                pivot_row = tableau[i]
                # Z_novo = Z_velho - (coef_Z_velho * linha_pivo) -> aqui o coef é -1
                for j, val in enumerate(pivot_row):
                    tableau[z_row_idx][j] += val

        # Executar o algoritmo Simplex para a Fase 1
        while True:
            z_row = tableau[-1]
            pivot_col = -1
            # Encontrar a variável para entrar na base (maior coeficiente positivo)
            max_val = 0
            for i in range(len(z_row) - 1):
                if z_row[i] > max_val:
                    max_val = z_row[i]
                    pivot_col = i

            if pivot_col == -1:
                break # Ótimo da Fase 1 encontrado

            # Teste da razão para encontrar a variável para sair da base
            min_ratio = float('inf')
            pivot_row = -1
            for i in range(num_constraints):
                if tableau[i][pivot_col] > 1e-6: # Evitar divisão por zero ou negativo
                    ratio = tableau[i][-1] / tableau[i][pivot_col]
                    if ratio < min_ratio:
                        min_ratio = ratio
                        pivot_row = i
            
            if pivot_row == -1:
                return {"status": "inviável", "message": "Problema inviável (Fase 1)."}

            basis[pivot_row] = pivot_col # Atualiza a base

            # Pivoteamento
            pivot_element = tableau[pivot_row][pivot_col]
            for j in range(len(tableau[pivot_row])):
                tableau[pivot_row][j] /= pivot_element
            
            for i in range(len(tableau)):
                if i != pivot_row:
                    multiplier = tableau[i][pivot_col]
                    for j in range(len(tableau[i])):
                        tableau[i][j] -= multiplier * tableau[pivot_row][j]

        # Verificar se a Fase 1 foi bem-sucedida
        if abs(tableau[-1][-1]) > 1e-6:
             return {"status": "inviável", "message": f"Problema inviável. O valor ótimo da Fase 1 não é zero ({tableau[-1][-1]:.2f})."}

        # Remover a linha da função objetivo da Fase 1
        tableau.pop()
        # Remover colunas das variáveis artificiais (opcional, mas limpa o tableau)
        # Por simplicidade, vamos mantê-las mas garantir que não entrem na base novamente.
        
    # --- Fase 2: Encontrar a Solução Ótima ---
    
    # Criar a linha da função objetivo original (Z)
    c_full = c + [0] * (len(var_names) - num_original_vars)
    z_row = [-x for x in c_full] + [0] # Z - c*x = 0
    tableau.append(z_row)

    # Corrigir a linha Z para a base atual
    z_row_idx = len(tableau) - 1
    for i in range(num_constraints):
        basic_var_idx = basis[i]
        if tableau[z_row_idx][basic_var_idx] != 0:
            multiplier = tableau[z_row_idx][basic_var_idx]
            pivot_row = tableau[i]
            for j in range(len(tableau[z_row_idx])):
                tableau[z_row_idx][j] -= multiplier * pivot_row[j]

    # Executar o algoritmo Simplex para a Fase 2
    while True:
        z_row = tableau[-1]
        pivot_col = -1
        # Encontrar variável para entrar (maior coeficiente positivo, pois estamos maximizando)
        max_val = 1e-6 # Pequena tolerância
        for i in range(len(z_row) - 1):
            if z_row[i] > max_val and i not in artificial_indices:
                max_val = z_row[i]
                pivot_col = i

        if pivot_col == -1:
            break # Solução ótima encontrada

        # Teste da razão
        min_ratio = float('inf')
        pivot_row = -1
        for i in range(num_constraints):
            if tableau[i][pivot_col] > 1e-6:
                ratio = tableau[i][-1] / tableau[i][pivot_col]
                if ratio < min_ratio:
                    min_ratio = ratio
                    pivot_row = i
        
        if pivot_row == -1:
            return {"status": "ilimitado", "message": "O problema é ilimitado."}

        basis[pivot_row] = pivot_col

        # Pivoteamento
        pivot_element = tableau[pivot_row][pivot_col]
        for j in range(len(tableau[pivot_row])):
            tableau[pivot_row][j] /= pivot_element
        
        for i in range(len(tableau)):
            if i != pivot_row:
                multiplier = tableau[i][pivot_col]
                for j in range(len(tableau[i])):
                    tableau[i][j] -= multiplier * tableau[pivot_row][j]

    # --- Passo 5: Extrair e Apresentar a Solução ---
    solution = [0] * num_original_vars
    for i in range(num_constraints):
        if basis[i] < num_original_vars:
            solution[basis[i]] = tableau[i][-1]
    
    optimal_value = tableau[-1][-1]
    if objective == 'min':
        optimal_value *= -1 # Desfazer a conversão inicial

    return {
        "status": "ótima",
        "valor_otimo": optimal_value,
        "variaveis": {var_names[i]: val for i, val in enumerate(solution)}
    }


# --- DADOS DO SEU PROBLEMA DE TRANSPORTE ---

# Coeficientes da função objetivo (custos)
# Ordem: xA1, xA2, xA3, xB1, xB2, xB3, xC1, xC2, xC3
c = [4, 7, 6, 5, 5, 5, 9, 5, 8]

# Matriz de coeficientes das restrições (A)
A = [
    # Restrições de Oferta (Fornecedores)
    [1, 1, 1, 0, 0, 0, 0, 0, 0],  # Fornecedor A
    [0, 0, 0, 1, 1, 1, 0, 0, 0],  # Fornecedor B
    [0, 0, 0, 0, 0, 0, 1, 1, 1],  # Fornecedor C
    # Restrições de Demanda (Plantas)
    [1, 0, 0, 1, 0, 0, 1, 0, 0],  # Planta 1
    [0, 1, 0, 0, 1, 0, 0, 1, 0],  # Planta 2
    [0, 0, 1, 0, 0, 1, 0, 0, 1]   # Planta 3
]

# Vetor de resultados das restrições (b)
b = [400, 700, 500, 600, 500, 300]

# Tipos de inequação para cada restrição
inequality_types = ['<=', '<=', '<=', '=', '=', '=']

# Objetivo do problema
objective = 'min'

# --- RESOLVER O PROBLEMA ---
resultado = solve_simplex_from_scratch(c, A, b, inequality_types, objective)

# --- APRESENTAR OS RESULTADOS ---
print(f"Status da Solução: {resultado['status']}")
if resultado['status'] == 'ótima':
    print(f"Custo Mínimo Total: ${resultado['valor_otimo']:.2f}")
    print("\nPlano de Transporte Ótimo:")
    variaveis = resultado['variaveis']
    # Renomeando para ficar igual ao problema original
    nomes_bonitos = {
        'x1': 'A -> 1', 'x2': 'A -> 2', 'x3': 'A -> 3',
        'x4': 'B -> 1', 'x5': 'B -> 2', 'x6': 'B -> 3',
        'x7': 'C -> 1', 'x8': 'C -> 2', 'x9': 'C -> 3',
    }
    for var, val in variaveis.items():
        if val > 1e-6: # Mostrar apenas as rotas utilizadas
            print(f"  - Enviar {val:.0f} toneladas de {nomes_bonitos[var]}")