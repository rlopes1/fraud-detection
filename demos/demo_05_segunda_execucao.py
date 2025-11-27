#!/usr/bin/env python3
"""
Demo 05: Segunda Execução (Comparação de Modelos)

Este script demonstra o que acontece quando já existe
um modelo em produção e o job executa novamente.

Pré-requisito: Executar demo_04 primeiro!

Execução:
    python demos/demo_05_segunda_execucao.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def verificar_prerequisito():
    """Verifica se existe modelo em produção."""
    
    modelo = Path("models/modelo_em_producao.pkl")
    
    if not modelo.exists():
        print("=" * 60)
        print("ERRO: Não existe modelo em produção!")
        print("=" * 60)
        print()
        print("Execute primeiro:")
        print("  python demos/demo_04_primeira_execucao.py")
        print()
        return False
    
    return True


def mostrar_estado_antes():
    """Mostra estado atual do diretório models/."""
    
    print("[Estado antes da execução]")
    
    modelo = Path("models/modelo_em_producao.pkl")
    arquivo = Path("models/arquivo")
    
    if modelo.exists():
        size = modelo.stat().st_size / 1024
        print(f"  models/modelo_em_producao.pkl ({size:.1f} KB)")
    
    if arquivo.exists():
        modelos = list(arquivo.glob("*.pkl"))
        print(f"  models/arquivo/: {len(modelos)} modelo(s) arquivado(s)")
        for m in modelos:
            print(f"    └─ {m.name}")
    else:
        print("  models/arquivo/: (vazio)")
    
    print()


def mostrar_estado_depois():
    """Mostra estado após execução."""
    
    print("[Estado depois da execução]")
    
    arquivo = Path("models/arquivo")
    
    if arquivo.exists():
        modelos = sorted(arquivo.glob("*.pkl"))
        print(f"  models/arquivo/: {len(modelos)} modelo(s) arquivado(s)")
        for m in modelos:
            size = m.stat().st_size / 1024
            print(f"    └─ {m.name} ({size:.1f} KB)")
    
    print()


def main():
    print("=" * 60)
    print("SEGUNDA EXECUÇÃO DO JOB (COMPARAÇÃO)")
    print("=" * 60)
    print()
    print("Cenário: Já existe modelo em produção.")
    print("         Job vai treinar novo e COMPARAR.")
    print()
    print("O que vai acontecer:")
    print("  • F1 atual > 0 (modelo anterior)")
    print("  • Se novo >= atual: promove e arquiva anterior")
    print("  • Se novo < atual: mantém atual e alerta")
    print()
    print("─" * 60)
    
    if not verificar_prerequisito():
        return
    
    mostrar_estado_antes()
    
    # Executa job
    from demo_job_retreinamento import executar_job
    executar_job(usar_csv=False)
    
    print("─" * 60)
    print()
    
    mostrar_estado_depois()
    
    print("OBSERVAÇÃO:")
    print("  O modelo anterior foi ARQUIVADO com timestamp.")
    print("  Isso permite rollback se necessário.")
    print()


if __name__ == "__main__":
    main()
