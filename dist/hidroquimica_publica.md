# Auditoria de dados hidroquímicos públicos

Consulta realizada em 05/10/2026. O inventário complementa o ÁguaTwin e não modifica os modelos ou suas métricas.

A consulta à camada pública usada pelo projeto (`Hosted/siagas_web/FeatureServer/1`) com o filtro `str_uf='PB' AND str_parametro_amostra_quimica IS NOT NULL` retornou 130 registros. Todos os parâmetros expostos nesse campo eram sólidos dissolvidos totais. A camada alternativa `Siagas_WebMap_MIL1/MapServer/0` retornou a mesma contagem. Isso descreve as exportações consultadas, não a cobertura de todas as análises do SIAGAS.

Dos 130 registros, 13 são de Cabaceiras. Suas fichas individuais foram recuperadas e auditadas. Todas apresentam sólidos dissolvidos totais, de 334 a 5.419 mg/L. A ficha 2600003189, Pocinhos, apresenta cálcio de 38,4 mg/L e magnésio de 16,03 mg/L. Uma concentração de 171,77 mg/L aparece sem nome do parâmetro e foi mantida como não identificada; não foi atribuída ao sódio. As fichas não fornecem data e código de amostra suficientes para vincular medições. Nenhuma das 13 foi considerada elegível para análise conjunta de CE e RAS.

O arquivo CSV mantém ausências vazias. Valores zero nos cabeçalhos não são tratados como medições químicas. Não se estima RAS por CE ou sólidos dissolvidos, não se atribui aptidão agrícola, e datas de cadastro e perfuração não são substitutos de datas de coleta.

## Arquivos e reprodução

- `research/chemistry/hosted_pb_raw.json.gz`: resposta congelada da camada pública.
- `research/chemistry/pages.zip`: 13 fichas individuais preservadas.
- `research/chemistry/audit.json`: resultado, fontes e hashes das fichas.
- `research/chemistry/cabaceiras_chemistry.csv`: inventário com unidades nos nomes das colunas.
- `research/audit_public_chemistry.py`: auditoria determinística, sem nova consulta.

Execute `python3 research/audit_public_chemistry.py`. O resultado esperado é 130 registros estaduais na camada, 13 fichas locais auditadas e zero fichas elegíveis para revisão conjunta de CE e RAS.

Quando forem obtidos Na, Ca e Mg identificados na mesma amostra, a conversão de mg/L para meq/L deve preceder a RAS: Na/22,989769, Ca/20,039 e Mg/12,1525. A fórmula é RAS = Na / raiz((Ca + Mg)/2), com os três íons em meq/L. Medições incompletas permanecem indeterminadas.

## Relação com o manuscrito

O manuscrito enviado descreve avaliação v2.2 e módulo agrícola v2.3. O repositório consultado em 05/10/2026 contém a versão 2.1.0 e comparação de cinco modelos mais Random Forest hidrogeológico. Este suplemento não comprova os resultados de regressão logística e gradient boosting apresentados no manuscrito. A correspondência entre versões deve ser resolvida antes da submissão.

O livro de Francisco et al. (2025), disponível no repositório da UFCG, descreve 460 poços históricos e publica uma tabela de águas superficiais. A linha Cabaceiras dessa tabela não foi incorporada como água de poço. O download institucional do PDF não pôde ser concluído nesta consulta; os 460 registros individuais não foram recuperados.

## Fontes

- SGB/SIAGAS: https://geoportal.sgb.gov.br/server/rest/services/Hosted/siagas_web/FeatureServer/1
- SGB/SIAGAS: https://geoportal.sgb.gov.br/server/rest/services/Siagas_WebMap_MIL1/MapServer/0
- Fichas: https://siagasweb.sgb.gov.br/layout/detalhe.php?ponto=2600003189 (demais URLs em audit.json).
- BRITO, Adson Monteiro; PAULA, Thiago Luiz Feijó de. Mapa hidrogeológico do estado da Paraíba. CPRM, 2019. Escala 1:500.000. https://rigeo.sgb.gov.br/handle/doc/21598
- UFCG: https://dspace.sti.ufcg.edu.br/handle/riufcg/43148

Dados secundários públicos atribuídos ao SGB. Este release não concede uma licença nova aos dados de terceiros.
