#!/usr/bin/env python3
"""
Demo 02: Comparação de Frequências de Re-treinamento

Este script compara NA PRÁTICA o impacto de diferentes
frequências de re-treinamento na performance do modelo.

Execução:
    python demos/demo_02_frequencias_retreinamento.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score


def gerar_dados_semana(semana: int, n: int = 5000) -> pd.DataFrame:
    """
    Gera dados de uma semana com drift progressivo.
    
    Semanas 1-4: sem drift
    Semanas 5-12: drift suave
    """
    np.random.seed(semana * 100)
    
    # Drift suave (máximo 50% de mudança)
    drift = max(0, (semana - 4) * 0.05)
    drift = min(drift, 0.5)
    
    # Features base
    valor = np.random.exponential(500, n)
    hora = np.random.randint(0, 24, n)
    dia_semana = np.random.randint(0, 7, n)
    categoria = np.random.choice(['A', 'B', 'C', 'D'], n)
    
    # Padrão de fraude: valor alto + horário noturno
    # Com drift, o limiar de "valor alto" muda
    limiar_valor = 800 + drift * 400  # Limiar sobe de 800 para 1000
    
    score = np.zeros(n)
    score += (valor > limiar_valor) * 0.5
    score += ((hora >= 22) | (hora <= 5)) * 0.3
    score += 0.03
    
    is_fraude = (np.random.random(n) < score).astype(int)
    
    return pd.DataFrame({
        'valor': valor,
        'hora': hora,
        'dia_semana': dia_semana,
        'categoria': categoria,
        'is_fraude': is_fraude
    })


def preparar_features(dados: pd.DataFrame):
    """Prepara features para o modelo."""
    dados_encoded = pd.get_dummies(dados, columns=['categoria'])
    colunas = [c for c in dados_encoded.columns if c != 'is_fraude']
    return dados_encoded[colunas], dados_encoded['is_fraude']


def treinar_modelo(dados: pd.DataFrame) -> RandomForestClassifier:
    """Treina um novo modelo."""
    X, y = preparar_features(dados)
    modelo = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
    modelo.fit(X, y)
    return modelo


def simular_estrategia(nome: str, frequencia: int, semanas: int = 12) -> list:
    """
    Simula uma estratégia de re-treinamento.
    
    frequencia: re-treina a cada N semanas (0 = nunca)
    """
    # Dados iniciais para primeiro treino
    dados_treino = pd.concat([gerar_dados_semana(i) for i in range(1, 5)])
    modelo = treinar_modelo(dados_treino)
    
    resultados = []
    
    for semana in range(1, semanas + 1):
        # Gera dados da semana atual
        dados_semana = gerar_dados_semana(semana)
        X_teste, y_teste = preparar_features(dados_semana)
        
        # Avalia modelo atual
        f1 = f1_score(y_teste, modelo.predict(X_teste))
        resultados.append(f1)
        
        # Re-treina se for hora (e se frequencia > 0)
        if frequencia > 0 and semana % frequencia == 0:
            # Usa últimas 4 semanas para re-treino
            inicio = max(1, semana - 3)
            dados_treino = pd.concat([gerar_dados_semana(i) for i in range(inicio, semana + 1)])
            modelo = treinar_modelo(dados_treino)
    
    return resultados


def main():
    print("=" * 60)
    print("COMPARAÇÃO: FREQUÊNCIAS DE RE-TREINAMENTO")
    print("=" * 60)
    
    # ===== Simular diferentes estratégias =====
    print("\n[1] Simulando 12 semanas com diferentes estratégias...\n")
    
    estrategias = [
        ("Nunca re-treina", 0),
        ("Mensal (4 sem)", 4),
        ("Quinzenal (2 sem)", 2),
        ("Semanal", 1),
    ]
    
    resultados = {}
    
    for nome, freq in estrategias:
        print(f"    Simulando: {nome}...")
        resultados[nome] = simular_estrategia(nome, freq)
    
    # ===== Mostrar resultados =====
    print("\n[2] F1-Score por semana:\n")
    
    # Cabeçalho
    print("    Semana  ", end="")
    for nome, _ in estrategias:
        print(f"{nome[:12]:>14}", end="")
    print()
    print("    " + "─" * 62)
    
    # Dados
    for semana in range(12):
        print(f"    {semana+1:6}  ", end="")
        for nome, _ in estrategias:
            f1 = resultados[nome][semana]
            # Marca re-treino com *
            marca = ""
            if nome == "Semanal":
                marca = "*"
            elif nome == "Quinzenal (2 sem)" and (semana + 1) % 2 == 0:
                marca = "*"
            elif nome == "Mensal (4 sem)" and (semana + 1) % 4 == 0:
                marca = "*"
            print(f"{f1:>13.2f}{marca}", end="")
        print()
    
    print("\n    * = re-treinamento executado")
    
    # ===== Resumo =====
    print("\n[3] Resumo:\n")
    print("    Estratégia          F1 médio   F1 mínimo   Variação")
    print("    " + "─" * 52)
    
    for nome, _ in estrategias:
        valores = resultados[nome]
        media = np.mean(valores)
        minimo = np.min(valores)
        variacao = np.max(valores) - np.min(valores)
        print(f"    {nome:20} {media:8.2f}   {minimo:8.2f}   {variacao:8.2f}")
    
    # ===== Conclusão =====
    print("\n[4] CONCLUSÕES:")
    print()
    print("    • Sem re-treino: F1 cai progressivamente")
    print("    • Re-treino semanal: F1 mais estável")
    print("    • Trade-off: custo computacional vs performance")
    print()
    print("    REGRA PRÁTICA:")
    print("    'Comece com semanal, ajuste baseado em observação'")
    print()


if __name__ == "__main__":
    main()
