# Mapa de locais para investigar poços

A tela principal mostra um mapa geográfico da Paraíba. Começa em um registro de Cabaceiras e permite escolher outro município com dados no cadastro.

1. Escolha a cidade e um poço cadastrado como centro.
2. Todos os pontos sugeridos da grade aparecem automaticamente, em azul e numerados. Use o botão de atualização depois de mudar o raio ou informar coordenadas.
3. Arraste o mapa e use os controles de zoom. “Ver toda a Paraíba” mostra o contexto regional.
4. Clique em qualquer número para abrir sua própria latitude e longitude no mapa. A lista visível também contém todas as coordenadas. Pontos na mesma linha podem ter a mesma latitude; seus pares latitude/longitude são distintos.
5. Baixe a lista se precisar levar as coordenadas a uma visita de campo.

Verde indica um registro com evidência histórica de produção; marrom indica situação histórica de poço seco. O fundo geográfico é OpenStreetMap, o contorno estadual é IBGE e os poços são SGB/SIAGAS.

Os pontos azuis são uma grade de hipóteses, ordenada pelo Random Forest treinado no cadastro com latitude, longitude e profundidade. A profundidade inicial vem do registro selecionado; para um lugar novo, ela é uma suposição. A pontuação não é uma probabilidade calibrada de encontrar água. Os pontos podem ultrapassar limites municipais: só o contorno estadual é usado para a restrição geográfica.

Municípios aparecem por terem registros disponíveis, e não porque já foi demonstrada viabilidade de novos poços. Essa interface não mapeia todos os terrenos do município nem recomenda perfuração. Visita técnica, avaliação hidrogeológica e confirmação em campo continuam necessárias.

O plano de campo está em uma seção visível. Após preparar as visitas, os marcadores roxos V1, V2… mostram suas localizações. O plano pode ser lido na página ou baixado como arquivo HTML; coordenadas em CSV e dados completos em JSON também ficam disponíveis. Os resultados dos 18 testes abrem na página, independentemente do carregamento do mapa geológico. Acurácia, F1 macro, matrizes de confusão e configurações dos cinco métodos aparecem abaixo do mapa, com explicações. Os antigos módulos de clima NASA e tratamento saíram da navegação principal para simplificar a tela, conforme solicitado. Os modelos e arquivos científicos anteriores foram preservados.

Verificação: execução da interface em jsdom com canvas nativo, todos os pontos gerados na abertura, correspondência de cada clique e de cada janela do mapa com suas coordenadas, pares sem duplicatas, botões reais de preparação e download, retomada após falha no carregamento, visitas no mapa, resultados independentes da rede, remoção de sugestões desatualizadas e verificações anteriores dos modelos. O carregamento das ruas pela rede e o layout em um navegador completo não foram testados neste ambiente.
