# auctions
Projeto de integração de dados imóveis em leilões


## Diretório da aplicação

``` /app ```

## Efetuando download com WGET

``` wget https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_TO.csv?27030242 ```


## Sobre o projeto

A ideia inicial é efetuar o donwload dos arquivos da caixa todos os dias pela manhã e com isso efetuar o insert na base de dados PGSQL

Após isso, iremos com a *GOOGLE PLACES API*, efetuarmos o enriquecimentos dos dados, buscando lugaremos próximos bem como a média de valores dos imóveis ao redor do endereço de cada imóvel listado na base de dados.

google-chrome --headless --no-sandbox --disable-gpu --dump-dom https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_TO.csv?27030242