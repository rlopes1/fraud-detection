#!/usr/bin/env python3
"""
Job de Re-treinamento Semanal

Este job é executado periodicamente (ex: todo domingo às 2h) para:
1. Coletar dados recentes
2. Validar qualidade dos dados
3. Treinar novo modelo
4. Comparar com modelo em produção
5. Promover se for melhor, alertar se for pior
"""

import argparse
import pickle
import shutil
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# Caminhos padrão
MODELO_PRODUCAO = Path("models/modelo_em_producao.pkl")
MODELO_ARQUIVO = Path("models/arquivo")
DADOS_TESTE = Path("data/teste_fixo.csv")
DADOS_TREINO = Path("data/transacoes.csv")


def coletar_dados(caminho: Path = None, dias: int = 90) -> pd.DataFrame:
    """
    Coleta dados para treinamento.
    
    Em produção real: query no banco de dados
    Aqui: lê arquivo CSV ou gera dados sintéticos
    """
    log.info(f"Coletando dados dos últimos {dias} dias...")
    
    if caminho and caminho.exists():
        dados = pd.read_csv(caminho)
        log.info(f"✓ {len(dados):,} transações carregadas de {caminho}")
    else:
        # Gera dados sintéticos com padrão detectável
        np.random.seed(None)
        n = np.random.randint(40000, 50000)
        
        valor = np.random.exponential(500, n)
        hora = np.random.randint(0, 24, n)
        dia_semana = np.random.randint(0, 7, n)
        categoria = np.random.choice(['A', 'B', 'C', 'D'], n)
        
        # Padrão: fraude correlacionada com valor alto + horário noturno
        score = np.zeros(n)
        score += (valor > 800) * 0.4
        score += ((hora >= 22) | (hora <= 5)) * 0.3
        score += (categoria == 'D') * 0.2
        score += 0.02
        is_fraude = (np.random.random(n) < score).astype(int)
        
        dados = pd.DataFrame({
            'valor': valor,
            'hora': hora,
            'dia_semana': dia_semana,
            'categoria': categoria,
            'is_fraude': is_fraude
        })
        log.info(f"✓ {len(dados):,} transações geradas")
    
    return dados


def validar_dados(dados: pd.DataFrame, minimo: int = 1000) -> pd.DataFrame:
    """
    Valida e limpa os dados.
    
    Remove:
    - Valores negativos ou zero
    - Horas inválidas
    - Duplicatas
    - Linhas com NaN
    
    Falha se restar menos que o mínimo necessário.
    """
    log.info("Validando dados...")
    
    n_original = len(dados)
    
    # Limpeza
    dados = dados[dados['valor'] > 0].copy()
    dados = dados[dados['hora'].between(0, 23)]
    dados = dados.drop_duplicates()
    dados = dados.dropna()
    
    n_removidos = n_original - len(dados)
    if n_removidos > 0:
        log.info(f"  Removidos: {n_removidos:,} registros inválidos")
    
    # Validação de quantidade mínima
    if len(dados) < minimo:
        raise ValueError(f"Dados insuficientes: {len(dados)} < {minimo}")
    
    log.info(f"✓ {len(dados):,} transações válidas")
    return dados


def preparar_features(dados: pd.DataFrame):
    """
    Prepara features para o modelo.
    
    Converte categoria em one-hot encoding.
    Separa features (X) de target (y).
    """
    dados_encoded = pd.get_dummies(dados, columns=['categoria'])
    colunas_features = [c for c in dados_encoded.columns if c != 'is_fraude']
    
    X = dados_encoded[colunas_features]
    y = dados_encoded['is_fraude']
    
    return X, y


def treinar_modelo(dados: pd.DataFrame) -> RandomForestClassifier:
    """
    Treina modelo RandomForest.
    
    Configuração padrão para detecção de fraude:
    - 100 árvores
    - Profundidade máxima 10 (evita overfitting)
    """
    log.info("Treinando modelo...")
    
    X, y = preparar_features(dados)
    
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    modelo.fit(X, y)
    
    log.info("✓ Modelo treinado")
    return modelo


