# ÁguaTwin IA — resultados v2.1

Avaliação histórica reproduzida em 5 de outubro de 2026. Dados públicos reais; sem resultados prospectivos de perfuração ou relatos comunitários coletados.

## Comparação pré-definida

Random Forest com 64 árvores, profundidade máxima 6, mínimo de 5 observações por folha, `balanced_subsample`, semente 42. Mesmos cinco grupos espaciais da v2.0, células de 0,04°. Para cada faixa, retiram-se do treino todos os pontos mais próximos que 0, 2 ou 5 km de qualquer observação do teste. Categorias são codificadas somente no treino, com tratamento de categoria desconhecida. Conjuntos de entradas, parâmetros e faixas foram fixados antes dos testes, sem seleção do melhor resultado.

| Tarefa | Entradas | Isolamento (km) | Acurácia balanceada | Avaliados |
|---|---|---:|---:|---:|
| Produção × seco | Cadastro com profundidade | 0 | 69.35% | 3022 |
| Produção × seco | Cadastro + geologia | 0 | 67.61% | 3022 |
| Produção × seco | Geologia sem profundidade | 0 | 63.38% | 3022 |
| Produção × seco | Cadastro com profundidade | 2 | 70.31% | 3022 |
| Produção × seco | Cadastro + geologia | 2 | 69.18% | 3022 |
| Produção × seco | Geologia sem profundidade | 2 | 61.21% | 3022 |
| Produção × seco | Cadastro com profundidade | 5 | 67.48% | 3022 |
| Produção × seco | Cadastro + geologia | 5 | 65.92% | 3022 |
| Produção × seco | Geologia sem profundidade | 5 | 59.25% | 3022 |
| CE > 3.000 µS/cm | Cadastro com profundidade | 0 | 77.23% | 8234 |
| CE > 3.000 µS/cm | Cadastro + geologia | 0 | 77.01% | 8234 |
| CE > 3.000 µS/cm | Geologia sem profundidade | 0 | 77.27% | 8234 |
| CE > 3.000 µS/cm | Cadastro com profundidade | 2 | 77.07% | 8234 |
| CE > 3.000 µS/cm | Cadastro + geologia | 2 | 76.50% | 8234 |
| CE > 3.000 µS/cm | Geologia sem profundidade | 2 | 76.93% | 8234 |
| CE > 3.000 µS/cm | Cadastro com profundidade | 5 | 76.85% | 8234 |
| CE > 3.000 µS/cm | Cadastro + geologia | 5 | 76.32% | 8234 |
| CE > 3.000 µS/cm | Geologia sem profundidade | 5 | 76.85% | 8234 |

Todos os registros têm previsão fora do treino em cada configuração: 3.022 para produção e 8.234 para condutividade. Confusões, sensibilidade por classe, cobertura, tamanhos de treino e distâncias mínimas por grupo estão no JSON completo.

## Interpretação

A inclusão dessas camadas regionais não melhorou a classificação histórica de produção. O modelo sem profundidade tem menor acurácia balanceada nessa tarefa. Ele foi escolhido para exploração de pontos novos porque não exige uma profundidade já medida, e não por apresentar a melhor métrica. A avaliação da salinidade varia pouco entre as configurações e não constitui diagnóstico de potabilidade.

O cenário sem faixa recalculado usa entradas numéricas diretamente no Random Forest; a v2.0 usava padronização. Pequenas diferenças numéricas de implementação não devem ser interpretadas como ganho científico. As outras tarefas e os cinco métodos originais são preservados.

## Proveniência geológica e geometria

Foram obtidas 841 estruturas (camada 2) e 523 polígonos de domínio hidrolitológico (camada 5), do mapa SGB com referência de 2019. A fonte consultada foi congelada em `2026-10-05T10:24:50.115113+00:00`. Fonte EPSG:4674, resposta EPSG:4326. Camadas derivadas de produtividade, condutividade e densidade não entram como preditores. Independência temporal entre elaboração do mapa e observações históricas não foi demonstrada.

A simplificação preserva topologia com tolerância de 0.0005 graus; coordenadas são arredondadas a seis casas quando válidas. Houve 1 reparo de geometria autointersectante por `make_valid`, com mudança de área desprezível registrada, e 2 casos mantidos em precisão completa para evitar invalidade no arredondamento. Arquivos brutos, hashes e operações constam da fonte ZIP e da proveniência. Python e JavaScript consultam a mesma geometria derivada.

A distância às estruturas usa projeção equiretangular local em torno de −7,15°, −36,5°, com 111,195 km por grau. É aproximação regional, sem precisão de levantamento. Proximidade de estrutura mapeada não demonstra conexão hidráulica nem presença de água doce. Domínios próximos de fronteiras precisam de confirmação de campo.

## Planejamento e simulador

A grade de investigação testa até 28 pontos no raio escolhido, dentro da Paraíba. Exige suporte próximo aos dois históricos, distância de 150 m a 5 km de um registro de produção e até 5 km de um registro de condutividade; sobreposições ou falta de domínio são excluídas da pontuação. Isso delimita a exploração pelo protótipo, sem demonstrar ausência de água nos pontos excluídos. Até seis visitas são propostas com separação de 1 km: maior escore de produção primeiro, depois dispersão das árvores. Escores não foram calibrados e dispersão não é intervalo de confiança. Benefícios de custo ou descoberta não foram medidos.

As alternativas A/B/C são hipotéticas. Com 18 kWh/dia e R$ 80/dia, o exemplo seleciona A pela maior produção bruta e B pelo maior volume condicional após tratamento. A regra de produção mais sais na entrada não seleciona alternativa nesse exemplo. Todos recebem as mesmas restrições. O modelo conserva volume e massa de sais, inclui energia de bombeamento e osmose e custos informados. O critério de 500 mg/L é uma entrada experimental; não certifica água potável ou adequada a uma cultura. Custos e parâmetros exigem calibração.

## Verificação e limitações

`npm test` executa comparações independentes de previsões Python/JavaScript, validação de suporte, distâncias de isolamento, balanços e restrições operacionais, auditoria de relatos, execução DOM e contratos da API NASA. Os relatórios de execução ficam em `research/qa_result.json` e `research/qa_v2_1.json`. A verificação DOM usa jsdom e canvas nativo; não demonstra funcionamento da geofísica ou validação de campo, e não substitui inspeção completa de layout em navegadores.

Persistem viés de seleção cadastral, datas ausentes, classes de situação histórica, possível dependência entre mapa e cadastro, parâmetros regionais e ausência de relevo ou medições geofísicas. Não há rótulos gerados de narrativas, participantes coletados, resultado de novos poços, eficácia social demonstrada ou ineditismo comprovado. O protocolo prospectivo é descrito em `AGUA_RURAL_NORDESTE.md`.
