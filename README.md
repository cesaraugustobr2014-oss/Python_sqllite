# Pipeline de Dados - Arquitetura Medalhao

Pipeline de engenharia de dados construido com **Python** e **SQLite**, seguindo a arquitetura medalhao (Bronze, Silver, Gold).

## Sobre o Projeto

Este projeto simula um pipeline ETL completo para processamento de dados de vendas e clientes de uma loja de informatica. Os dados passam por tres camadas de qualidade ate chegar em formato pronto para analise de negocio.

## Arquitetura Medalhao

```
data/raw/          -> Arquivos CSV brutos (vendas.csv, clientes.csv)
    |
    v
[BRONZE]           -> Ingestao dos dados brutos para o SQLite (sem transformacao)
    |
    v
[SILVER]           -> Limpeza: remocao de duplicados, validacao de tipos, tratamento de nulos
    |
    v
[GOLD]             -> Agregacoes de negocio: ranking de clientes, produtos e vendas por estado
```

## Fontes de Dados

- **vendas.csv** - 25 registros de vendas (com dados intencionalmente sujos: duplicados, nulos, datas invalidas)
- **clientes.csv** - 14 registros de clientes (com duplicados e campos faltantes)

## Camadas

### Bronze
- Leitura dos arquivos CSV
- Carga integral no banco SQLite sem alteracao

### Silver
- Remocao de registros duplicados
- Validacao de tipos (inteiros, floats, datas)
- Tratamento de valores nulos e invalidos
- Padronizacao de texto (lowercase, uppercase)
- Calculo de valor_total (quantidade x preco)

### Gold
- **gold_vendas_por_cliente** - Total de compras, gasto total, ticket medio e produto favorito por cliente
- **gold_ranking_produtos** - Ranking dos produtos mais vendidos por receita
- **gold_vendas_por_estado** - Vendas agregadas por estado e mes

## Como Executar

```bash
python main.py
```

O pipeline executa as tres camadas em sequencia e exibe os resultados no terminal.

## Estrutura do Projeto

```
Python_sqllite/
    data/
        raw/
            vendas.csv
            clientes.csv
    scripts/
        bronze.py
        silver.py
        gold.py
    database/
        pipeline.db      (gerado em tempo de execucao)
    main.py
    README.md
```

## Tecnologias

- Python 3 (bibliotecas nativas: csv, sqlite3, datetime)
- SQLite

## Autor

Cesar Augusto
