#!/usr/bin/env python3
"""
Demo 04: Primeira Execução do Job

Este script demonstra a primeira execução do job de re-treinamento,
quando ainda não existe modelo em produção.

Execução:
    python demos/demo_04_primeira_execucao.py
"""

import sys
import shutil
from pathlib import Path

# Adiciona diretório pai ao path para importar o job
sys.path.insert(0, str(Path(__file__).parent.parent))


def limpar_estado():
    """Remove modelos anteriores para simular primeira execução."""
    
    arquivos = [
        Path("models/modelo_em_producao.pkl"),
        Path("data/teste_fixo.csv"),
    ]
    
    diretorios = [
        Path("models/arquivo"),
    ]
    
    print("[Preparação] Limpando estado anterior...")
    
    for arq in arquivos:
        if arq.exists():
            arq.unlink()
            print(f"  Removido: {arq}")
    
    for dir in diretorios:
        if dir.exists():
            shutil.rmtree(dir)
            print(f"  Removido: {dir}/")
    
    print("  ✓ Estado limpo\n")


def main():
    print("=" * 60)
    print("PRIMEIRA EXECUÇÃO DO JOB")
    print("=" * 60)
    print()
    print("Cenário: É a primeira vez que o job roda.")
    print("         Não existe modelo em produção ainda.")
    print()
    print("O que vai acontecer:")
    print("  • F1 atual = 0 (não há modelo para comparar)")
    print("  • Qualquer modelo novo será promovido")
    print("  • Arquivo de teste fixo será criado")
    print()
    print("─" * 60)
    
    # Limpa estado
    limpar_estado()
    
    # Executa job
    from demo_job_retreinamento import executar_job
    executar_job(usar_csv=False)
    
    print("─" * 60)
    print()
    print("RESULTADO:")
    print()
    
    # Verifica o que foi criado
    if Path("models/modelo_em_producao.pkl").exists():
        size = Path("models/modelo_em_producao.pkl").stat().st_size / 1024
        print(f"  ✓ models/modelo_em_producao.pkl criado ({size:.1f} KB)")
    
    if Path("data/teste_fixo.csv").exists():
        import pandas as pd
        df = pd.read_csv("data/teste_fixo.csv")
        print(f"  ✓ data/teste_fixo.csv criado ({len(df):,} linhas)")
    
    print()
    print("Próximo passo: Execute demo_05 para ver a comparação")
    print()


if __name__ == "__main__":
    main()
