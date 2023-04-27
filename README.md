# README.md

## Analisador de Fundos Imobiliários

Este projeto tem como objetivo analisar Fundos Imobiliários (FIIs) listados na B3. Ele extrai informações de fundos disponíveis no site [Funds Explorer](https://www.fundsexplorer.com.br/ranking) e adiciona informações complementares do Yahoo Finance.

### Bibliotecas Utilizadas

- pandas
- urllib
- yfinance
- re
- PySimpleGUI
- threading
- requests
- BeautifulSoup
- logging

### Funcionalidades

- Extração de dados dos fundos imobiliários
- Limpeza e transformação dos dados
- Busca de informações complementares no Yahoo Finance
- Interface gráfica simples para iniciar a análise

### Como executar

1. Instale as bibliotecas necessárias usando o comando:

```bash
pip install pandas urllib yfinance re PySimpleGUI threading requests BeautifulSoup logging
```

2. Execute o script Python:

```bash
python analisador_fundos_imobiliarios.py
```

3. Clique no botão "Iniciar Análise" para começar a análise dos fundos imobiliários. O progresso será exibido na barra de progresso.

Após a análise ser concluída com sucesso, um arquivo CSV chamado fii_data.csv será criado com as informações dos fundos imobiliários analisados.