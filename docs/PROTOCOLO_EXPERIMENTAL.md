# Protocolo proposto: selecionar alternativas de água aproveitável

Este protocolo descreve trabalho futuro. Não relata medições ou resultados de campo já realizados.

## 1. Definir uma área e um uso

Escolher um município do semiárido paraibano após avaliar necessidade hídrica, parceiros, acesso a poços e qualidade dos registros. Começar pela avaliação de poços existentes reduz custo e permite verificar vazão e tratamento antes de estudar novas perfurações.

Definir um uso primário e seus critérios: uma cultura e solo específicos para irrigação, ou abastecimento humano com comprovação laboratorial correspondente. Analisar os dois usos em cenários separados, sem transferir automaticamente critérios de irrigação para consumo humano.

## 2. Separar treino, calibração e validação

Preservar identificadores de poços, coordenadas, datas de teste e de coleta, métodos, unidades, incerteza instrumental e dados ausentes. Unificar registros duplicados. Documentar divergências entre situação cadastral e ensaio de produção.

Criar grupos espaciais coerentes com a escala dos processos e investigar faixa de isolamento. Reservar regiões e um período prospectivo para validação; manter esses dados fora de seleção de variáveis, hiperparâmetros e calibração. Na seleção de hiperparâmetros, usar avaliação interna ao treino.

A amostra SIAGAS atual contém seleção histórica e datas de medição incompletas. O rótulo `Seco` é situação cadastral e não deve ser anunciado como desfecho confirmado de perfuração.

## 3. Enriquecer os preditores

Acrescentar litologia, estruturas/fraturas, relevo, drenagem e características hidrogeológicas com fontes e escalas documentadas. Para CNN com imagens, preparar recortes georreferenciados de imagens ou camadas raster, mantendo cada local e seu entorno no mesmo grupo. A CNN atual é um comparador tabular experimental.

Usar dados climáticos NASA somente com significado temporal e espacial adequado. Séries recentes não devem ser ligadas arbitrariamente a testes históricos sem data. A API POWER é útil no cenário solar e de demanda, mas sua grade não resolve a posição de uma fratura ou a localização exata de água subterrânea.

## 4. Obter medições para calibração

Registrar CE com compensação de temperatura e procedimento de calibração, temperatura, vazão volumétrica e condições do teste de bombeamento. Vazão específica não deve ser tratada como vazão em m³/h. Validar os indicadores de salinidade por análises de referência e medir íons relevantes ao uso escolhido.

No sistema de tratamento, medir vazão e CE de alimentação, permeado e concentrado, recuperação, energia consumida, pressões e variabilidade temporal. Incluir bombeamento e armazenamento energético quando fizerem parte da instalação. Comparar o modelo de massa e energia com os dados antes de usá-lo na decisão.

Uma medição de CE ou um conjunto de sensores não certifica potabilidade. Para uso humano, a comprovação química e microbiológica é etapa específica.

## 5. Definir estratégias de decisão

Comparar, sob as mesmas restrições:

- **Referência A:** priorização baseada somente em produção observada ou estimada.
- **Referência B:** produção com restrição simples de salinidade.
- **Proposta:** produção, salinidade e tratamento, com energia e custo, incorporando incerteza e domínio de aplicabilidade.

Usar uma etapa de análise retrospectiva com dados existentes e, depois, validação prospectiva. Não perfurar como parte de uma recomendação automática do protótipo. Locais novos exigem estudo hidrogeológico e verificação geofísica apropriada, além das condições locais de implantação.

## 6. Escolher o desfecho e o plano de análise antes da validação

Uma opção de desfecho primário é o custo por m³ de água que atende aos critérios definidos para o uso. Documentar equipamentos, operação, energia, recuperação, rejeito e manutenção incluídos nesse custo. Outra opção é o volume diário aproveitável para um orçamento fixo. Escolher uma, evitando trocar o objetivo após ver os resultados.

Informar desempenho preditivo, erros de simulação, confiabilidade temporal e incerteza das diferenças entre estratégias. Fazer análises de sensibilidade para parâmetros ainda incertos. Definir o tamanho da amostra com dados piloto e viabilidade de campo; não fixar um número como garantia de poder estatístico.

Para classificação, manter métricas por classe e acurácia balanceada. Para probabilidades, avaliar calibração em dados independentes. Para vazão e salinidade contínuas, usar métricas apropriadas às unidades. Para seleção de locais, avaliar o desfecho decisório, e não somente a acurácia do classificador.

## 7. Registrar conclusões e limites

Se não houver melhoria, relatar esse resultado. Distinguir estimativas, cenários, observações históricas e novas medições. Disponibilizar código, versões dos dados e protocolo quando o responsável definir condições de divulgação.

O resultado esperado é um experimento verificável sobre uma contribuição proposta, sem pressupor que a integração será superior ou inédita.
