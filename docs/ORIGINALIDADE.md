# Originalidade: avaliação preliminar e contribuição a testar

Data da busca exploratória: 04/10/2026. Não se trata de revisão sistemática exaustiva e não permite afirmar que não existe trabalho igual.

## O que já tem antecedentes

| Trabalho | O que investigou | Relação com ÁguaTwin |
|---|---|---|
| Souza et al. (2023), doi:10.14393/rbcv75n0a-65381 | Seis métodos de aprendizado de máquina, vazões de 4.028 poços SIAGAS e covariáveis ambientais no norte de Minas Gerais | IA, SIAGAS e mapeamento de potencial hídrico já foram combinados |
| Vio et al. (2025), doi:10.28998/contegeo.10i.24.18434 | Árvore de decisão e 14 variáveis para identificar depósitos aluviais no Riacho do Tigre/PB | Há trabalho de IA e sensoriamento remoto relacionado à água subterrânea na Paraíba; o alvo são depósitos aluviais, não sucesso de perfuração |
| Riaz et al. (2024), doi:10.1038/s41598-024-76607-3 | Mapeamento de potencial subterrâneo com SVM/WOE e análise físico-química e bacteriológica de amostras em Muzaffarabad, Paquistão | Integrar potencial hídrico e qualidade da água também tem antecedentes |

Assim, a originalidade não pode ser sustentada apenas por usar cinco algoritmos, a API NASA, o nome “gêmeo digital”, um sensor ou um novo município.

## Contribuição principal proposta

Desenvolver e avaliar uma **estratégia de decisão para água aproveitável**, no contexto do semiárido paraibano, que combine:

1. Estimativa espacial de evidência de produção e salinidade, com avaliação de incerteza e possibilidade de abstenção em áreas sem suporte de dados.
2. Simulação calibrada do volume após tratamento, restrições de energia solar e destinação do concentrado.
3. Medições prospectivas de campo, antes e depois do tratamento, em locais separados dos usados no ajuste.
4. Comparação com escolhas baseadas somente em produção, sob o mesmo orçamento e restrições.

Essa combinação é uma hipótese de contribuição. Sua novidade precisa ser confrontada com a literatura sobre seleção de locais, dessalinização solar, otimização multicritério e gêmeos digitais para águas subterrâneas.

## Pergunta e hipóteses

**Pergunta:** ao selecionar alternativas de abastecimento, a estratégia integrada melhora o volume diário aproveitável ou o custo por m³ aproveitável em relação à seleção baseada somente em produção?

- **H0:** não há melhoria no desfecho primário predefinido, dentro da incerteza do experimento.
- **H1:** a estratégia integrada melhora esse desfecho no conjunto independente de validação.

O protocolo deve escolher antecipadamente um desfecho primário, como custo por m³ que atende aos critérios do uso estudado. Volume atendido, confiabilidade, energia e salinidade podem ser desfechos secundários. Não anunciar melhoria percentual antes de obter os resultados.

## Duas extensões opcionais

**Coleta guiada por incerteza:** testar se escolher novas medições de CE e vazão em locais onde o modelo é mais incerto reduz o número de visitas para atingir um desempenho definido, comparando com amostragem aleatória e espacial estratificada, sob custos iguais.

**Adaptação do tratamento às medições:** testar se atualizar o simulador com CE, temperatura, vazão e energia medidas melhora a previsão de volume de permeado em diferentes períodos. A CE serve ao acompanhamento de sais; a comprovação de potabilidade exige as análises pertinentes ao uso humano.

Escolher uma contribuição principal ajuda a manter o escopo compatível com um mestrado. As extensões podem virar trabalhos posteriores.

## O que o protótipo atual já oferece

Dados secundários auditados, duas tarefas de classificação, cinco comparadores, validação espacial inicial, integração climática e cenário operacional idealizado. O código deixa explícitos os dados ausentes e preserva os resultados de métodos que tiveram desempenho fraco.

## O que ainda falta demonstrar

Modelagem conjunta de utilidade, desempenho em regiões e datas independentes, calibração de incerteza, variáveis hidrogeológicas, integração temporal com sensores, calibração física do tratamento e avaliação econômica. No estágio atual, não houve descoberta confirmada de novos poços nem demonstração de água potável ou de vantagem da estratégia integrada.

## Busca a ampliar

Registrar bases, data, consultas, critérios de seleção e motivos de exclusão. Buscar artigos e dissertações com termos em português e inglês: groundwater potential; salinity; well site selection; solar reverse osmosis; digital twin; uncertainty; active learning; multiobjective optimization; SIAGAS; semi-arid Brazil; Paraíba. A avaliação de novidade depende do conteúdo dos trabalhos relevantes, não apenas da ausência de resultados para uma combinação de palavras.

## Referências verificadas

Souza et al. (2023): https://seer.ufu.br/index.php/revistabrasileiracartografia/article/view/65381

Vio et al. (2025): https://periodicos.ufal.br/contextogeografico/article/view/18434

Riaz et al. (2024): https://www.nature.com/articles/s41598-024-76607-3
