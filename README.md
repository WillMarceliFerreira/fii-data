# Analisador de Fundos Imobiliários

Este projeto é um analisador de fundos imobiliários que extrai dados do site [Funds Explorer](https://www.fundsexplorer.com.br/ranking) e realiza diversas análises, como verificar informações adicionais do Yahoo Finance, calcular o preço teto e analisar as correlações entre os fundos. O resultado é armazenado em um arquivo CSV.

## Requisitos

- Python 3.6 ou superior
- Pandas
- urllib
- yfinance
- re
- PySimpleGUI
- threading
- requests
- BeautifulSoup

## Instalação

1. Clone este repositório ou baixe o arquivo .zip
2. Instale as dependências necessárias:

**pip install pandas urllib3 yfinance re PySimpleGUI requests beautifulsoup4**

## Como usar

1. Execute o arquivo `analisador_fundos.py`
2. Clique no botão "Iniciar Análise"
3. Aguarde a conclusão da análise e verifique o arquivo gerado `fii_teste.csv`

## Funções

- `extrair_tabela_fundos(url)`: Extrai a tabela de fundos do site Funds Explorer
- `data_cleaning(funds_df)`: Limpa os dados ausentes do DataFrame
- `data_transform(funds_df)`: Transforma os dados do DataFrame
- `buscar_info_aux(funds_df)`: Busca informações adicionais do Yahoo Finance
- `run_analise()`: Executa a análise completa e salva o resultado em um arquivo CSV