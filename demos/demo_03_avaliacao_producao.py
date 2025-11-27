#!/usr/bin/env python3
"""
Demo 03: Avaliação de Modelo em Produção

Este script demonstra como funciona o monitoramento de um modelo
em produção, lidando com o problema de ground truth atrasado.

Em fraude, só sabemos se era fraude de verdade 7-30 dias depois
(quando o chargeback acontece).

Execução:
    python demos/demo_03_avaliacao_producao.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, precision_score, recall_score


def gerar_log_predicoes(n_dias: int = 40) -> pd.DataFrame:
    """
    Simula log de predições do modelo em produção.
    
    Cada transação tem:
    - data da predição
    - predição do modelo (0 ou 1)
    - probabilidade
    """
    np.random.seed(42)
    
    registros = []
    hoje = datetime.now()
    
    for dia in range(n_dias):
        data = hoje - timedelta(days=dia)
        n_transacoes = np.random.randint(800, 1200)
        
        for _ in range(n_transacoes):
            prob = np.random.beta(2, 50)  # maioria baixa probabilidade
            registros.append({
                'transacao_id': len(registros),
                'data_predicao': data,
                'predicao': 1 if prob > 0.3 else 0,
                'probabilidade': prob
            })
    
    return pd.DataFrame(registros)


def gerar_labels_reais(predicoes: pd.DataFrame, delay_dias: int = 7) -> pd.DataFrame:
    """
    Simula chegada de labels reais (chargebacks).
    
    Labels só estão disponíveis para transações com mais de 'delay_dias'.
    """
    np.random.seed(123)
    
    hoje = datetime.now()
    cutoff = hoje - timedelta(days=delay_dias)
    
    # Só transações antigas têm label
    antigas = predicoes[predicoes['data_predicao'] <= cutoff].copy()
    
    # Simula label real (com alguma correlação com predição)
    labels = []
    for _, row in antigas.iterrows():
        # Se modelo previu fraude, 60% de chance de ser fraude real
        # Se modelo previu não-fraude, 2% de chance de ser fraude real
        if row['predicao'] == 1:
            label = np.random.choice([0, 1], p=[0.4, 0.6])
        else:
            label = np.random.choice([0, 1], p=[0.98, 0.02])
        labels.append(label)
    
    antigas['label_real'] = labels
    return antigas


def calcular_metricas(dados: pd.DataFrame) -> dict:
    """Calcula métricas de avaliação."""
    return {
        'f1': f1_score(dados['label_real'], dados['predicao']),
        'precision': precision_score(dados['label_real'], dados['predicao']),
        'recall': recall_score(dados['label_real'], dados['predicao']),
    }


def main():
    print("=" * 60)
    print("AVALIAÇÃO DE MODELO EM PRODUÇÃO")
    print("=" * 60)
    
    # ===== ETAPA 1: Simular log de predições =====
    print("\n[1] Carregando log de predições dos últimos 40 dias...")
    
    predicoes = gerar_log_predicoes(n_dias=40)
    
    print(f"    Total de predições: {len(predicoes):,}")
    print(f"    Predições positivas: {predicoes['predicao'].sum():,}")
    print(f"    Taxa de positivos: {predicoes['predicao'].mean()*100:.1f}%")
    
    # ===== ETAPA 2: Explicar o problema =====
    print("\n[2] O PROBLEMA: Ground truth atrasado")
    print()
    print("    ┌─────────────────────────────────────────────────────┐")
    print("    │  Dia 0        Dia 7-30           Dia 30+            │")
    print("    │    │              │                 │               │")
    print("    │    ▼              ▼                 ▼               │")
    print("    │ Transação     Chargeback       Podemos             │")
    print("    │ + Predição    (label real)     avaliar!            │")
    print("    └─────────────────────────────────────────────────────┘")
    print()
    print("    Não podemos avaliar predições de HOJE porque")
    print("    não sabemos ainda se eram fraude de verdade.")
    
    # ===== ETAPA 3: Obter labels disponíveis =====
    print("\n[3] Obtendo labels reais (transações com 7+ dias)...")
    
    dados_avaliacao = gerar_labels_reais(predicoes, delay_dias=7)
    
    print(f"    Transações avaliáveis: {len(dados_avaliacao):,}")
    print(f"    Transações recentes (sem label): {len(predicoes) - len(dados_avaliacao):,}")
    
    # ===== ETAPA 4: Calcular métricas =====
    print("\n[4] Calculando métricas em produção...")
    
    metricas = calcular_metricas(dados_avaliacao)
    
    print()
    print(f"    F1-Score:  {metricas['f1']:.3f}")
    print(f"    Precision: {metricas['precision']:.3f}")
    print(f"    Recall:    {metricas['recall']:.3f}")
    
    # ===== ETAPA 5: Verificar limiar =====
    LIMIAR_F1 = 0.70
    
    print(f"\n[5] Verificando limiar (F1 >= {LIMIAR_F1})...")
    
    if metricas['f1'] >= LIMIAR_F1:
        print(f"    ✓ F1 = {metricas['f1']:.3f} está OK")
    else:
        print(f"    ⚠️  F1 = {metricas['f1']:.3f} ABAIXO do limiar!")
        print("    → Disparar alerta para equipe")
        print("    → Considerar re-treinamento")
    
    # ===== ETAPA 6: Evolução temporal =====
    print("\n[6] Evolução do F1 por semana:")
    print()
    
    dados_avaliacao['semana'] = dados_avaliacao['data_predicao'].dt.isocalendar().week
    
    for semana in sorted(dados_avaliacao['semana'].unique())[-4:]:
        dados_semana = dados_avaliacao[dados_avaliacao['semana'] == semana]
        if len(dados_semana) > 100:
            f1_semana = f1_score(dados_semana['label_real'], dados_semana['predicao'])
            barra = "█" * int(f1_semana * 20)
            print(f"    Semana {semana}: {barra} {f1_semana:.2f}")
    
    print()
    print("=" * 60)
    print("Este job rodaria DIARIAMENTE para monitorar o modelo.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
