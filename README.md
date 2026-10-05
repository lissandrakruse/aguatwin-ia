# ÁguaTwin IA

Protótipo de pesquisa aplicada para investigar poços na Paraíba, comparar cinco métodos de aprendizado de máquina e simular água, salinidade e energia com contexto climático NASA POWER.

[Abrir o simulador](https://aguatwin-ia.fuganti.chatgpt.site) — o acesso inicial ao site é privado. Este repositório também foi criado como privado.

## O que está implementado

- Comparação de KNN, Random Forest, Gaussian Naive Bayes, K-means e CNN 1D em duas tarefas separadas.
- Hipóteses de locais: uma grade de candidatos próximos é ordenada pelo escore do Random Forest. Os pontos precisam de investigação hidrogeológica e geofísica em campo.
- Consulta da API NASA POWER por coordenadas para chuva, temperatura do ar e radiação solar em 2024–2025.
- Cenários diários de água, osmose reversa, reservatório, irrigação e limite de energia solar.
- Download dos dados, previsões de validação e código do treino.

## Dados e resultados iniciais

Consulta pública SGB/SIAGAS em **04/10/2026**, com duas amostras:

| Tarefa | Registros | Municípios | Definição |
|---|---:|---:|---|
| Produção registrada × situação seco | 3.022 | 204 | 2.677 com vazão específica positiva; 345 com situação `Seco` sem vazão específica positiva |
| Salinidade | 8.234 | 223 | 5.663 com CE ≤ 3 dS/m; 2.571 com CE > 3 dS/m |

Na tarefa de produção, 24 registros que combinavam situação `Seco` e vazão específica positiva foram excluídos por contradição. A ausência de dados de produção não foi convertida em poço seco. A situação cadastral não informa, por si só, o resultado de uma nova perfuração.

As entradas dos cinco modelos originais (v2.0) são **latitude, longitude e profundidade do poço**. O Random Forest geológico da v2.1 pode avaliar locais futuros sem profundidade observada. Para um ponto novo, a profundidade é um cenário escolhido, sem interpretação causal de quanto se deveria perfurar. NASA POWER alimenta o cenário operacional; **ainda não é preditor dos modelos de poços**.

Cinco partições de validação espacial usam células de 0,04°. A padronização e a associação dos grupos K-means às classes são ajustadas somente no treino. Todos os métodos usam os mesmos grupos de teste. A tabela apresenta acurácia balanceada calculada a partir das previsões fora do treino:

| Método | Produção × seco | Salinidade |
|---|---:|---:|
| KNN | 53,2% | 74,0% |
| Random Forest | 69,3% | 77,2% |
| Naive Bayes | 49,5% | 72,1% |
| K-means | 50,0% | 50,0% |
| CNN 1D | 68,1% | 75,9% |

Esses percentuais medem a classificação da amostra histórica. Não são probabilidades de encontrar água. K-means é um comparador de agrupamento com associação de classe pela maioria do treino. A CNN convolui três variáveis tabulares ordenadas, sem imagens de satélite nesta versão.

## Executar o simulador localmente

Requer Python 3 para servir os arquivos. As inferências já treinadas são executadas no navegador:

```sh
python3 -m http.server 8000 --directory dist
```

Abra `http://localhost:8000`. Para a consulta climática por coordenadas, é necessário acesso à Internet. O site usa a API pública NASA POWER.

## Reproduzir o treino com a amostra congelada

Requer Python 3.12. Os dois arquivos de dados preparados estão em `research/paraiba_dataset.json` e `research/potential_dataset.json`.

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 python3 research/compare_five_models.py
OPENBLAS_NUM_THREADS=1 python3 research/reference_predictions.py
```

Use o Python do ambiente virtual, ativando-o ou substituindo `python3` por `.venv/bin/python` nos comandos acima. A etapa de treino grava os modelos, CSVs e relatório de validação em `dist/`.

Para fazer uma nova consulta ao cadastro, execute `fetch_paraiba.py`, `prepare_state_dataset.py` e `fetch_potential.py` nessa ordem, antes do treino. O cadastro pode mudar; os scripts originais e seus metadados correspondem ao experimento de 04/10/2026. Uma nova consulta precisa registrar sua própria data de acesso e manter uma nova versão da amostra.

## Verificação realizada

O protótipo passou por verificação numérica dos gradientes da CNN, comparação de **240 previsões** entre Python e JavaScript, testes de conservação de água e sais, domínio geográfico dos candidatos, respostas NASA válidas e inválidas e ações WebMCP. O ambiente de verificação usou DOM e canvas nativo; não constitui validação hidrogeológica nem teste de campo. Veja `research/qa_result.json`.

### Reproduzir a verificação em JavaScript

Com Node.js 22.12 ou superior e npm:

```sh
npm install
npm test
```

O teste executa os casos numéricos no DOM, compara as referências Python exportadas e usa respostas NASA controladas para avaliar sucesso e falha. Ele não substitui teste visual em navegador nem validação de campo. Para regenerar as referências antes do teste, execute `research/reference_predictions.py` com as dependências Python instaladas.

## Hipótese de contribuição para o mestrado

**Pergunta proposta:** uma estratégia que considera produção, qualidade e tratamento prioriza locais com maior volume aproveitável sob restrições de energia, em comparação com uma estratégia que considera somente produção?

Veja [a análise de originalidade](docs/ORIGINALIDADE.md) e [o protocolo experimental proposto](docs/PROTOCOLO_EXPERIMENTAL.md). A integração decisória exploratória foi acrescentada na v2.1; a validação prospectiva descrita nesses documentos continua planejada. O protótipo atual ainda não demonstrou originalidade científica nem eficácia dessa estratégia conjunta.

## Estrutura

- `dist/`: simulador pronto, modelos treinados, dados exportados e relatório de validação.
- `research/`: treino, coleta, preparação, amostras congeladas e registros de verificação.
- `docs/`: proposta de pesquisa e artigo inicial v1.1, restrito ao estudo piloto de Cabaceiras. O PDF v1.1 antecede a comparação estadual v2.0; seus resultados não devem ser atribuídos à nova comparação.

## Limites da interpretação

Faltam datas de medição e validação independente. Os cinco métodos originais não usam geologia nem isolamento entre células vizinhas. A v2.1 acrescenta um Random Forest com geologia regional e faixas de 0, 2 e 5 km, mantendo os resultados completos e suas limitações. A amostra cadastral não representa uma seleção aleatória de todo o estado. A regra de 5 km do registro mais próximo é um limite prático de exploração, sem garantia de aplicabilidade hidrogeológica.

CE indica salinidade e não certifica potabilidade. O cenário operacional ainda precisa de calibração do tratamento e da energia, inclusive bombeamento, incrustação e armazenamento. O sistema é um simulador exploratório com possibilidade de evolução para gêmeo digital calibrado em campo.

## Fontes principais

- [SGB/SIAGAS — cadastro de poços](https://geoportal.sgb.gov.br/server/rest/services/Hosted/siagas_web/FeatureServer/1)
- [NASA POWER — documentação da API diária](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [IBGE — malha simplificada da Paraíba](https://servicodados.ibge.gov.br/api/v3/malhas/estados/25?formato=application/vnd.geo%2Bjson&qualidade=minima)
- Souza et al. (2023), [modelagem do potencial hídrico no norte de Minas Gerais](https://doi.org/10.14393/rbcv75n0a-65381).
- Vio et al. (2025), [depósitos aluviais no Riacho do Tigre/PB](https://doi.org/10.28998/contegeo.10i.24.18434).
- Riaz et al. (2024), [potencial de água subterrânea e qualidade da água](https://doi.org/10.1038/s41598-024-76607-3).

O código ainda não recebeu uma licença de distribuição escolhida pelo responsável. As fontes de dados mantêm sua autoria e seus próprios termos.


## Atualização v2.1 — investigação e contribuição rural

A versão 2.1 acrescenta o mapa hidrogeológico oficial da Paraíba, treino Random Forest sem profundidade para locais futuros e 18 comparações com/sem geologia e faixas de isolamento espacial de 0, 2 e 5 km. Acrescentar geologia regional não melhorou a classificação de produção nesta avaliação. Escores não são probabilidades calibradas; não foram descobertos novos poços.

O plano de visitas usa dispersão entre árvores e separação espacial como heurísticas a testar. A aba **Água útil e campo** compara produção bruta com volume tratado sob energia e orçamento comuns, usando exemplos iniciais hipotéticos. O volume condicional considera apenas um critério experimental de sais, sem certificar água para beber ou irrigar.

O auditor de fichas separa relatos comunitários de testes datados e revisados. Relatos ainda não foram coletados; não entram no treino atual. Falha de bomba, vazão ausente e evidência contraditória ficam pendentes. A nova coorte de campo deve reservar locais e períodos para validação independente.

- [Protocolo e hipótese social/rural](docs/AGUA_RURAL_NORDESTE.md)
- [Resultados e limitações v2.1](docs/RESULTADOS_V2_1.md)
- [Resultados completos de validação](dist/hydro_validation.json)
- [Fontes geológicas brutas compactadas](research/hydro_layers_source.zip), com URLs e hashes em [hydro_provenance.json](research/hydro_provenance.json)
- [Ficha vazia de campo](research/field_report_template.json)

Reprodução adicional:

```sh
python3 -m pip install -r requirements.txt
python3 research/fetch_hydrogeology.py
OPENBLAS_NUM_THREADS=1 python3 research/train_hydrogeology.py
python3 research/build_site.py
npm ci
npm test
```

O treino usa os datasets históricos já presentes em `research`. Para reproduzir exatamente a fonte geológica congelada, extraia `research/hydro_layers_source.zip` em `research` e execute `prepare_context` de `fetch_hydrogeology.py` com suas duas FeatureCollections e a proveniência guardada; consultar a API novamente pode alterar dados e data de acesso. Não publique fichas pessoais de campo no repositório. Software verificado não substitui validação hidrogeológica prospectiva.