def obter_dados_teste() -> tuple:
    """
    Obtém dados de teste FIXOS.
    
    Importante: usar sempre os mesmos dados de teste
    para comparação justa entre modelos.
    """
    if DADOS_TESTE.exists():
        dados = pd.read_csv(DADOS_TESTE)
    else:
        # Cria conjunto de teste fixo na primeira execução
        log.info("Criando conjunto de teste fixo...")
        np.random.seed(12345)
        n = 10000
        
        valor = np.random.exponential(500, n)
        hora = np.random.randint(0, 24, n)
        dia_semana = np.random.randint(0, 7, n)
        categoria = np.random.choice(['A', 'B', 'C', 'D'], n)
        
        # Mesmo padrão do treino
        score = np.zeros(n)
        score += (valor > 800) * 0.4
        score += ((hora >= 22) | (hora <= 5)) * 0.3
        score += (categoria == 'D') * 0.2
        score += 0.02
        is_fraude = (np.random.random(n) < score).astype(int)
        
        dados = pd.DataFrame({
            'valor': valor,
            'hora': hora,
            'dia_semana': dia_semana,
            'categoria': categoria,
            'is_fraude': is_fraude
        })
        
        DADOS_TESTE.parent.mkdir(parents=True, exist_ok=True)
        dados.to_csv(DADOS_TESTE, index=False)
    
    return preparar_features(dados)


def avaliar_modelo(modelo, X_teste, y_teste) -> float:
    """Calcula F1-score do modelo."""
    y_pred = modelo.predict(X_teste)
    return f1_score(y_teste, y_pred)


def comparar_modelos(modelo_novo) -> tuple:
    """
    Compara modelo novo com modelo em produção.
    
    Retorna:
        (modelo_novo_eh_melhor, f1_atual, f1_novo)
    """
    log.info("Comparando com modelo atual...")
    
    X_teste, y_teste = obter_dados_teste()
    
    # Avalia modelo novo
    f1_novo = avaliar_modelo(modelo_novo, X_teste, y_teste)
    
    # Avalia modelo atual (se existir)
    if MODELO_PRODUCAO.exists():
        with open(MODELO_PRODUCAO, 'rb') as f:
            modelo_atual = pickle.load(f)
        f1_atual = avaliar_modelo(modelo_atual, X_teste, y_teste)
    else:
        f1_atual = 0.0
        log.info("  (Primeiro modelo - não há anterior)")
    
    log.info(f"  F1 atual: {f1_atual:.4f}")
    log.info(f"  F1 novo:  {f1_novo:.4f}")
    
    # Usa >= para preferir modelo mais recente em caso de empate
    return f1_novo >= f1_atual, f1_atual, f1_novo


def promover_modelo(modelo):
    """
    Promove modelo para produção.
    
    1. Arquiva modelo anterior com timestamp
    2. Salva novo modelo como modelo em produção
    """
    log.info("Promovendo modelo...")
    
    # Arquiva modelo anterior
    if MODELO_PRODUCAO.exists():
        MODELO_ARQUIVO.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = MODELO_ARQUIVO / f"modelo_{timestamp}.pkl"
        shutil.copy(MODELO_PRODUCAO, destino)
        log.info(f"  Anterior arquivado: {destino.name}")
    
    # Salva novo modelo
    MODELO_PRODUCAO.parent.mkdir(parents=True, exist_ok=True)
    with open(MODELO_PRODUCAO, 'wb') as f:
        pickle.dump(modelo, f)
    
    log.info("✓ Modelo em produção atualizado")


def alertar(mensagem: str, f1_atual: float = None, f1_novo: float = None):
    """
    Envia alerta para equipe.
    
    Em produção: email, Slack, PagerDuty, etc.
    """
    log.warning("=" * 50)
    log.warning(f"⚠️  ALERTA: {mensagem}")
    if f1_atual is not None and f1_novo is not None:
        log.warning(f"  F1 atual: {f1_atual:.4f}")
        log.warning(f"  F1 novo:  {f1_novo:.4f}")
        log.warning(f"  Queda:    {f1_atual - f1_novo:.4f}")
    log.warning("=" * 50)


def executar_job(usar_csv: bool = False):
    """
    Executa o job completo de re-treinamento.
    """
    log.info("=" * 50)
    log.info("JOB DE RE-TREINAMENTO")
    log.info("=" * 50)
    
    try:
        # 1. Coletar dados
        caminho = DADOS_TREINO if usar_csv else None
        dados = coletar_dados(caminho)
        
        # 2. Validar dados
        dados = validar_dados(dados)
        
        # 3. Treinar modelo
        modelo = treinar_modelo(dados)
        
        # 4. Comparar com atual
        eh_melhor, f1_atual, f1_novo = comparar_modelos(modelo)
        
        # 5. Decidir
        if eh_melhor:
            log.info("✓ Modelo novo é melhor ou igual")
            promover_modelo(modelo)
        else:
            log.warning("✗ Modelo novo é PIOR")
            alertar("Modelo novo pior que atual", f1_atual, f1_novo)
    
    except Exception as e:
        log.error(f"❌ Falha: {e}")
        alertar(str(e))
        raise
    
    finally:
        log.info("=" * 50)
        log.info("FIM DO JOB")
        log.info("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--usar-csv", action="store_true", help="Usar data/transacoes.csv")
    args = parser.parse_args()
    
    executar_job(usar_csv=args.usar_csv)
