#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <time.h>
#include <math.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <unistd.h>
#include <string.h>
#include <limits.h>

typedef struct {
    int m;
    int n;
    int execucao;
    double tempo_total;
    double tempo_construcao;
    double tempo_simplex;
    double memoria_mb;
    int iteracoes;
    double custo_total;
} ResultadoExecucao;

typedef struct {
    char tamanho[20];
    int m;
    int n;
    int num_repeticoes;
    ResultadoExecucao *execucoes;
    double tempo_medio;
    double tempo_mediano;
    double tempo_desvio;
    double tempo_min;
    double tempo_max;
    double tempo_simplex_medio;
    double memoria_media;
    double memoria_max;
    double iteracoes_media;
    int iteracoes_min;
    int iteracoes_max;
} ResultadoBenchmark;

// Função para obter tempo em segundos com alta precisão
double obter_tempo() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

// Função para obter memória usada em MB
double memoria_usada_MB() {
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    // No Linux, ru_maxrss está em kilobytes
    return usage.ru_maxrss / 1024.0;
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

// Encontrar coluna pivô
int encontrar_coluna_pivo(double **tabela, int linhas, int colunas) {
    double valor_min = 0;
    int coluna_pivo = -1;
    
    for (int j = 0; j < colunas - 1; j++) {
        if (tabela[linhas - 1][j] < valor_min) {
            valor_min = tabela[linhas - 1][j];
            coluna_pivo = j;
        }
    }
    return coluna_pivo;
}

// Encontrar linha pivô
int encontrar_linha_pivo(double **tabela, int linhas, int colunas, int coluna_pivo) {
    double menor = DBL_MAX;
    int linha_pivo = -1;
    
    for (int i = 0; i < linhas - 1; i++) {
        double elemento = tabela[i][coluna_pivo];
        if (elemento > 0) {
            double razao = tabela[i][colunas - 1] / elemento;
            if (razao < menor) {
                menor = razao;
                linha_pivo = i;
            }
        }
    }
    return linha_pivo;
}

// Pivotear
void pivotear(double **tabela, int linhas, int colunas, int linha_pivo, int coluna_pivo) {
    double pivo = tabela[linha_pivo][coluna_pivo];
    
    for (int j = 0; j < colunas; j++) {
        tabela[linha_pivo][j] /= pivo;
    }
    
    for (int i = 0; i < linhas; i++) {
        if (i != linha_pivo) {
            double multiplicador = tabela[i][coluna_pivo];
            for (int j = 0; j < colunas; j++) {
                tabela[i][j] -= multiplicador * tabela[linha_pivo][j];
            }
        }
    }
}

// Algoritmo Simplex - retorna número de iterações
int simplex(double **tabela, int linhas, int colunas, int max_iter) {
    int iteracao = 0;
    
    while (iteracao < max_iter) {
        iteracao++;
        
        int coluna_pivo = encontrar_coluna_pivo(tabela, linhas, colunas);
        if (coluna_pivo == -1) {
            return iteracao;
        }
        
        int linha_pivo = encontrar_linha_pivo(tabela, linhas, colunas, coluna_pivo);
        if (linha_pivo == -1) {
            printf("Problema ilimitado.\n");
            return -1;
        }
        
        pivotear(tabela, linhas, colunas, linha_pivo, coluna_pivo);
    }
    
    printf("ATENÇÃO: Limite de %d iterações atingido!\n", max_iter);
    return iteracao;
}

// Construir tabela simplex
double** construir_tabela_transporte(int *oferta, int *demanda, int **custos, 
                                     int m, int n, int *linhas_ret, int *colunas_ret) {
    int num_vars = m * n;
    int total_linhas = m + n + 1;
    int total_colunas = num_vars + m + n + 1;
    
    *linhas_ret = total_linhas;
    *colunas_ret = total_colunas;
    
    double **tabela = alocar_matriz(total_linhas, total_colunas);
    
    // Restrições de oferta
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            tabela[i][i * n + j] = 1;
        }
        tabela[i][num_vars + i] = 1;
        tabela[i][total_colunas - 1] = oferta[i];
    }
    
    // Restrições de demanda
    for (int j = 0; j < n; j++) {
        for (int i = 0; i < m; i++) {
            tabela[m + j][i * n + j] = 1;
        }
        tabela[m + j][num_vars + m + j] = 1;
        tabela[m + j][total_colunas - 1] = demanda[j];
    }
    
    // Função objetivo
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < n; j++) {
            tabela[total_linhas - 1][i * n + j] = -custos[i][j];
        }
    }
    
    return tabela;
}

