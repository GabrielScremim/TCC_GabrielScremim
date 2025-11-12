# Relatório Comparativo: Bibliotecas Python para Simplex

## 📊 Resumo Executivo

### Problema 50x50
- **Mais rápida:** OR-Tools (0.0174s)
- **Mais lenta:** Implementação Manual (2.5068s)
- **Speedup:** 144.27x

### Problema 60x60
- **Mais rápida:** OR-Tools (0.0250s)
- **Mais lenta:** Implementação Manual (5.2724s)
- **Speedup:** 211.21x

### Problema 70x70
- **Mais rápida:** OR-Tools (0.0333s)
- **Mais lenta:** Implementação Manual (10.9708s)
- **Speedup:** 329.18x

### Problema 80x80
- **Mais rápida:** OR-Tools (0.0409s)
- **Mais lenta:** Implementação Manual (19.4680s)
- **Speedup:** 475.43x

### Problema 90x90
- **Mais rápida:** OR-Tools (0.0523s)
- **Mais lenta:** Implementação Manual (32.1145s)
- **Speedup:** 613.80x

### Problema 100x100
- **Mais rápida:** OR-Tools (0.0685s)
- **Mais lenta:** Implementação Manual (55.1566s)
- **Speedup:** 804.91x

## 📋 Tabela Comparativa Completa

| Tamanho | Biblioteca | Tempo (s) | Memória (MB) | Iterações | Taxa Sucesso |
|---------|------------|-----------|--------------|-----------|-------------|
| 50x50 | Implementação Manual | 2.5068 ± 0.1322 | 1.37 | 138 | 100% |
| 50x50 | SciPy (linprog) | 0.0432 ± 0.0159 | 0.61 | 132 | 100% |
| 50x50 | PuLP | 0.1138 ± 0.0630 | 0.32 | 0 | 100% |
| 50x50 | OR-Tools | 0.0174 ± 0.0023 | 0.28 | 129 | 100% |
| 60x60 | Implementação Manual | 5.2724 ± 0.3745 | 1.29 | 167 | 100% |
| 60x60 | SciPy (linprog) | 0.0565 ± 0.0016 | 0.19 | 163 | 100% |
| 60x60 | PuLP | 0.1306 ± 0.0128 | 0.50 | 0 | 100% |
| 60x60 | OR-Tools | 0.0250 ± 0.0020 | 0.10 | 171 | 100% |
| 70x70 | Implementação Manual | 10.9708 ± 1.2706 | 0.91 | 204 | 100% |
| 70x70 | SciPy (linprog) | 0.0822 ± 0.0037 | 0.11 | 183 | 100% |
| 70x70 | PuLP | 0.1398 ± 0.0062 | 1.01 | 0 | 100% |
| 70x70 | OR-Tools | 0.0333 ± 0.0021 | 0.10 | 194 | 100% |
| 80x80 | Implementação Manual | 19.4680 ± 2.2765 | 1.72 | 241 | 100% |
| 80x80 | SciPy (linprog) | 0.1083 ± 0.0033 | 0.17 | 211 | 100% |
| 80x80 | PuLP | 0.1670 ± 0.0060 | 0.52 | 0 | 100% |
| 80x80 | OR-Tools | 0.0409 ± 0.0015 | 1.39 | 229 | 100% |
| 90x90 | Implementação Manual | 32.1145 ± 4.0150 | 1.81 | 273 | 100% |
| 90x90 | SciPy (linprog) | 0.1466 ± 0.0094 | 1.15 | 242 | 100% |
| 90x90 | PuLP | 0.1996 ± 0.0022 | 0.29 | 0 | 100% |
| 90x90 | OR-Tools | 0.0523 ± 0.0019 | 0.97 | 274 | 100% |
| 100x100 | Implementação Manual | 55.1566 ± 5.8765 | 1.73 | 308 | 100% |
| 100x100 | SciPy (linprog) | 0.1944 ± 0.0200 | 3.64 | 268 | 100% |
| 100x100 | PuLP | 0.2394 ± 0.0053 | 0.11 | 0 | 100% |
| 100x100 | OR-Tools | 0.0685 ± 0.0029 | 1.15 | 317 | 100% |

## 🏆 Ranking Geral (Tempo Médio Total)

1. **OR-Tools**: 0.2375s (soma de todos os testes)
2. **SciPy (linprog)**: 0.6313s (soma de todos os testes)
3. **PuLP**: 0.9902s (soma de todos os testes)
4. **Implementação Manual**: 125.4891s (soma de todos os testes)

## 📚 Características das Bibliotecas

### Implementação Manual

**Vantagens:**
- Controle total do algoritmo
- Didático
- Sem dependências externas

**Desvantagens:**
- Mais lento
- Sem otimizações avançadas
- Maior uso de memória Python

### SciPy (linprog)

**Vantagens:**
- Biblioteca padrão científica
- Bem documentada
- HiGHS solver moderno

**Desvantagens:**
- Interface genérica (não específica para transporte)
- Overhead de conversão

### PuLP

**Vantagens:**
- Modelagem intuitiva
- Suporta múltiplos solvers
- Código limpo

**Desvantagens:**
- Depende de solver externo (CBC)
- Overhead de modelagem

### OR-Tools

**Vantagens:**
- Desenvolvido pelo Google
- Solver GLOP otimizado
- Performance excelente

**Desvantagens:**
- Sintaxe mais verbosa
- Biblioteca grande

## 💡 Recomendações

### Para Aprendizado:
- Use a **Implementação Manual** para entender o algoritmo Simplex

### Para Prototipagem Rápida:
- Use **PuLP** pela facilidade de modelagem

### Para Performance:
- Use **OR-Tools** (melhor desempenho observado)

### Para Produção:
- Use **OR-Tools** ou **SciPy** (estáveis e bem mantidas)

## 📈 Conclusões

1. Bibliotecas especializadas são significativamente mais rápidas que implementações manuais
2. A escolha da biblioteca deve considerar: performance, facilidade de uso e requisitos do projeto
3. Para problemas grandes, a diferença de performance se torna crítica
4. Todas as bibliotecas testadas produziram resultados corretos (taxa de sucesso 100%)

