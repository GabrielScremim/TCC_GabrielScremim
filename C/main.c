#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <time.h>
#include <windows.h>
#include <psapi.h>

// Função para mostrar a tabela simplex
void mostrar_tabela(double **tabela, int linhas, int colunas) {
    printf("\nTabela Simplex:\n");
    for (int i = 0; i < linhas; i++) {
        for (int j = 0; j < colunas; j++) {
            printf("%+8.2f ", tabela[i][j]);
        }
        printf("\n");
    }
    printf("\n");
}

// Encontrar a coluna pivô (menor valor na última linha)
int encontrar_coluna_pivo(double **tabela, int colunas) {
    double valor_min = 0;
    int coluna_pivo = -1;

    for (int j = 0; j < colunas - 1; j++) {
        if (tabela[tabela != NULL ? 0 : 0][j] < valor_min) { // Assumindo que a última linha é a linha 0 para função objetivo
            valor_min = tabela[tabela != NULL ? 0 : 0][j];
            coluna_pivo = j;
        }
    }
    return coluna_pivo;
}

// Versão corrigida da função encontrar_coluna_pivo
int encontrar_coluna_pivo_correto(double **tabela, int linhas, int colunas) {
    double valor_min = 0;
    int coluna_pivo = -1;

    // A última linha contém os coeficientes da função objetivo
    for (int j = 0; j < colunas - 1; j++) {
        if (tabela[linhas - 1][j] < valor_min) {
            valor_min = tabela[linhas - 1][j];
            coluna_pivo = j;
        }
    }
    return coluna_pivo;
}

// Encontrar a linha pivô usando o teste da razão
int encontrar_linha_pivo(double **tabela, int linhas, int coluna_pivo) {
    double menor = DBL_MAX;
    int linha_pivo = -1;

    for (int i = 0; i < linhas - 1; i++) { // Não incluir a linha da função objetivo
        double elemento = tabela[i][coluna_pivo];
        if (elemento > 0) {
            double razao = tabela[i][tabela[0] != NULL ? 0 : 0] / elemento; // Assumindo última coluna
            if (razao < menor) {
                menor = razao;
                linha_pivo = i;
            }
        }
    }
    return linha_pivo;
}

// Versão corrigida da função encontrar_linha_pivo
int encontrar_linha_pivo_correto(double **tabela, int linhas, int colunas, int coluna_pivo) {
    double menor = DBL_MAX;
    int linha_pivo = -1;

    for (int i = 0; i < linhas - 1; i++) { // Não incluir a linha da função objetivo
        double elemento = tabela[i][coluna_pivo];
        if (elemento > 0) {
            double razao = tabela[i][colunas - 1] / elemento; // Última coluna (RHS)
            if (razao < menor) {
                menor = razao;
                linha_pivo = i;
            }
        }
    }
    return linha_pivo;
}

// Realizar a operação de pivoteamento
void pivotear(double **tabela, int linhas, int colunas, int linha_pivo, int coluna_pivo) {
    double pivo = tabela[linha_pivo][coluna_pivo];

    // Normalizar a linha pivô
    for (int j = 0; j < colunas; j++) {
        tabela[linha_pivo][j] /= pivo;
    }

    // Eliminar outros elementos da coluna pivô
    for (int i = 0; i < linhas; i++) {
        if (i != linha_pivo) {
            double multiplicador = tabela[i][coluna_pivo];
            for (int j = 0; j < colunas; j++) {
                tabela[i][j] -= multiplicador * tabela[linha_pivo][j];
            }
        }
    }
}

// Algoritmo Simplex principal
double** simplex(double **tabela, int linhas, int colunas, int verbose) {
    while (1) {
        if (verbose) {
            mostrar_tabela(tabela, linhas, colunas);
        }

        int coluna_pivo = encontrar_coluna_pivo_correto(tabela, linhas, colunas);
        if (coluna_pivo == -1) {
            printf("Solução ótima encontrada.\n");
            break;
        }

        int linha_pivo = encontrar_linha_pivo_correto(tabela, linhas, colunas, coluna_pivo);
        if (linha_pivo == -1) {
            printf("Problema ilimitado.\n");
            break;
        }

        if (verbose) {
            printf("Pivoteando na linha %d, coluna %d\n", linha_pivo + 1, coluna_pivo + 1);
        }

        pivotear(tabela, linhas, colunas, linha_pivo, coluna_pivo);
    }
    return tabela;
}

// Alocar matriz 2D
double** alocar_matriz(int linhas, int colunas) {
    double **matriz = (double**)malloc(linhas * sizeof(double*));
    for (int i = 0; i < linhas; i++) {
        matriz[i] = (double*)calloc(colunas, sizeof(double));
    }
    return matriz;
}

// Liberar matriz 2D
void liberar_matriz(double **matriz, int linhas) {
    for (int i = 0; i < linhas; i++) {
        free(matriz[i]);
    }
    free(matriz);
}