// Extrair solução
double extrair_solucao(double **tabela, int linhas, int colunas, int m, int n) {
    return -tabela[linhas - 1][colunas - 1];
}

// Gerar problema de transporte
void gerar_problema_transporte(int m, int n, int **oferta_ret, int **demanda_ret, 
                               int ***custos_ret, int semente) {
    int total = 100000;
    
    int *oferta = (int*)malloc(m * sizeof(int));
    int *demanda = (int*)malloc(n * sizeof(int));
    int **custos = (int**)malloc(m * sizeof(int*));
    
    srand(semente);
    
    // Gerar oferta
    int soma_oferta = 0;
    for (int i = 0; i < m; i++) {
        oferta[i] = rand() % 3000 + 1000;
        soma_oferta += oferta[i];
    }
    
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
        demanda[j] = rand() % 3000 + 1000;
        soma_demanda += demanda[j];
    }
    
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
            custos[i][j] = rand() % 100 + 1;
        }
    }
    
    *oferta_ret = oferta;
    *demanda_ret = demanda;
    *custos_ret = custos;
}

// Função de comparação para qsort
int comparar_double(const void *a, const void *b) {
    double diff = *(double*)a - *(double*)b;
    return (diff > 0) - (diff < 0);
}

// Calcular estatísticas
void calcular_estatisticas(ResultadoBenchmark *resultado) {
    int n = resultado->num_repeticoes;
    
    double soma_tempo = 0, soma_tempo_simplex = 0, soma_memoria = 0;
    double soma_iteracoes = 0;
    
    double *tempos = (double*)malloc(n * sizeof(double));
    
    resultado->tempo_min = DBL_MAX;
    resultado->tempo_max = 0;
    resultado->iteracoes_min = INT_MAX;
    resultado->iteracoes_max = 0;
    resultado->memoria_max = 0;
    
    for (int i = 0; i < n; i++) {
        ResultadoExecucao *exec = &resultado->execucoes[i];
        
        tempos[i] = exec->tempo_total;
        soma_tempo += exec->tempo_total;
        soma_tempo_simplex += exec->tempo_simplex;
        soma_memoria += exec->memoria_mb;
        soma_iteracoes += exec->iteracoes;
        
        if (exec->tempo_total < resultado->tempo_min) resultado->tempo_min = exec->tempo_total;
        if (exec->tempo_total > resultado->tempo_max) resultado->tempo_max = exec->tempo_total;
        if (exec->iteracoes < resultado->iteracoes_min) resultado->iteracoes_min = exec->iteracoes;
        if (exec->iteracoes > resultado->iteracoes_max) resultado->iteracoes_max = exec->iteracoes;
        if (exec->memoria_mb > resultado->memoria_max) resultado->memoria_max = exec->memoria_mb;
    }
    
    resultado->tempo_medio = soma_tempo / n;
    resultado->tempo_simplex_medio = soma_tempo_simplex / n;
    resultado->memoria_media = soma_memoria / n;
    resultado->iteracoes_media = soma_iteracoes / n;
    
    // Calcular mediana
    qsort(tempos, n, sizeof(double), comparar_double);
    if (n % 2 == 0) {
        resultado->tempo_mediano = (tempos[n/2-1] + tempos[n/2]) / 2.0;
    } else {
        resultado->tempo_mediano = tempos[n/2];
    }
    
    // Calcular desvio padrão
    double soma_quad = 0;
    for (int i = 0; i < n; i++) {
        double diff = resultado->execucoes[i].tempo_total - resultado->tempo_medio;
        soma_quad += diff * diff;
    }
    resultado->tempo_desvio = sqrt(soma_quad / n);
    
    free(tempos);
}

