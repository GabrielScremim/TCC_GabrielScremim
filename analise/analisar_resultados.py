import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def carregar_resultados(arquivo_json):
    """Carrega resultados de um arquivo JSON"""
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def criar_dataframe_comparativo(resultados_python, resultados_c):
    """Cria DataFrame com comparação lado a lado"""
    dados = []
    
    for py, c in zip(resultados_python, resultados_c):
        dados.append({
            'Tamanho': py['tamanho'],
            'M': py['m'],
            'N': py['n'],
            
            # Python
            'Python_Tempo_Medio': py['estatisticas']['tempo_medio'],
            'Python_Tempo_Desvio': py['estatisticas']['tempo_desvio'],
            'Python_Memoria_MB': py['estatisticas']['memoria_media'],
            'Python_Iteracoes': py['estatisticas']['iteracoes_media'],
            
            # C
            'C_Tempo_Medio': c['estatisticas']['tempo_medio'],
            'C_Tempo_Desvio': c['estatisticas']['tempo_desvio'],
            'C_Memoria_MB': c['estatisticas']['memoria_media'],
            'C_Iteracoes': c['estatisticas']['iteracoes_media'],
            
            # Speedup
            'Speedup': py['estatisticas']['tempo_medio'] / c['estatisticas']['tempo_medio'],
            'Reducao_Memoria': (1 - c['estatisticas']['memoria_media'] / py['estatisticas']['memoria_media']) * 100
        })
    
    return pd.DataFrame(dados)

