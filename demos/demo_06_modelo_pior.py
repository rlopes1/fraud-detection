#!/usr/bin/env python3
"""
Demo 06: Modelo Novo é PIOR

Este script demonstra o que acontece quando o modelo novo
tem performance pior que o atual.

O sistema deve:
- Detectar que é pior
- NÃO promover
- Alertar a equipe
- Manter modelo atual em produção

Execução:
    python demos/demo_06_modelo_pior.py
"""

import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import f1_score


def criar_modelo_bom():
    """Cria um modelo razoável para simular o modelo em produção."""
    
    print("[1] Criando modelo BOM em produção...")
    
    np.random.seed(42)
    n = 20000
    
    dados = pd.DataFrame({
        'valor': np.random.exponential(500, n),
        'hora': np.random.randint(0, 24, n),
        'dia_semana': np.random.randint(0, 7, n),
        'categoria': np.random.choice(['A', 'B', 'C', 'D'], n),
        'is_fraude': np.random.choice([0, 1], n, p=[0.97, 0.03])
    })
    
    dados_enc = pd.get_dummies(dados, columns=['categoria'])
    cols = [c for c in dados_enc.columns if c != 'is_fraude']
    X, y = dados_enc[cols], dados_enc['is_fraude']
    
    modelo = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    modelo.fit(X, y)
    
    Path("models").mkdir(exist_ok=True)
    with open("models/modelo_em_producao.pkl", 'wb') as f:
        pickle.dump(modelo, f)
    
    print("    ✓ Modelo bom salvo")
    return modelo


def criar_dados_teste():
    """Cria dados de teste fixos."""
    
    np.random.seed(12345)
    dados = pd.DataFrame({
        'valor': np.random.exponential(500, 10000),
        'hora': np.random.randint(0, 24, 10000),
        'dia_semana': np.random.randint(0, 7, 10000),
        'categoria': np.random.choice(['A', 'B', 'C', 'D'], 10000),
        'is_fraude': np.random.choice([0, 1], 10000, p=[0.97, 0.03])
    })
    
    Path("data").mkdir(exist_ok=True)
    dados.to_csv("data/teste_fixo.csv", index=False)
    return dados


def treinar_modelo_ruim():
    """
    Treina modelo PROPOSITALMENTE ruim.
    
    Usa DummyClassifier que sempre prevê a classe majoritária.
    Isso simula um cenário onde os dados de treino vieram
    corrompidos ou com problema.
    """
    
    print("\n[2] Treinando modelo RUIM (dados problemáticos)...")
    
    np.random.seed(999)
    n = 1000
    
    dados = pd.DataFrame({
        'valor': np.random.exponential(500, n),
        'hora': np.random.randint(0, 24, n),
        'dia_semana': np.random.randint(0, 7, n),
        'categoria': np.random.choice(['A', 'B', 'C', 'D'], n),
        'is_fraude': np.random.choice([0, 1], n, p=[0.97, 0.03])
    })
    
    dados_enc = pd.get_dummies(dados, columns=['categoria'])
    cols = [c for c in dados_enc.columns if c != 'is_fraude']
    X, y = dados_enc[cols], dados_enc['is_fraude']
    
    # DummyClassifier sempre prevê "não fraude" (classe majoritária)
    modelo = DummyClassifier(strategy='most_frequent')
    modelo.fit(X, y)
    
    print("    ✓ Modelo ruim treinado (sempre prevê 'não fraude')")
    return modelo


def comparar_modelos(modelo_atual, modelo_novo, dados_teste):
    """Compara os dois modelos."""
    
    print("\n[3] Comparando modelos...")
    
    dados_enc = pd.get_dummies(dados_teste, columns=['categoria'])
    cols = [c for c in dados_enc.columns if c != 'is_fraude']
    X_teste, y_teste = dados_enc[cols], dados_enc['is_fraude']
    
    f1_atual = f1_score(y_teste, modelo_atual.predict(X_teste))
    f1_novo = f1_score(y_teste, modelo_novo.predict(X_teste))
    
    print(f"\n    F1 modelo ATUAL: {f1_atual:.4f}")
    print(f"    F1 modelo NOVO:  {f1_novo:.4f}")
    print(f"    Diferença:       {f1_novo - f1_atual:+.4f}")
    
    return f1_atual, f1_novo


def main():
    print("=" * 60)
    print("CENÁRIO: MODELO NOVO É PIOR")
    print("=" * 60)
    print()
    print("Situação: Os dados desta semana vieram com problema.")
    print("          O modelo treinado é RUIM.")
    print("          O sistema deve PROTEGER a produção.")
    print()
    print("─" * 60)
    
    # Setup
    modelo_atual = criar_modelo_bom()
    dados_teste = criar_dados_teste()
    modelo_novo = treinar_modelo_ruim()
    
    # Comparação
    f1_atual, f1_novo = comparar_modelos(modelo_atual, modelo_novo, dados_teste)
    
    # Decisão
    print("\n[4] Decisão do sistema:")
    print()
    
    if f1_novo >= f1_atual:
        print("    ✓ Modelo novo é melhor → PROMOVER")
    else:
        print("    ✗ Modelo novo é PIOR")
        print()
        print("    ╔══════════════════════════════════════════════════╗")
        print("    ║  ⚠️  ALERTA: Modelo novo rejeitado!              ║")
        print("    ╠══════════════════════════════════════════════════╣")
        print(f"    ║  F1 atual: {f1_atual:.4f}                           ║")
        print(f"    ║  F1 novo:  {f1_novo:.4f}                           ║")
        print("    ║                                                  ║")
        print("    ║  AÇÃO: Modelo atual MANTIDO em produção          ║")
        print("    ║  TODO: Investigar dados de treino                ║")
        print("    ╚══════════════════════════════════════════════════╝")
    
    print()
    print("─" * 60)
    print()
    print("CONCLUSÃO:")
    print("  O sistema funcionou corretamente!")
    print("  Ele detectou o problema e protegeu a produção.")
    print()
    print("  Sem essa verificação, o modelo ruim iria para produção")
    print("  e causaria problemas (fraudes não detectadas, etc).")
    print()


if __name__ == "__main__":
    main()