// Construir tabela simplex para problema de transporte
double** construir_tabela_transporte(int *oferta, int *demanda, int **custos, int m, int n, int *linhas_ret, int *colunas_ret) {
    int num_vars = m * n;
    int total_linhas = m + n + 1; // restrições de oferta + demanda + função objetivo
    int total_colunas = num_vars + m + n + 1; // variáveis + folgas + RHS

    *linhas_ret = total_linhas;
    *colunas_ret = total_colunas;

    double **tabela = alocar_matriz(total_linhas, total_colunas);

    // Restrições de oferta
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            tabela[i][i * n + j] = 1;
        }
        tabela[i][num_vars + i] = 1; // variável de folga
        tabela[i][total_colunas - 1] = oferta[i]; // RHS
    }

    // Restrições de demanda
    for (int j = 0; j < n; j++) {
        for (int i = 0; i < m; i++) {
            tabela[m + j][i * n + j] = 1;
        }
        tabela[m + j][num_vars + m + j] = 1; // variável de folga
        tabela[m + j][total_colunas - 1] = demanda[j]; // RHS
    }

    // Função objetivo (minimizar → max -Z)
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            tabela[total_linhas - 1][i * n + j] = -custos[i][j];
        }
    }

    return tabela;
}

// Extrair solução da tabela final
void extrair_solucao(double **tabela, int linhas, int colunas, int m, int n, double **valores_ret, double *custo_total_ret) {
    int num_vars = m * n;
    double *valores = (double*)calloc(num_vars, sizeof(double));

    for (int j = 0; j < num_vars; j++) {
        int count_one = 0, count_zero = 0, linha_base = -1;

        for (int i = 0; i < linhas; i++) {
            if (tabela[i][j] == 1.0) {
                count_one++;
                linha_base = i;
            } else if (tabela[i][j] == 0.0) {
                count_zero++;
            }
        }

        if (count_one == 1 && count_zero == linhas - 1) {
            valores[j] = tabela[linha_base][colunas - 1];
        }
    }

    *valores_ret = valores;
    *custo_total_ret = -tabela[linhas - 1][colunas - 1]; // Negar porque maximizamos -Z
}

// Gerar problema de transporte grande
void gerar_problema_transporte_grande(int m, int n, int **oferta_ret, int **demanda_ret, int ***custos_ret) {
    int total = 100000;

    int *oferta = (int*)malloc(m * sizeof(int));
    int *demanda = (int*)malloc(n * sizeof(int));
    int **custos = (int**)malloc(m * sizeof(int*));

    srand(42); // Seed fixo para reproduzibilidade

    // Gerar oferta
    int soma_oferta = 0;
    for (int i = 0; i < m; i++) {
        oferta[i] = rand() % 3000 + 1000; // Entre 1000 e 4000
        soma_oferta += oferta[i];
    }

    // Escalar oferta para totalizar 'total'
    double escala = (double)total / soma_oferta;
    soma_oferta = 0;
    for (int i = 0; i < m; i++) {
        oferta[i] = (int)(oferta[i] * escala);
        soma_oferta += oferta[i];
    }
    oferta[m - 1] += total - soma_oferta;

    // Gerar demanda
    int soma_demanda = 0;
    for (int j = 0; j < n; j++) {
        demanda[j] = rand() % 3000 + 1000; // Entre 1000 e 4000
        soma_demanda += demanda[j];
    }

    // Escalar demanda para totalizar 'total'
    escala = (double)total / soma_demanda;
    soma_demanda = 0;
    for (int j = 0; j < n; j++) {
        demanda[j] = (int)(demanda[j] * escala);
        soma_demanda += demanda[j];
    }
    demanda[n - 1] += total - soma_demanda;

    // Gerar custos
    for (int i = 0; i < m; i++) {
        custos[i] = (int*)malloc(n * sizeof(int));
        for (int j = 0; j < n; j++) {
            custos[i][j] = rand() % 100 + 1; // Entre 1 e 100
        }
    }

    *oferta_ret = oferta;
    *demanda_ret = demanda;
    *custos_ret = custos;
}

// Função principal
size_t memoria_usada_MB() {
    PROCESS_MEMORY_COUNTERS pmc;
    if (GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        return pmc.PeakWorkingSetSize / (1024 * 1024); // retorna em MB
    }
    return 0;
}

// ======================
// Função principal
// ======================
int main() {
    int m = 20;  // número de fontes
    int n = 20;  // número de destinos

    printf("Gerando problema de transporte %dx%d...\n", m, n);

    clock_t inicio = clock();

    int *oferta, *demanda, **custos;
    gerar_problema_transporte_grande(m, n, &oferta, &demanda, &custos);

    int linhas, colunas;
    double **tabela = construir_tabela_transporte(oferta, demanda, custos, m, n, &linhas, &colunas);

    double **tabela_final = simplex(tabela, linhas, colunas, 0);

    double *valores, custo_total;
    extrair_solucao(tabela_final, linhas, colunas, m, n, &valores, &custo_total);

    clock_t fim = clock();
    double tempo_exec = (double)(fim - inicio) / CLOCKS_PER_SEC;

    printf("\n--- MÉTRICAS C (Windows) ---\n");
    printf("Tempo de execução: %.4f segundos\n", tempo_exec);
    printf("Memória máxima usada: %zu MB\n", memoria_usada_MB());

    printf("\nCusto total mínimo: %.2f\n", custo_total);

    // Liberar memória
    liberar_matriz(tabela_final, linhas);
    free(valores);
    free(oferta);
    free(demanda);
    for (int i = 0; i < m; i++) {
        free(custos[i]);
    }
    free(custos);

    return 0;
}