# Relatório de Comparação: Python vs C

## Resumo Executivo

- **Speedup médio:** 75.08x (C é 75.08x mais rápido)
- **Speedup máximo:** 100.44x (no problema 70x70)
- **Redução média de memória:** 58.06%

## Tabela Comparativa

| Tamanho | Tempo Python (s) | Tempo C (s) | Speedup | Memória Python (MB) | Memória C (MB) |
|---------|------------------|-------------|---------|---------------------|----------------|
| 50x50 | 9.0649 ± 1.1984 | 0.1179 ± 0.0148 | 76.89x | 5.44 | 2.00 |
| 60x60 | 18.0839 ± 0.7961 | 0.2673 ± 0.0490 | 67.65x | 7.02 | 3.00 |
| 70x70 | 42.3769 ± 5.6838 | 0.4219 ± 0.0236 | 100.44x | 10.73 | 5.00 |
| 80x80 | 61.8559 ± 4.1444 | 0.7437 ± 0.0246 | 83.17x | 18.05 | 8.00 |
| 90x90 | 87.8633 ± 12.7515 | 1.1777 ± 0.0600 | 74.61x | 27.62 | 11.00 |
| 100x100 | 86.0018 ± 37.1240 | 1.8023 ± 0.0895 | 47.72x | 38.62 | 16.00 |

## Análise

### Desempenho Temporal

A linguagem C demonstrou ser consistentemente mais rápida que Python em todos os tamanhos de problema testados. O speedup variou de 47.72x a 100.44x.

### Uso de Memória

C também apresentou menor consumo de memória, com redução média de 58.06% em relação à implementação Python.

### Escalabilidade

Ambas as implementações seguem a complexidade teórica esperada do algoritmo Simplex.

## Gráficos

Os gráficos detalhados estão disponíveis na pasta `graficos/`.

