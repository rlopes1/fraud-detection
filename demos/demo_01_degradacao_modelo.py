#!/usr/bin/env python3
"""
Demo 01: Degradação de Modelo ao Longo do Tempo

Este script demonstra NA PRÁTICA como um modelo degrada quando
os dados mudam (drift) e ele não é re-treinado.

Execução:
    python demos/demo_01_degradacao_modelo.py
"""

from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score


def gerar_dados_mes(n: int, seed: int, drift: float = 0.0) -> pd.DataFrame:
    """
    Gera dados de um mês.
    
    drift: intensidade da mudança nos dados (0 = sem mudança)
    """
    np.random.seed(seed)
    
    # Cria features base
    valor = np.random.exponential(500, n)
    hora = np.random.randint(0, 24, n)
    dia_semana = np.random.randint(0, 7, n)
    categoria = np.random.choice(['A', 'B', 'C', 'D'], n)
    
    # Padrão de fraude muda com drift
    # Sem drift: fraude = valor alto + horário noturno + categoria D
    # Com drift: padrão inverte gradualmente
    
    score_fraude = np.zeros(n)
    
    # Componente valor (alto = suspeito originalmente)
    if drift < 0.5:
        score_fraude += (valor > 1000) * 0.4 * (1 - drift)
    else:
        score_fraude += (valor < 200) * 0.4 * drift  # Inverte
    
    # Componente horário (noturno = suspeito originalmente)
    if drift < 0.5:
        score_fraude += ((hora >= 22) | (hora <= 5)) * 0.3 * (1 - drift)
    else:
        score_fraude += ((hora >= 10) & (hora <= 16)) * 0.3 * drift  # Inverte
    
    # Componente categoria
    score_fraude += (categoria == 'D') * 0.2
    
    # Base de fraude
    score_fraude += 0.02
    
    # Gera fraudes baseado no score
    is_fraude = (np.random.random(n) < score_fraude).astype(int)
    
    dados = pd.DataFrame({
        'valor': valor,
        'hora': hora,
        'dia_semana': dia_semana,
        'categoria': categoria,
        'is_fraude': is_fraude
    })
    
    return dados


def preparar_features(dados: pd.DataFrame):
    """Prepara features para o modelo."""
    dados_encoded = pd.get_dummies(dados, columns=['categoria'])
    colunas = [c for c in dados_encoded.columns if c != 'is_fraude']
    return dados_encoded[colunas], dados_encoded['is_fraude']


def imprimir_barra(valor: float, rotulo: str, largura: int = 30):
    """Imprime barra visual do F1-score."""
    preenchido = int(valor * largura)
    barra = "█" * preenchido + "░" * (largura - preenchido)
    
    if valor >= 0.75:
        status = "🟢"
    elif valor >= 0.50:
        status = "🟡"
    else:
        status = "🔴"
    
    print(f"  {rotulo:12} │{barra}│ {valor:.2f} {status}")


def main():
    print("=" * 60)
    print("SIMULAÇÃO: DEGRADAÇÃO DE MODELO SEM RE-TREINAMENTO")
    print("=" * 60)
    
    # ===== ETAPA 1: Treinar modelo com dados de janeiro =====
    print("\n[1] Treinando modelo com dados de JANEIRO...")
    
    dados_janeiro = gerar_dados_mes(50000, seed=1, drift=0.0)
    X_treino, y_treino = preparar_features(dados_janeiro)
    
    modelo = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
    modelo.fit(X_treino, y_treino)
    
    print(f"    Transações de treino: {len(dados_janeiro):,}")
    print(f"    Fraudes no treino: {y_treino.sum():,} ({y_treino.mean()*100:.1f}%)")
    print("    ✓ Modelo treinado")
    
    # ===== ETAPA 2: Avaliar em cada mês (sem re-treinar) =====
    print("\n[2] Avaliando modelo nos meses seguintes (SEM re-treinar)...")
    print()
    
    meses = [
        ("Janeiro", 0.0),
        ("Fevereiro", 0.1),
        ("Março", 0.3),
        ("Abril", 0.5),
        ("Maio", 0.7),
        ("Junho", 1.0),
    ]
    
    resultados = []
    
    for i, (nome, drift) in enumerate(meses):
        # Gera dados do mês
        dados_mes = gerar_dados_mes(10000, seed=100+i, drift=drift)
        X_teste, y_teste = preparar_features(dados_mes)
        
        # Avalia modelo (que foi treinado só em janeiro!)
        y_pred = modelo.predict(X_teste)
        f1 = f1_score(y_teste, y_pred)
        
        resultados.append((nome, f1, drift))
        imprimir_barra(f1, nome)
    
    # ===== ETAPA 3: Análise =====
    print("\n" + "─" * 60)
    print("\n[3] O QUE ACONTECEU?")
    
    f1_inicial = resultados[0][1]
    f1_final = resultados[-1][1]
    queda = f1_inicial - f1_final
    
    print(f"\n    F1 em Janeiro: {f1_inicial:.2f}")
    print(f"    F1 em Junho:   {f1_final:.2f}")
    print(f"    Queda total:   {queda:.2f}")
    if f1_inicial > 0:
        print(f"    Queda %:       {queda/f1_inicial*100:.0f}%")
    
    print("\n    CAUSAS:")
    print("    • DATA DRIFT: distribuição dos dados mudou")
    print("      - Valores de transação aumentaram (inflação)")
    print("      - Padrões de fraude mudaram")
    print()
    print("    • CONCEPT DRIFT: relação features→fraude mudou")
    print("      - Fraudadores adaptaram táticas")
    print("      - Modelo aprendeu padrões que não valem mais")
    
    print("\n    SOLUÇÃO: Re-treinar periodicamente!")
    print()


if __name__ == "__main__":
    main()
