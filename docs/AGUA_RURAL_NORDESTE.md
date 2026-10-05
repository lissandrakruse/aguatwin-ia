# ÁguaTwin IA: investigação de poços e água utilizável no meio rural

Proposta de pesquisa de mestrado — v2.1, 5 de outubro de 2026. Este documento apresenta um protocolo e um protótipo; não apresenta descobertas de novos poços ou resultados de intervenção social.

## Problema e contribuição a testar

A pesquisa distingue duas decisões: onde coletar evidência para investigar um poço futuro e como obter água utilizável a partir de uma fonte já medida. O objetivo social é reduzir a falta de abastecimento e apoiar a irrigação mediante decisões que considerem produção, qualidade, energia, custos e manejo do concentrado.

Reativação e tratamento de poços existentes devem entrar na comparação. O diagnóstico CPRM de Cabaceiras de 2005 distingue condições operacionais, incluindo paralisações por problemas de equipamentos, e discute recuperação e dessalinização. Essa evidência é histórica e não informa o estado atual dos mesmos poços. Não foi transformada em novas linhas de treino nem duplicada com o cadastro SIAGAS.

A hipótese principal é que decidir pelo volume utilizável para um uso definido, sob orçamento e energia comuns, produz uma escolha mais adequada que decidir somente pela produção bruta. A hipótese secundária é que uma coleta guiada por informações do modelo obtém dados mais úteis por visita que coleta aleatória ou estratificada espacialmente. Ambas dependem de comparação prospectiva; as simulações iniciais são exemplos hipotéticos.

## Dados existentes e treino implementado

- Histórico SIAGAS/SGB: 3.022 registros para produção registrada × situação seco e 8.234 para condutividade acima de 3.000 µS/cm. Não há datas dos testes nessa extração; situação cadastral não equivale a desfecho datado de perfuração.
- Mapa hidrogeológico SGB da Paraíba, referência Brito e Paula (2019): 841 estruturas e 523 polígonos de domínio hidrolitológico. Apenas as camadas descritivas 2 e 5 foram usadas. Mapas de condutividade, produtividade e densidade de poços ficaram fora dos preditores para evitar informação derivada dos alvos. A independência temporal entre elaboração do mapa e registros históricos ainda não foi demonstrada.
- NASA POWER: chuva, temperatura e radiação solar diárias de 2024–2025. A radiação pode informar uma estimativa de energia fotovoltaica histórica. Essas séries não entram no treino de localização dos poços; chuva não comprova recarga ou uma fratura produtiva.

Os cinco métodos da v2.0 permanecem disponíveis: KNN, Random Forest, Naive Bayes gaussiano, K-means com classes atribuídas no treino e CNN 1D tabular. A v2.1 acrescenta uma comparação controlada de três conjuntos de entradas em Random Forest, com faixas de isolamento de 0, 2 e 5 km. O modelo de investigação futura exclui profundidade observada, que ainda não existe num poço novo. Os resultados completos estão em `RESULTADOS_V2_1.md` e `dist/hydro_validation.json`.

O novo modelo produz escores históricos sem calibração de probabilidade. A seleção de visitas escolhe primeiro um candidato com alto escore de produção e depois candidatos com maior dispersão entre árvores, exigindo separação de 1 km. Essa dispersão não é intervalo de confiança ou ganho de informação demonstrado. Os limiares de distância são heurísticos. Ausência de escore por falta de suporte indica necessidade de dados, sem excluir a comunidade ou concluir que falta água.

## Como transformar relatos em evidência

O projeto ainda não recebeu relatos individuais nem laudos municipais. Relatos comunitários orientam o levantamento e permanecem como pistas, sem rótulos automáticos. Textos como “poço seco”, “bomba parada” ou “água salobra” não geram classes por palavras-chave.

A ficha vazia `research/field_report_template.json` registra documento de origem, código do local, data, coordenadas e sua precisão, revisão técnica, método de produção, vazão operacional e duração do teste. Um teste datado, documentado e revisado pode constituir uma futura coorte de campo. Produção medida exige vazão positiva; seco confirmado exige teste documentado e vazão zero. Vazão ausente, equipamento avariado e evidência contraditória ficam pendentes. Capacidade específica em m³/h/m não substitui vazão em m³/h.

O auditor `import_field_reports.py` separa pistas, pendências e registros elegíveis. O estado “reviewed” é declarado por um revisor; o programa não autentica documentos ou competência técnica. Ele não anexa registros automaticamente ao treino histórico. A nova coorte tem semântica diferente da situação SIAGAS e deve reservar locais e períodos para validação independente antes de atualizar os modelos.