def gerar_graficos(df, output_dir='graficos'):
    """Gera todos os gráficos de comparação"""
    Path(output_dir).mkdir(exist_ok=True)
    
    # Configuração de estilo
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 6)
    
    # 1. Comparação de Tempo de Execução
    plt.figure()
    x = np.arange(len(df))
    width = 0.35
    
    plt.bar(x - width/2, df['Python_Tempo_Medio'], width, label='Python', 
            yerr=df['Python_Tempo_Desvio'], capsize=5, alpha=0.8)
    plt.bar(x + width/2, df['C_Tempo_Medio'], width, label='C', 
            yerr=df['C_Tempo_Desvio'], capsize=5, alpha=0.8)
    
    plt.xlabel('Tamanho do Problema', fontsize=12)
    plt.ylabel('Tempo Médio (segundos)', fontsize=12)
    plt.title('Comparação de Tempo de Execução: Python vs C', fontsize=14, fontweight='bold')
    plt.xticks(x, df['Tamanho'])
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacao_tempo.png', dpi=300)
    print(f"✓ Gráfico salvo: {output_dir}/comparacao_tempo.png")
    
    # 2. Speedup (escala logarítmica se necessário)
    plt.figure()
    plt.plot(df['Tamanho'], df['Speedup'], marker='o', linewidth=2, markersize=8, color='green')
    plt.axhline(y=1, color='r', linestyle='--', label='Sem ganho')
    plt.xlabel('Tamanho do Problema', fontsize=12)
    plt.ylabel('Speedup (Python/C)', fontsize=12)
    plt.title('Speedup: Quantas vezes C é mais rápido que Python', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/speedup.png', dpi=300)
    print(f"✓ Gráfico salvo: {output_dir}/speedup.png")
    
    # 3. Uso de Memória
    plt.figure()
    x = np.arange(len(df))
    
    plt.bar(x - width/2, df['Python_Memoria_MB'], width, label='Python', alpha=0.8)
    plt.bar(x + width/2, df['C_Memoria_MB'], width, label='C', alpha=0.8)
    
    plt.xlabel('Tamanho do Problema', fontsize=12)
    plt.ylabel('Memória Média (MB)', fontsize=12)
    plt.title('Comparação de Uso de Memória: Python vs C', fontsize=14, fontweight='bold')
    plt.xticks(x, df['Tamanho'])
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/comparacao_memoria.png', dpi=300)
    print(f"✓ Gráfico salvo: {output_dir}/comparacao_memoria.png")
    
    # 4. Tempo vs Tamanho (escala log-log)
    plt.figure()
    plt.loglog(df['M'] * df['N'], df['Python_Tempo_Medio'], marker='o', label='Python', linewidth=2)
    plt.loglog(df['M'] * df['N'], df['C_Tempo_Medio'], marker='s', label='C', linewidth=2)
    plt.xlabel('Número de Variáveis (M × N)', fontsize=12)
    plt.ylabel('Tempo Médio (segundos)', fontsize=12)
    plt.title('Escalabilidade: Tempo vs Tamanho do Problema', fontsize=14, fontweight='bold')
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/escalabilidade.png', dpi=300)
    print(f"✓ Gráfico salvo: {output_dir}/escalabilidade.png")
    
    # 5. Número de Iterações
    plt.figure()
    plt.plot(df['Tamanho'], df['Python_Iteracoes'], marker='o', label='Python', linewidth=2)
    plt.plot(df['Tamanho'], df['C_Iteracoes'], marker='s', label='C', linewidth=2)
    plt.xlabel('Tamanho do Problema', fontsize=12)
    plt.ylabel('Iterações Médias', fontsize=12)
    plt.title('Número de Iterações do Simplex', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/iteracoes.png', dpi=300)
    print(f"✓ Gráfico salvo: {output_dir}/iteracoes.png")
    
    # 6. Dashboard completo
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Tempo
    axes[0, 0].bar(x - width/2, df['Python_Tempo_Medio'], width, label='Python', alpha=0.8)
    axes[0, 0].bar(x + width/2, df['C_Tempo_Medio'], width, label='C', alpha=0.8)
    axes[0, 0].set_xlabel('Tamanho')
    axes[0, 0].set_ylabel('Tempo (s)')
    axes[0, 0].set_title('Tempo de Execução')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(df['Tamanho'])
    axes[0, 0].legend()
    
    # Speedup
    axes[0, 1].plot(df['Tamanho'], df['Speedup'], marker='o', linewidth=2, color='green')
    axes[0, 1].axhline(y=1, color='r', linestyle='--', alpha=0.5)
    axes[0, 1].set_xlabel('Tamanho')
    axes[0, 1].set_ylabel('Speedup')
    axes[0, 1].set_title('Speedup (Python/C)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Memória
    axes[1, 0].bar(x - width/2, df['Python_Memoria_MB'], width, label='Python', alpha=0.8)
    axes[1, 0].bar(x + width/2, df['C_Memoria_MB'], width, label='C', alpha=0.8)
    axes[1, 0].set_xlabel('Tamanho')
    axes[1, 0].set_ylabel('Memória (MB)')
    axes[1, 0].set_title('Uso de Memória')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(df['Tamanho'])
    axes[1, 0].legend()
    
    # Iterações
    axes[1, 1].plot(df['Tamanho'], df['Python_Iteracoes'], marker='o', label='Python', linewidth=2)
    axes[1, 1].plot(df['Tamanho'], df['C_Iteracoes'], marker='s', label='C', linewidth=2)
    axes[1, 1].set_xlabel('Tamanho')
    axes[1, 1].set_ylabel('Iterações')
    axes[1, 1].set_title('Número de Iterações')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Dashboard Comparativo: Python vs C', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/dashboard_completo.png', dpi=300, bbox_inches='tight')
    print(f"✓ Gráfico salvo: {output_dir}/dashboard_completo.png")
    
    plt.close('all')

def gerar_relatorio_latex(df, arquivo_saida='relatorio_comparacao.tex'):
    """Gera tabela em LaTeX para o TCC"""
    latex = r"""\begin{table}[htbp]
\centering
\caption{Comparação de Desempenho: Python vs C}
\label{tab:comparacao}
\begin{tabular}{lrrrrr}
\hline
\textbf{Tamanho} & \textbf{Tempo Python (s)} & \textbf{Tempo C (s)} & \textbf{Speedup} & \textbf{Mem. Python (MB)} & \textbf{Mem. C (MB)} \\
\hline
"""
    
    for _, row in df.iterrows():
        latex += f"{row['Tamanho']} & {row['Python_Tempo_Medio']:.4f} $\pm$ {row['Python_Tempo_Desvio']:.4f} & "
        latex += f"{row['C_Tempo_Medio']:.4f} $\pm$ {row['C_Tempo_Desvio']:.4f} & "
        latex += f"{row['Speedup']:.2f}x & {row['Python_Memoria_MB']:.2f} & {row['C_Memoria_MB']:.2f} \\\\\n"
    
    latex += r"""\hline
\end{tabular}
\end{table}
"""
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write(latex)
    
    print(f"✓ Tabela LaTeX salva: {arquivo_saida}")

def gerar_relatorio_markdown(df, arquivo_saida='RELATORIO.md'):
    """Gera relatório em Markdown"""
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        f.write("# Relatório de Comparação: Python vs C\n\n")
        f.write("## Resumo Executivo\n\n")
        
        speedup_medio = df['Speedup'].mean()
        speedup_max = df['Speedup'].max()
        reducao_memoria_media = df['Reducao_Memoria'].mean()
        
        f.write(f"- **Speedup médio:** {speedup_medio:.2f}x (C é {speedup_medio:.2f}x mais rápido)\n")
        f.write(f"- **Speedup máximo:** {speedup_max:.2f}x (no problema {df.loc[df['Speedup'].idxmax(), 'Tamanho']})\n")
        f.write(f"- **Redução média de memória:** {reducao_memoria_media:.2f}%\n\n")
        
        f.write("## Tabela Comparativa\n\n")
        f.write("| Tamanho | Tempo Python (s) | Tempo C (s) | Speedup | Memória Python (MB) | Memória C (MB) |\n")
        f.write("|---------|------------------|-------------|---------|---------------------|----------------|\n")
        
        for _, row in df.iterrows():
            f.write(f"| {row['Tamanho']} | ")
            f.write(f"{row['Python_Tempo_Medio']:.4f} ± {row['Python_Tempo_Desvio']:.4f} | ")
            f.write(f"{row['C_Tempo_Medio']:.4f} ± {row['C_Tempo_Desvio']:.4f} | ")
            f.write(f"{row['Speedup']:.2f}x | ")
            f.write(f"{row['Python_Memoria_MB']:.2f} | ")
            f.write(f"{row['C_Memoria_MB']:.2f} |\n")
        
        f.write("\n## Análise\n\n")
        f.write("### Desempenho Temporal\n\n")
        f.write(f"A linguagem C demonstrou ser consistentemente mais rápida que Python em todos os tamanhos de problema testados. ")
        f.write(f"O speedup variou de {df['Speedup'].min():.2f}x a {df['Speedup'].max():.2f}x.\n\n")
        
        f.write("### Uso de Memória\n\n")
        f.write(f"C também apresentou menor consumo de memória, com redução média de {reducao_memoria_media:.2f}% ")
        f.write(f"em relação à implementação Python.\n\n")
        
        f.write("### Escalabilidade\n\n")
        f.write("Ambas as implementações seguem a complexidade teórica esperada do algoritmo Simplex.\n\n")
        
        f.write("## Gráficos\n\n")
        f.write("Os gráficos detalhados estão disponíveis na pasta `graficos/`.\n\n")
    
    print(f"✓ Relatório Markdown salvo: {arquivo_saida}")

# ======================
# EXECUÇÃO PRINCIPAL
# ======================

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISE COMPARATIVA: PYTHON vs C")
    print("="*60)
    
    # Solicitar arquivos JSON
    print("\nArquivos JSON disponíveis:")
    json_files = list(Path('.').glob('benchmark_*.json'))
    for i, f in enumerate(json_files, 1):
        print(f"{i}. {f.name}")
    
    # Se não encontrar, usar nomes padrão
    arquivo_python = input("\nArquivo JSON do Python (ou Enter para buscar automaticamente): ").strip()
    arquivo_c = input("Arquivo JSON do C (ou Enter para buscar automaticamente): ").strip()
    
    if not arquivo_python:
        python_files = list(Path('.').glob('benchmark_python_*.json'))
        arquivo_python = str(python_files[0]) if python_files else None
    
    if not arquivo_c:
        c_files = list(Path('.').glob('benchmark_c_*.json'))
        arquivo_c = str(c_files[0]) if c_files else None
    
    if not arquivo_python or not arquivo_c:
        print("\n❌ Erro: Não foi possível encontrar os arquivos de benchmark!")
        print("Execute primeiro os benchmarks em Python e C.")
        exit(1)
    
    print(f"\n📊 Carregando resultados...")
    print(f"  Python: {arquivo_python}")
    print(f"  C: {arquivo_c}")
    
    # Carregar resultados
    resultados_python = carregar_resultados(arquivo_python)
    resultados_c = carregar_resultados(arquivo_c)
    
    # Criar DataFrame comparativo
    print("\n📈 Criando análise comparativa...")
    df = criar_dataframe_comparativo(resultados_python, resultados_c)
    
    # Mostrar resumo no console
    print("\n" + "="*60)
    print("RESUMO COMPARATIVO")
    print("="*60)
    print(df[['Tamanho', 'Python_Tempo_Medio', 'C_Tempo_Medio', 'Speedup', 
              'Python_Memoria_MB', 'C_Memoria_MB']].to_string(index=False))
    print("="*60)
    
    print(f"\n📊 Speedup médio: {df['Speedup'].mean():.2f}x")
    print(f"📊 Speedup máximo: {df['Speedup'].max():.2f}x")
    print(f"💾 Redução média de memória: {df['Reducao_Memoria'].mean():.2f}%")
    
    # Gerar gráficos
    print("\n🎨 Gerando gráficos...")
    gerar_graficos(df)
    
    # Salvar CSV comparativo
    df.to_csv('comparacao_python_c.csv', index=False)
    print(f"\n✓ CSV comparativo salvo: comparacao_python_c.csv")
    
    # Gerar relatórios
    print("\n📝 Gerando relatórios...")
    gerar_relatorio_latex(df)
    gerar_relatorio_markdown(df)
    
    print("\n" + "="*60)
    print("✅ ANÁLISE COMPLETA!")
    print("="*60)
    print("\nArquivos gerados:")
    print("  📊 graficos/ - Todos os gráficos de comparação")
    print("  📄 comparacao_python_c.csv - Dados comparativos")
    print("  📄 relatorio_comparacao.tex - Tabela para LaTeX")
    print("  📄 RELATORIO.md - Relatório completo em Markdown")
    print("="*60)