# Implementação simples do método Simplex (M-grande) em Python puro
# Gabriel Scremim pode usar tanto para transporte quanto outros LPs pequenos

def simplex(c, A, b, maxiter=1000, M=10000):
    """
    Resolve min c^T x, sujeito a A x = b, x >= 0
    usando método Simplex padrão (com artificiais via M-grande já embutidos em c).
    
    c: lista de custos (já ajustados com M-grande se houver artificiais)
    A: matriz (lista de listas) das restrições
    b: lado direito
    """

    m = len(A)   # número de restrições
    n = len(A[0])  # número de variáveis
    
    # Base inicial: últimas m colunas (variáveis artificiais, identidade)
    base = list(range(n - m, n))
    nao_base = list(range(n - m))

    # matriz aumentada (cópia)
    A = [linha[:] for linha in A]
    b = b[:]
    c = c[:]

    for it in range(maxiter):
        # Calcula custos básicos
        cb = [c[j] for j in base]
        cn = [c[j] for j in nao_base]

        # Calcula solução básica (x_B = b)
        xB = b[:]

        # Calcula custo reduzido das não básicas: cn - cb * B^-1 * N
        # Aqui B = identidade (pois sempre pivotamos)
        # Então precisamos realmente manter a base atualizada
        # Implementação "na mão": resolver sistema para u^T
        # u^T * A_B = c_B^T
        # mas como mantemos B explícito, resolvemos via eliminação gaussiana simples

        # montar A_B
        AB = [[A[i][j] for j in base] for i in range(m)]
        # resolver u^T * AB = cb^T
        u = gauss_solve_transpose(AB, cb)

        # calcular custo reduzido
        reduzidos = []
        for j in nao_base:
            soma = sum(u[i]*A[i][j] for i in range(m))
            reduzidos.append(c[j] - soma)

        # condição de otimalidade
        if all(r >= 0 for r in reduzidos):
            # solução ótima
            x = [0]*n
            for i, bi in enumerate(base):
                x[bi] = xB[i]
            valor = sum(c[i]*x[i] for i in range(n) if c[i] < M)  # não conta M artificiais
            return x, valor

        # entra: índice com custo reduzido mais negativo
        j_in = nao_base[reduzidos.index(min(reduzidos))]

        # direções: dB = -B^-1 * A[:, j_in]
        col = [A[i][j_in] for i in range(m)]
        dB = gauss_solve(AB, col)

        # ratio test
        ratios = []
        for i in range(m):
            if dB[i] > 1e-9:
                ratios.append(xB[i]/dB[i])
            else:
                ratios.append(float('inf'))
        if all(r == float('inf') for r in ratios):
            raise Exception("Problema ilimitado!")

        i_out = ratios.index(min(ratios))

        # pivoteia: variável base sai, entra
        base[i_out], j_in = j_in, base[i_out]
        nao_base = [j for j in range(n) if j not in base]

        # atualizar b com pivoteamento (Gauss-Jordan)
        piv = dB[i_out]
        xB = [xB[k] - dB[k]*ratios[i_out] for k in range(m)]
        xB[i_out] = ratios[i_out]

    raise Exception("Iterações excedidas!")


def gauss_solve(A, b):
    """Resolve Ax = b via eliminação de Gauss, retorna x"""
    m = len(A)
    M = [A[i][:] + [b[i]] for i in range(m)]
    n = len(M[0])

    # forward elimination
    for k in range(m):
        # pivot
        if abs(M[k][k]) < 1e-12:
            for i in range(k+1, m):
                if abs(M[i][k]) > 1e-12:
                    M[k], M[i] = M[i], M[k]
                    break
        piv = M[k][k]
        for j in range(k, n):
            M[k][j] /= piv
        for i in range(k+1, m):
            f = M[i][k]
            for j in range(k, n):
                M[i][j] -= f*M[k][j]

    # back substitution
    x = [0]*m
    for i in range(m-1, -1, -1):
        x[i] = M[i][n-1] - sum(M[i][j]*x[j] for j in range(i+1,m))
    return x

def gauss_solve_transpose(A, c):
    """Resolve u^T * A = c^T, ou seja, A^T u = c"""
    m = len(A)
    n = len(A[0])
    AT = [[A[j][i] for j in range(m)] for i in range(n)]
    return gauss_solve(AT, c)


# --------------------------
# EXEMPLO: problema de transporte da imagem
# Fornecedores: A<=400, B<=700, C<=500
# Plantas: P1=600, P2=500, P3=300
# Custos conforme figura
# --------------------------

c = [4,7,6, 5,5,5, 9,5,8]  # custos variáveis reais (9 variáveis x_ij)
# vamos adicionar 3 folgas (oferta), 3 artificiais (demanda)
c += [0,0,0]  # folgas
c += [10000,10000,10000]  # artificiais com M-grande

# Matriz A
A = []
b = []

# oferta A: xA1+xA2+xA3+sA=400
A.append([1,1,1, 0,0,0, 0,0,0, 1,0,0, 0,0,0])
b.append(400)

# oferta B
A.append([0,0,0, 1,1,1, 0,0,0, 0,1,0, 0,0,0])
b.append(700)

# oferta C
A.append([0,0,0, 0,0,0, 1,1,1, 0,0,1, 0,0,0])
b.append(500)

# demanda P1
A.append([1,0,0, 1,0,0, 1,0,0, 0,0,0, 1,0,0])
b.append(600)

# demanda P2
A.append([0,1,0, 0,1,0, 0,1,0, 0,0,0, 0,1,0])
b.append(500)

# demanda P3
A.append([0,0,1, 0,0,1, 0,0,1, 0,0,0, 0,0,1])
b.append(300)

# Resolver
x, valor = simplex(c, A, b)

print("Solução ótima:")
for i, val in enumerate(x[:9]):  # apenas as 9 variáveis de transporte
    print(f"x{i+1} = {val}")
print("Custo mínimo =", valor)
