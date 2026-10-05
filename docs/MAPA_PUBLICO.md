# Mapa de locais para investigar poços

A tela principal mostra um mapa geográfico da Paraíba. Começa em um registro de Cabaceiras e permite escolher outro município com dados no cadastro.

1. Escolha a cidade e um poço cadastrado como centro.
2. Os primeiros dez pontos sugeridos aparecem automaticamente, em azul e numerados. Use o botão de atualização depois de mudar o raio ou informar coordenadas.
3. Arraste o mapa e use os controles de zoom. “Ver toda a Paraíba” mostra o contexto regional.
4. Clique em um número para ler latitude, longitude e a distância ao registro histórico mais próximo.
5. Baixe a lista se precisar levar as coordenadas a uma visita de campo.

Verde indica um registro com evidência histórica de produção; marrom indica situação histórica de poço seco. O fundo geográfico é OpenStreetMap, o contorno estadual é IBGE e os poços são SGB/SIAGAS.

Os pontos azuis são uma grade de hipóteses, ordenada pelo Random Forest treinado no cadastro com latitude, longitude e profundidade. A profundidade inicial vem do registro selecionado; para um lugar novo, ela é uma suposição. A pontuação não é uma probabilidade calibrada de encontrar água. Os pontos podem ultrapassar limites municipais: só o contorno estadual é usado para a restrição geográfica.

Municípios aparecem por terem registros disponíveis, e não porque já foi demonstrada viabilidade de novos poços. Essa interface não mapeia todos os terrenos do município nem recomenda perfuração. Visita técnica, avaliação hidrogeológica e confirmação em campo continuam necessárias.

A análise adicional de geologia e plano de visitas continua acessível em uma seção recolhida. Acurácia, F1 macro e configurações dos cinco métodos aparecem abaixo do mapa, com explicações. Os antigos módulos de clima NASA e tratamento saíram da navegação principal para simplificar a tela, conforme solicitado. Os modelos e arquivos científicos anteriores foram preservados.

Verificação: execução da interface em jsdom com canvas nativo, pontos gerados na abertura, correspondência entre cliques e coordenadas, remoção de sugestões desatualizadas e verificações anteriores dos modelos. O carregamento das ruas pela rede e o layout em um navegador completo não foram testados neste ambiente.