// Executar benchmark
ResultadoBenchmark executar_benchmark(int m, int n, int num_repeticoes) {
    printf("\n============================================================\n");
    printf("BENCHMARK: %dx%d - %d repeticoes\n", m, n, num_repeticoes);
    printf("============================================================\n");
    
    ResultadoBenchmark resultado;
    sprintf(resultado.tamanho, "%dx%d", m, n);
    resultado.m = m;
    resultado.n = n;
    resultado.num_repeticoes = num_repeticoes;
    resultado.execucoes = (ResultadoExecucao*)malloc(num_repeticoes * sizeof(ResultadoExecucao));
    
    for (int i = 0; i < num_repeticoes; i++) {
        printf("\nExecucao %d/%d... ", i+1, num_repeticoes);
        fflush(stdout);
        
        double mem_antes = memoria_usada_MB();
        double inicio_total = obter_tempo();
        
        // Gerar problema
        int *oferta, *demanda, **custos;
        gerar_problema_transporte(m, n, &oferta, &demanda, &custos, 42 + i);
        
        // Construir tabela
        double inicio_construcao = obter_tempo();
        int linhas, colunas;
        double **tabela = construir_tabela_transporte(oferta, demanda, custos, m, n, &linhas, &colunas);
        double fim_construcao = obter_tempo();
        
        // Resolver
        double inicio_simplex = obter_tempo();
        int iteracoes = simplex(tabela, linhas, colunas, 1000000);
        double fim_simplex = obter_tempo();
        
        // Extrair solução
        double custo_total = extrair_solucao(tabela, linhas, colunas, m, n);
        
        double fim_total = obter_tempo();
        double mem_depois = memoria_usada_MB();
        
        // Salvar resultados
        ResultadoExecucao *exec = &resultado.execucoes[i];
        exec->m = m;
        exec->n = n;
        exec->execucao = i + 1;
        exec->tempo_total = fim_total - inicio_total;
        exec->tempo_construcao = fim_construcao - inicio_construcao;
        exec->tempo_simplex = fim_simplex - inicio_simplex;
        exec->memoria_mb = mem_depois - mem_antes;
        exec->iteracoes = iteracoes;
        exec->custo_total = custo_total;
        
        printf("OK - %.4fs - %d iteracoes", exec->tempo_total, iteracoes);
        
        // Liberar memória
        liberar_matriz(tabela, linhas);
        free(oferta);
        free(demanda);
        for (int j = 0; j < m; j++) {
            free(custos[j]);
        }
        free(custos);
    }
    
    // Calcular estatísticas
    calcular_estatisticas(&resultado);
    
    // Mostrar resumo
    printf("\n============================================================\n");
    printf("ESTATISTICAS:\n");
    printf("Tempo medio: %.4fs +/- %.4fs\n", resultado.tempo_medio, resultado.tempo_desvio);
    printf("Tempo Simplex medio: %.4fs\n", resultado.tempo_simplex_medio);
    printf("Memoria media: %.2f MB\n", resultado.memoria_media);
    printf("Iteracoes medias: %.0f\n", resultado.iteracoes_media);
    printf("============================================================\n");
    
    return resultado;
}

// Salvar resultados em arquivo JSON
void salvar_resultados_json(ResultadoBenchmark *resultados, int num_testes, const char *nome_arquivo) {
    FILE *fp = fopen(nome_arquivo, "w");
    if (fp == NULL) {
        printf("Erro ao criar arquivo JSON!\n");
        return;
    }
    
    fprintf(fp, "[\n");
    
    for (int t = 0; t < num_testes; t++) {
        ResultadoBenchmark *r = &resultados[t];
        
        fprintf(fp, "  {\n");
        fprintf(fp, "    \"tamanho\": \"%s\",\n", r->tamanho);
        fprintf(fp, "    \"m\": %d,\n", r->m);
        fprintf(fp, "    \"n\": %d,\n", r->n);
        fprintf(fp, "    \"num_repeticoes\": %d,\n", r->num_repeticoes);
        fprintf(fp, "    \"execucoes\": [\n");
        
        for (int i = 0; i < r->num_repeticoes; i++) {
            ResultadoExecucao *e = &r->execucoes[i];
            fprintf(fp, "      {\n");
            fprintf(fp, "        \"execucao\": %d,\n", e->execucao);
            fprintf(fp, "        \"tempo_total\": %.6f,\n", e->tempo_total);
            fprintf(fp, "        \"tempo_construcao\": %.6f,\n", e->tempo_construcao);
            fprintf(fp, "        \"tempo_simplex\": %.6f,\n", e->tempo_simplex);
            fprintf(fp, "        \"memoria_mb\": %.2f,\n", e->memoria_mb);
            fprintf(fp, "        \"iteracoes\": %d,\n", e->iteracoes);
            fprintf(fp, "        \"custo_total\": %.2f\n", e->custo_total);
            fprintf(fp, "      }%s\n", (i < r->num_repeticoes - 1) ? "," : "");
        }
        
        fprintf(fp, "    ],\n");
        fprintf(fp, "    \"estatisticas\": {\n");
        fprintf(fp, "      \"tempo_medio\": %.6f,\n", r->tempo_medio);
        fprintf(fp, "      \"tempo_mediano\": %.6f,\n", r->tempo_mediano);
        fprintf(fp, "      \"tempo_desvio\": %.6f,\n", r->tempo_desvio);
        fprintf(fp, "      \"tempo_min\": %.6f,\n", r->tempo_min);
        fprintf(fp, "      \"tempo_max\": %.6f,\n", r->tempo_max);
        fprintf(fp, "      \"tempo_simplex_medio\": %.6f,\n", r->tempo_simplex_medio);
        fprintf(fp, "      \"memoria_media\": %.2f,\n", r->memoria_media);
        fprintf(fp, "      \"memoria_max\": %.2f,\n", r->memoria_max);
        fprintf(fp, "      \"iteracoes_media\": %.0f,\n", r->iteracoes_media);
        fprintf(fp, "      \"iteracoes_min\": %d,\n", r->iteracoes_min);
        fprintf(fp, "      \"iteracoes_max\": %d\n", r->iteracoes_max);
        fprintf(fp, "    }\n");
        fprintf(fp, "  }%s\n", (t < num_testes - 1) ? "," : "");
    }
    
    fprintf(fp, "]\n");
    fclose(fp);
    
    printf("\nResultados salvos em: %s\n", nome_arquivo);
}

