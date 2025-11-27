#!/bin/bash
# Demo 09: Ciclo Completo com DVC
#
# Este script executa os comandos DVC DE VERDADE.
# Mostra o ciclo completo de versionamento.
#
# Pré-requisitos:
#   - Git instalado
#   - DVC instalado (pip install dvc)
#   - Dados gerados (python scripts/gerar_dados_sinteticos.py)
#
# Execução:
#   cd fraud-detection
#   bash demos/demo_09_dvc_ciclo_completo.sh

set -e  # Para se der erro

echo "============================================================"
echo "CICLO COMPLETO COM DVC"
echo "============================================================"
echo

# Verifica pré-requisitos
echo "[0] Verificando pré-requisitos..."

if ! command -v git &> /dev/null; then
    echo "    ❌ Git não encontrado"
    exit 1
fi
echo "    ✓ Git OK"

if ! command -v dvc &> /dev/null; then
    echo "    ❌ DVC não encontrado (pip install dvc)"
    exit 1
fi
echo "    ✓ DVC OK"

if [ ! -f "data/transacoes.csv" ]; then
    echo "    ⚠️  Gerando dados..."
    python scripts/gerar_dados_sinteticos.py
fi
echo "    ✓ Dados OK"

echo
echo "------------------------------------------------------------"
echo "[1] SETUP: Inicializar DVC"
echo "------------------------------------------------------------"
echo

# Inicializa Git se necessário
if [ ! -d ".git" ]; then
    echo "$ git init"
    git init
    echo
fi

# Inicializa DVC
if [ ! -d ".dvc" ]; then
    echo "$ dvc init"
    dvc init
    echo
    
    # Configura storage local (para demo)
    echo "$ dvc remote add -d storage /tmp/dvc-storage-demo"
    mkdir -p /tmp/dvc-storage-demo
    dvc remote add -d storage /tmp/dvc-storage-demo
    echo
fi

# Commit inicial
echo "$ git add .dvc .dvcignore"
git add .dvc .dvcignore 2>/dev/null || true

echo "$ git commit -m 'Inicializa DVC'"
git commit -m "Inicializa DVC" 2>/dev/null || echo "    (já commitado)"

echo
echo "------------------------------------------------------------"
echo "[2] VERSIONAR DADOS v1"
echo "------------------------------------------------------------"
echo

echo "Tamanho do arquivo:"
echo "$ wc -l data/transacoes.csv"
wc -l data/transacoes.csv
echo

echo "$ dvc add data/transacoes.csv"
dvc add data/transacoes.csv
echo

echo "Arquivo .dvc criado:"
echo "$ cat data/transacoes.csv.dvc"
cat data/transacoes.csv.dvc
echo

echo "$ git add data/transacoes.csv.dvc data/.gitignore"
git add data/transacoes.csv.dvc data/.gitignore

echo "$ git commit -m 'Dados v1'"
git commit -m "Dados v1" 2>/dev/null || echo "    (já commitado)"

echo
echo "$ dvc push"
dvc push
echo

echo
echo "------------------------------------------------------------"
echo "[3] TREINAR E VERSIONAR MODELO v1"
echo "------------------------------------------------------------"
echo

echo "$ python demo_job_retreinamento.py --usar-csv"
python demo_job_retreinamento.py --usar-csv
echo

echo "$ dvc add models/modelo_em_producao.pkl"
dvc add models/modelo_em_producao.pkl
echo

echo "$ git add models/modelo_em_producao.pkl.dvc models/.gitignore"
git add models/modelo_em_producao.pkl.dvc models/.gitignore

echo "$ git commit -m 'Modelo v1'"
git commit -m "Modelo v1" 2>/dev/null || echo "    (já commitado)"

echo "$ dvc push"
dvc push
echo

echo
echo "------------------------------------------------------------"
echo "[4] SIMULAR NOVA SEMANA (adicionar dados)"
echo "------------------------------------------------------------"
echo

echo "$ cat data/novembro.csv >> data/transacoes.csv"
cat data/novembro.csv >> data/transacoes.csv

echo "$ wc -l data/transacoes.csv"
wc -l data/transacoes.csv
echo

echo "$ dvc add data/transacoes.csv"
dvc add data/transacoes.csv

echo "$ git add data/transacoes.csv.dvc"
git add data/transacoes.csv.dvc

echo "$ git commit -m 'Dados v2'"
git commit -m "Dados v2" 2>/dev/null || echo "    (já commitado)"

echo "$ dvc push"
dvc push
echo

echo
echo "------------------------------------------------------------"
echo "[5] RE-TREINAR E VERSIONAR MODELO v2"
echo "------------------------------------------------------------"
echo

echo "$ python demo_job_retreinamento.py --usar-csv"
python demo_job_retreinamento.py --usar-csv
echo

echo "$ dvc add models/modelo_em_producao.pkl"
dvc add models/modelo_em_producao.pkl

echo "$ git add models/modelo_em_producao.pkl.dvc"
git add models/modelo_em_producao.pkl.dvc

echo "$ git commit -m 'Modelo v2'"
git commit -m "Modelo v2" 2>/dev/null || echo "    (já commitado)"

echo "$ dvc push"
dvc push
echo

echo
echo "------------------------------------------------------------"
echo "[6] VERIFICAR HISTÓRICO"
echo "------------------------------------------------------------"
echo

echo "$ git log --oneline"
git log --oneline
echo

echo
echo "------------------------------------------------------------"
echo "[7] NAVEGAR NO TEMPO (voltar para v1)"
echo "------------------------------------------------------------"
echo

echo "Salvando hash do commit 'Dados v1'..."
HASH_V1=$(git log --oneline | grep "Dados v1" | cut -d' ' -f1)
echo "Hash: $HASH_V1"
echo

if [ -n "$HASH_V1" ]; then
    echo "$ git checkout $HASH_V1 -- data/transacoes.csv.dvc"
    git checkout $HASH_V1 -- data/transacoes.csv.dvc
    
    echo "$ dvc checkout"
    dvc checkout
    
    echo
    echo "Verificando (deve ter voltado para ~150k linhas):"
    echo "$ wc -l data/transacoes.csv"
    wc -l data/transacoes.csv
    echo
    
    echo "Restaurando para versão atual..."
    echo "$ git checkout HEAD -- data/transacoes.csv.dvc"
    git checkout HEAD -- data/transacoes.csv.dvc
    
    echo "$ dvc checkout"
    dvc checkout
    
    echo
    echo "$ wc -l data/transacoes.csv"
    wc -l data/transacoes.csv
fi

echo
echo "============================================================"
echo "CICLO COMPLETO FINALIZADO!"
echo "============================================================"
echo
echo "O que conseguimos:"
echo "  ✓ Versionar dados grandes sem inchar o Git"
echo "  ✓ Vincular código + dados + modelo"
echo "  ✓ Navegar entre versões"
echo "  ✓ Reprodutibilidade garantida"
echo