Uso do auditor, com uma lista JSON de fichas preenchidas:

```sh
python3 research/import_field_reports.py fichas_revisadas.json auditoria.json
```

## Validação de campo e desenho do estudo

1. Escolher município e comunidades mediante levantamento atual de interrupções, fontes disponíveis, acesso e demanda. Não foi estabelecido qual município da Paraíba é hoje o mais carente de água.
2. Pré-definir orçamento, regiões, critérios e comparação. Usar setores separados e estratos de geologia/acesso para comparar seleção pelo modelo com seleção aleatória e estratificada, sem contar o mesmo local como amostra independente em estratégias diferentes.
3. Medir posição, litologia e contexto de fraturas; considerar eletrorresistividade após avaliação hidrogeológica. Eletrorresistividade não distingue água doce por si só: salinidade e materiais argilosos também afetam respostas. Acrescentar relevo e variáveis de campo apenas em novas comparações declaradas, preservando locais de teste.
4. Medir vazão operacional, níveis estático e dinâmico e recuperação mediante teste apropriado. Medir condutividade com compensação a 25 °C, temperatura e calibração do instrumento. Obter STD e análises químicas/microbiológicas em laboratório para o uso escolhido. Uma sonda de condutividade é triagem, sem certificação de potabilidade.
5. Calibrar tratamento com volumes de entrada, permeado e concentrado, qualidade de cada corrente, energia registrada e custos reais. Registrar confiabilidade e manutenção. Destinação do concentrado precisa constar da alternativa avaliada.
6. Avaliar uma coorte independente e datada: produção, qualidade, erro de classificação e calibração. Para a coleta, comparar custo e evidência obtida por visita; para a operação, comparar volume que atende a critérios completos do uso, custo e confiabilidade.

Indicadores sociais devem ser agregados por comunidade: domicílios atendidos, dias sem abastecimento nos últimos 30 dias, tempo de coleta, custo por m³ e área irrigada. A ficha evita nomes, endereços domiciliares e informações pessoais. Os critérios da água devem ser definidos separadamente para consumo humano e para cada cultura/solo; atender apenas a um limite de sais não basta para qualquer desses usos.

## Simulador operacional e limites

A aba “Água útil e campo” compara três alternativas sob as mesmas restrições diárias de energia e orçamento. Considera energia de bombeamento pela altura total e eficiência, consumo de osmose por m³ de permeado, recuperação, rejeição de sais, custo fixo e manejo do concentrado. Conserva água e massa de sais. O volume condicional é o permeado que atende apenas ao limite experimental de STD escolhido pelo usuário.

A média solar mensal NASA informa contexto histórico, sem assegurar potência instantânea ou continuidade elétrica. O cálculo diário ideal não descreve incrustação, perdas da rede, armazenamento ou envelhecimento de membranas. A aba original explora sequência diária e reservatório. O sistema permanece um simulador exploratório, com evolução possível para gêmeo digital somente após calibração e atualização por medições de campo.

Originalidade não foi comprovada pela busca. IA para potencial hídrico, geofísica e gestão de água já têm antecedentes. Uma contribuição defensável pode estar na avaliação conjunta, prospectiva e reproduzível de coleta, tratamento e resultados sociais sob restrições locais — caso o estudo consiga demonstrá-la.

## Fontes primárias

- Brito e Paula (2019), SGB, [Mapa hidrogeológico do estado da Paraíba](https://rigeo.sgb.gov.br/handle/doc/21598); [serviço de camadas](https://geoportal.sgb.gov.br/server/rest/services/hidrologia/Mapa_Midrogeologico_Paraiba/FeatureServer).
- CPRM (2005), [Diagnóstico do município de Cabaceiras](https://rigeo.sgb.gov.br/handle/doc/15852).
- [NASA POWER — API diária](https://power.larc.nasa.gov/docs/services/api/temporal/daily/).
- [USGS — Borehole Geophysics](https://www.usgs.gov/centers/new-york-water-science-center/science/borehole-geophysics).
- [Hydrogeophysical Characterization of Fractured Aquifers for Groundwater Exploration in the Federal District of Brazil](https://repositorio.unb.br/handle/10482/43704), 2022, DOI 10.3390/app12052509.
- Souza et al. (2023), DOI [10.14393/rbcv75n0a-65381](https://doi.org/10.14393/rbcv75n0a-65381); Vio et al. (2025), DOI [10.28998/contegeo.10i.24.18434](https://doi.org/10.28998/contegeo.10i.24.18434); Riaz et al. (2024), DOI [10.1038/s41598-024-76607-3](https://doi.org/10.1038/s41598-024-76607-3).
