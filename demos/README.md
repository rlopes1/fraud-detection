# Demonstrações da Aula 3

## Ordem de Execução

### Bloco 1: Por que Modelos Degradam

```bash
python demos/demo_01_degradacao_modelo.py     # Simula degradação real
python demos/demo_02_frequencias_retreinamento.py  # Compara frequências
python demos/demo_03_avaliacao_producao.py    # Pipeline de monitoramento
```

### Bloco 2: Job de Re-treinamento

```bash
# Preparação
python scripts/gerar_dados_sinteticos.py

# Demos
python demos/demo_04_primeira_execucao.py     # Cria primeiro modelo
python demos/demo_05_segunda_execucao.py      # Comparação real
python demos/demo_06_modelo_pior.py           # Proteção da produção
python demos/demo_07_dados_corrompidos.py     # Fail fast
```

### Bloco 3: Versionamento com DVC

```bash
python demos/demo_08_antes_depois_dvc.py      # Git vs DVC
bash demos/demo_09_dvc_ciclo_completo.sh      # Ciclo completo real
```

## O que cada demo faz

| Demo | O que EXECUTA |
|------|---------------|
| 01 | Treina modelo, avalia em 6 meses com drift, mostra queda de F1 |
| 02 | Simula 12 semanas com diferentes frequências, compara métricas |
| 03 | Simula log de predições, calcula F1 com ground truth atrasado |
| 04 | Executa job real, cria primeiro modelo |
| 05 | Executa job real, compara e arquiva modelo anterior |
| 06 | Treina modelo ruim propositalmente, mostra rejeição |
| 07 | Gera dados corrompidos, mostra falha na validação |
| 08 | Cria arquivo real, calcula hash, simula crescimento de repo |
| 09 | Executa comandos DVC de verdade (init, add, push, checkout) |
