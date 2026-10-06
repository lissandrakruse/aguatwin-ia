# Correspondência do manuscrito Caatinga com o ÁguaTwin IA

Atualizado em 6 de outubro de 2026. Manuscrito em preparação; sem afirmação de submissão, aceite ou publicação.

Título: **Triagem de poços para irrigação na Paraíba por aprendizado de máquina e validação espacial**.

## Experimento do artigo

A configuração é `pre_drill` em `research/train_hydrogeology.py`, com faixas de isolamento de 0, 2 e 5 km. O resultado principal usa 5 km. Preditores: latitude, longitude, `log1p` da distância em quilômetros às estruturas e domínio hidrolitológico codificado por one-hot. Profundidade observada, clima NASA POWER e os demais métodos do protótipo ficam fora deste experimento.

Random Forest: 64 árvores, profundidade máxima 6, mínimo de 5 observações por folha, `balanced_subsample`, semente 42, `n_jobs=1`. Categorias são aprendidas somente no treino; categorias desconhecidas no teste são ignoradas pelo codificador. Ausência de domínio recebe `__unmapped__`; sobreposições usam o primeiro índice de polígono ordenado. Foram registrados 4 casos sem domínio e 3 sobreposições na produção, e 13 casos sem domínio e 11 sobreposições na salinidade.

## Resultados

| Tarefa | Isolamento (km) | Acurácia balanceada (%) | F1 macro |
|---|---:|---:|---:|
| Produção | 0 | 63.4 | 0.533 |
| Produção | 2 | 61.2 | 0.527 |
| Produção | 5 | 59.2 | 0.534 |
| Salinidade | 0 | 77.3 | 0.709 |
| Salinidade | 2 | 76.9 | 0.710 |
| Salinidade | 5 | 76.9 | 0.711 |

Matrizes principais: produção `[[157,188],[723,1954]]`, ordem seco/produtivo; salinidade `[[3594,2069],[251,2320]]`, ordem CE ≤ 3 / CE > 3 dS m⁻¹. Linhas são classes observadas; colunas, previstas.

## Partições principais de 5 km

| Tarefa | Partição | Treino antes | Treino após | Teste |
|---|---:|---:|---:|---:|
| Produção | 1 | 2417 | 1417 | 605 |
| Produção | 2 | 2417 | 1385 | 605 |
| Produção | 3 | 2418 | 1374 | 604 |
| Produção | 4 | 2418 | 1437 | 604 |
| Produção | 5 | 2418 | 1447 | 604 |
| Salinidade | 1 | 6587 | 2625 | 1647 |
| Salinidade | 2 | 6587 | 2645 | 1647 |
| Salinidade | 3 | 6587 | 2723 | 1647 |
| Salinidade | 4 | 6587 | 2901 | 1647 |
| Salinidade | 5 | 6588 | 2781 | 1646 |

## Reprodução

Python 3.12 é o requisito documentado. `requirements.txt` fixa NumPy 2.3.5, scikit-learn 1.8.0 e Shapely 2.1.2; isso descreve as dependências de reprodução e não certifica a versão de cada execução histórica.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Use os datasets históricos presentes em `research/`. Para manter a geometria congelada, extraia `research/hydro_layers_source.zip` em `research/` e utilize `prepare_context` de `research/fetch_hydrogeology.py` com as FeatureCollections e a proveniência guardada, conforme README. Não atualize a consulta à API para representar o mesmo experimento histórico.

```sh
OPENBLAS_NUM_THREADS=1 python3 research/train_hydrogeology.py
```

O relatório agregado é `dist/hydro_validation.json`. O script não exporta atualmente as previsões individuais de cada partição do experimento geológico, apenas métricas e matrizes agregadas. A validação prospectiva e a padronização da temperatura das medições cadastrais permanecem limitações.

## Materiais do artigo

O PDF `docs/Artigo_AguaTwin_Paraiba_v1_1.pdf` corresponde ao piloto anterior. O manuscrito atual e a página de título são mantidos separadamente para a submissão editorial. A referência ao GitHub e ao simulador deve respeitar a avaliação cega.
