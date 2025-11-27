#!/usr/bin/env python3
"""
Demo 07: Dados Corrompidos (Fail Fast)

Este script demonstra o que acontece quando os dados
de entrada estão corrompidos.

O sistema deve:
- Detectar na VALIDAÇÃO (antes de treinar)
- Parar o job IMEDIATAMENTE
- Não criar modelo com dados ruins
- Alertar a equipe

Conceito: "Fail Fast" - melhor falhar cedo que tarde.

Execução:
    python demos/demo_07_dados_corrompidos.py
"""

import pandas as pd
import numpy as np


def gerar_dados_corrompidos() -> pd.DataFrame:
    """
    Gera dados PROPOSITALMENTE corrompidos.
    
    Simula cenário onde ETL falhou e enviou dados ruins:
    - Valores negativos
    - Horas inválidas (>23 ou <0)
    - Muitos NaN
    - Poucos registros
    """
    
    print("[1] Simulando dados corrompidos do ETL...")
    
    np.random.seed(42)
    n = 500  # Poucos dados
    
    dados = pd.DataFrame({
        # 40% valores negativos (erro de sinal)
        'valor': np.concatenate([
            np.random.exponential(500, int(n * 0.6)),
            -np.random.exponential(500, int(n * 0.4))
        ]),
        # Horas inválidas
        'hora': np.random.randint(-5, 30, n),
        'dia_semana': np.random.randint(0, 7, n),
        'categoria': np.random.choice(['A', 'B', 'C', 'D', None], n),
        'is_fraude': np.random.choice([0, 1], n, p=[0.97, 0.03])
    })
    
    # Adiciona NaN extras
    dados.loc[np.random.choice(n, 100), 'valor'] = np.nan
    
    print(f"    Total de registros: {len(dados)}")
    print(f"    Valores negativos: {(dados['valor'] < 0).sum()}")
    print(f"    Horas inválidas: {(~dados['hora'].between(0, 23)).sum()}")
    print(f"    Valores NaN: {dados['valor'].isna().sum()}")
    
    return dados


def validar_dados(dados: pd.DataFrame, minimo: int = 1000) -> pd.DataFrame:
    """
    Valida e limpa os dados.
    
    Se dados insuficientes após limpeza, FALHA.
    """
    
    print("\n[2] Validando dados...")
    
    n_original = len(dados)
    
    # Etapa 1: Remove NaN
    dados_limpos = dados.dropna()
    removidos_nan = n_original - len(dados_limpos)
    print(f"    Removidos (NaN): {removidos_nan}")
    
    # Etapa 2: Remove valores negativos
    antes = len(dados_limpos)
    dados_limpos = dados_limpos[dados_limpos['valor'] > 0]
    print(f"    Removidos (valor <= 0): {antes - len(dados_limpos)}")
    
    # Etapa 3: Remove horas inválidas
    antes = len(dados_limpos)
    dados_limpos = dados_limpos[dados_limpos['hora'].between(0, 23)]
    print(f"    Removidos (hora inválida): {antes - len(dados_limpos)}")
    
    # Resumo
    print()
    print(f"    Registros originais: {n_original}")
    print(f"    Registros válidos: {len(dados_limpos)}")
    print(f"    Mínimo necessário: {minimo}")
    
    # Validação final
    if len(dados_limpos) < minimo:
        pct = (n_original - len(dados_limpos)) / n_original * 100
        raise ValueError(
            f"DADOS INSUFICIENTES: {len(dados_limpos)} < {minimo}. "
            f"Perdidos: {pct:.0f}% dos registros."
        )
    
    return dados_limpos


def main():
    print("=" * 60)
    print("CENÁRIO: DADOS CORROMPIDOS")
    print("=" * 60)
    print()
    print("Situação: ETL upstream falhou.")
    print("          Dados chegaram corrompidos.")
    print("          Sistema deve parar ANTES de treinar.")
    print()
    print("Conceito: 'FAIL FAST'")
    print("          Melhor falhar na validação")
    print("          do que treinar modelo com lixo.")
    print()
    print("─" * 60)
    
    # Gera dados corrompidos
    dados = gerar_dados_corrompidos()
    
    # Tenta validar
    try:
        dados_limpos = validar_dados(dados)
        
        # Se chegou aqui, dados eram OK (não deveria acontecer)
        print("\n[3] Treinando modelo...")
        print("    (não deveria chegar aqui)")
        
    except ValueError as e:
        print()
        print("╔══════════════════════════════════════════════════════════╗")
        print("║  ❌ FALHA NA VALIDAÇÃO                                   ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print(f"║  {str(e)[:54]:<54} ║")
        print("║                                                          ║")
        print("║  AÇÃO: Job ABORTADO                                      ║")
        print("║  - Nenhum modelo foi criado                              ║")
        print("║  - Modelo em produção continua intacto                   ║")
        print("║                                                          ║")
        print("║  PRÓXIMO PASSO:                                          ║")
        print("║  - Verificar logs do ETL                                 ║")
        print("║  - Checar fonte de dados                                 ║")
        print("║  - Contactar time de dados                               ║")
        print("╚══════════════════════════════════════════════════════════╝")
    
    print()
    print("─" * 60)
    print()
    print("CONCLUSÃO:")
    print("  O sistema funcionou corretamente!")
    print()
    print("  FAIL FAST significa:")
    print("  • Detectar problema o mais cedo possível")
    print("  • Não propagar erro para etapas seguintes")
    print("  • Dar informação clara sobre o que aconteceu")
    print()
    print("  Sem validação, teríamos treinado modelo com dados")
    print("  ruins e só descobriríamos o problema em produção.")
    print()


if __name__ == "__main__":
    main()