// Salvar resultados em CSV
void salvar_resultados_csv(ResultadoBenchmark *resultados, int num_testes, const char *nome_arquivo) {
    FILE *fp = fopen(nome_arquivo, "w");
    if (fp == NULL) {
        printf("Erro ao criar arquivo CSV!\n");
        return;
    }
    
    // Cabeçalho
    fprintf(fp, "Tamanho,M,N,Execucao,Tempo_Total,Tempo_Construcao,Tempo_Simplex,Memoria_MB,Iteracoes,Custo_Total\n");
    
    // Dados
    for (int t = 0; t < num_testes; t++) {
        ResultadoBenchmark *r = &resultados[t];
        for (int i = 0; i < r->num_repeticoes; i++) {
            ResultadoExecucao *e = &r->execucoes[i];
            fprintf(fp, "%s,%d,%d,%d,%.6f,%.6f,%.6f,%.2f,%d,%.2f\n",
                    r->tamanho, r->m, r->n, e->execucao,
                    e->tempo_total, e->tempo_construcao, e->tempo_simplex,
                    e->memoria_mb, e->iteracoes, e->custo_total);
        }
    }
    
    fclose(fp);
    printf("Resultados salvos em: %s\n", nome_arquivo);
}

// ======================
// FUNÇÃO PRINCIPAL
// ======================
int main() {
    printf("============================================================\n");
    printf("BENCHMARK SIMPLEX - LINUX\n");
    printf("============================================================\n");
    
    // Configurações de teste
    int tamanhos[][2] = {
        {5, 5},
        {10, 10},
        {15, 15},
        {20, 20},
        {25, 25},
        {30, 30}
    };
    
    int num_testes = sizeof(tamanhos) / sizeof(tamanhos[0]);
    int num_repeticoes = 10;
    
    ResultadoBenchmark *todos_resultados = (ResultadoBenchmark*)malloc(num_testes * sizeof(ResultadoBenchmark));
    
    // Executar todos os benchmarks
    for (int i = 0; i < num_testes; i++) {
        todos_resultados[i] = executar_benchmark(tamanhos[i][0], tamanhos[i][1], num_repeticoes);
    }
    
    // Gerar nome de arquivo com timestamp
    time_t t = time(NULL);
    struct tm *tm_info = localtime(&t);
    char timestamp[20];
    strftime(timestamp, sizeof(timestamp), "%Y%m%d_%H%M%S", tm_info);
    
    char nome_json[100], nome_csv[100];
    sprintf(nome_json, "benchmark_linux_%s.json", timestamp);
    sprintf(nome_csv, "benchmark_linux_%s.csv", timestamp);
    
    // Salvar resultados
    salvar_resultados_json(todos_resultados, num_testes, nome_json);
    salvar_resultados_csv(todos_resultados, num_testes, nome_csv);
    
    // Resumo final
    printf("\n============================================================\n");
    printf("RESUMO GERAL:\n");
    printf("============================================================\n");
    printf("%-12s %-15s %-12s %-15s\n", "Tamanho", "Tempo Medio", "Iteracoes", "Memoria (MB)");
    printf("------------------------------------------------------------\n");
    
    for (int i = 0; i < num_testes; i++) {
        ResultadoBenchmark *r = &todos_resultados[i];
        printf("%-12s %-15.4f %-12.0f %-15.2f\n",
               r->tamanho, r->tempo_medio, r->iteracoes_media, r->memoria_media);
    }
    
    printf("============================================================\n");
    
    // Liberar memória
    for (int i = 0; i < num_testes; i++) {
        free(todos_resultados[i].execucoes);
    }
    free(todos_resultados);
    
    return 0;
}