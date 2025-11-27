#!/usr/bin/env python3
"""
Demo 08: Por que usar DVC? (Git vs DVC)

Este script demonstra NA PRÁTICA a diferença entre
versionar arquivos grandes com Git vs DVC.

Mostra:
- Tamanho real dos arquivos
- Problema de crescimento do repositório
- Como DVC resolve com ponteiros

Execução:
    python demos/demo_08_antes_depois_dvc.py
"""

import os
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np


def criar_arquivo_dados(caminho: Path, n_linhas: int) -> int:
    """Cria arquivo CSV e retorna tamanho em bytes."""
    
    np.random.seed(42)
    dados = pd.DataFrame({
        'valor': np.random.exponential(500, n_linhas),
        'hora': np.random.randint(0, 24, n_linhas),
        'dia_semana': np.random.randint(0, 7, n_linhas),
        'categoria': np.random.choice(['A', 'B', 'C', 'D'], n_linhas),
        'is_fraude': np.random.choice([0, 1], n_linhas, p=[0.97, 0.03])
    })
    
    caminho.parent.mkdir(parents=True, exist_ok=True)
    dados.to_csv(caminho, index=False)
    
    return caminho.stat().st_size


def calcular_hash(caminho: Path) -> str:
    """Calcula hash MD5 do arquivo (como DVC faz)."""
    
    hash_md5 = hashlib.md5()
    with open(caminho, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def formatar_tamanho(bytes: int) -> str:
    """Formata bytes para leitura humana."""
    for unidade in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unidade}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


def simular_cenario_git(n_versoes: int, tamanho_arquivo: int) -> list:
    """Simula crescimento do repositório com Git puro."""
    
    tamanhos = []
    tamanho_acumulado = 0
    
    for v in range(1, n_versoes + 1):
        # Git guarda cópia completa de arquivos binários/grandes
        tamanho_acumulado += tamanho_arquivo
        tamanhos.append(tamanho_acumulado)
    
    return tamanhos


def simular_cenario_dvc(n_versoes: int) -> list:
    """Simula crescimento do repositório com DVC."""
    
    # Arquivo .dvc tem ~100 bytes
    tamanho_ponteiro = 100
    tamanhos = []
    
    for v in range(1, n_versoes + 1):
        # Git só guarda ponteiros pequenos
        tamanhos.append(tamanho_ponteiro * v)
    
    return tamanhos


def main():
    print("=" * 60)
    print("POR QUE USAR DVC? (Git vs DVC)")
    print("=" * 60)
    
    # ===== ETAPA 1: Criar arquivo de dados real =====
    print("\n[1] Criando arquivo de dados real...")
    
    caminho_dados = Path("data/exemplo_grande.csv")
    tamanho = criar_arquivo_dados(caminho_dados, n_linhas=100000)
    hash_arquivo = calcular_hash(caminho_dados)
    
    print(f"    Arquivo: {caminho_dados}")
    print(f"    Linhas: 100,000")
    print(f"    Tamanho: {formatar_tamanho(tamanho)}")
    print(f"    Hash MD5: {hash_arquivo[:16]}...")
    
    # ===== ETAPA 2: Simular arquivo .dvc =====
    print("\n[2] O que DVC criaria (arquivo .dvc):")
    print()
    print("    ┌─────────────────────────────────────────────────────┐")
    print("    │ outs:                                               │")
    print(f"    │ - md5: {hash_arquivo}   │")
    print(f"    │   size: {tamanho}                                  │")
    print("    │   path: exemplo_grande.csv                         │")
    print("    └─────────────────────────────────────────────────────┘")
    print()
    print(f"    Tamanho do .dvc: ~100 bytes")
    print(f"    Tamanho do CSV:  {formatar_tamanho(tamanho)}")
    print(f"    Redução: {tamanho / 100:.0f}x menor no Git!")
    
    # ===== ETAPA 3: Simular 24 semanas =====
    print("\n[3] Simulando 24 semanas (6 meses) de versionamento:")
    print()
    
    n_versoes = 24
    tamanhos_git = simular_cenario_git(n_versoes, tamanho)
    tamanhos_dvc = simular_cenario_dvc(n_versoes)
    
    print("    Semana    Git puro         Git + DVC")
    print("    " + "─" * 44)
    
    for semana in [1, 4, 8, 12, 24]:
        t_git = tamanhos_git[semana - 1]
        t_dvc = tamanhos_dvc[semana - 1]
        print(f"    {semana:6}    {formatar_tamanho(t_git):>12}     {formatar_tamanho(t_dvc):>12}")
    
    print("    " + "─" * 44)
    
    # ===== ETAPA 4: Comparação =====
    print("\n[4] Comparação após 6 meses:")
    print()
    
    repo_git = tamanhos_git[-1]
    repo_dvc = tamanhos_dvc[-1]
    storage_dvc = tamanho * n_versoes  # dados ficam no storage
    
    print("    COM GIT PURO:")
    print(f"      Repositório: {formatar_tamanho(repo_git)}")
    print(f"      Clone: baixa TUDO (lento)")
    print(f"      Push: pode falhar (limite 100MB no GitHub)")
    print()
    print("    COM GIT + DVC:")
    print(f"      Repositório Git: {formatar_tamanho(repo_dvc)}")
    print(f"      Storage DVC: {formatar_tamanho(storage_dvc)} (separado)")
    print(f"      Clone: só ponteiros (rápido)")
    print(f"      dvc pull: baixa só versão atual")
    
    # ===== ETAPA 5: Resumo =====
    print()
    print("─" * 60)
    print()
    print("RESUMO:")
    print()
    print("  ┌──────────────────┬──────────────────┐")
    print("  │    Git puro      │    Git + DVC     │")
    print("  ├──────────────────┼──────────────────┤")
    print("  │ Repo cresce      │ Repo pequeno     │")
    print("  │ Clone lento      │ Clone rápido     │")
    print("  │ Push pode falhar │ Push normal      │")
    print("  │ Sem histórico    │ Histórico OK     │")
    print("  │ dados            │ (via hash)       │")
    print("  └──────────────────┴──────────────────┘")
    print()
    print("  DVC = 'Git para dados'")
    print("  - Git versiona os PONTEIROS (pequenos)")
    print("  - DVC versiona os DADOS (no storage)")
    print()
    
    # Limpa arquivo criado
    if caminho_dados.exists():
        caminho_dados.unlink()


if __name__ == "__main__":
    main()
