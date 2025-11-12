# Relatório de Comparação: Python vs C

## Resumo Executivo

- **Speedup médio:** 23.71x (C é 23.71x mais rápido)
- **Speedup máximo:** 40.16x (no problema 90x90)
- **Redução média de memória:** 57.31%

## Tabela Comparativa

| Tamanho | Tempo Python (s) | Tempo C (s) | Speedup | Memória Python (MB) | Memória C (MB) |
|---------|------------------|-------------|---------|---------------------|----------------|
| 50x50 | 2.7732 ± 0.6423 | 0.3226 ± 0.1126 | 8.60x | 5.16 | 2.00 |
| 60x60 | 5.4639 ± 0.3654 | 0.6064 ± 0.2058 | 9.01x | 6.98 | 3.00 |
| 70x70 | 10.8382 ± 0.8585 | 0.5711 ± 0.2102 | 18.98x | 10.72 | 5.00 |
| 80x80 | 25.2189 ± 6.6228 | 0.7560 ± 0.0343 | 33.36x | 18.07 | 8.00 |
| 90x90 | 47.2530 ± 9.9874 | 1.1766 ± 0.0624 | 40.16x | 27.60 | 11.70 |
| 100x100 | 57.5184 ± 10.3389 | 1.7893 ± 0.0916 | 32.15x | 38.88 | 16.00 |

## Análise

### Desempenho Temporal

A linguagem C demonstrou ser consistentemente mais rápida que Python em todos os tamanhos de problema testados. O speedup variou de 8.60x a 40.16x.

### Uso de Memória

C também apresentou menor consumo de memória, com redução média de 57.31% em relação à implementação Python.

### Escalabilidade

Ambas as implementações seguem a complexidade teórica esperada do algoritmo Simplex.

## Gráficos

Os gráficos detalhados estão disponíveis na pasta `graficos/`.

