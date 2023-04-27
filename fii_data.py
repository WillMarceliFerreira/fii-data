import pandas as pd
import urllib.request
import yfinance as yf
import re
from urllib.error import HTTPError
import PySimpleGUI as sg
from threading import Thread
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fii_analyzer.log"),
        logging.StreamHandler()
    ]
)

def extrair_tabela_fundos(url):
    # Define um cabeçalho personalizado para simular uma requisição autêntica
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        # Faz a requisição com o cabeçalho personalizado
        req = urllib.request.Request(url, headers=headers)
        resposta = urllib.request.urlopen(req).read()

        # Extrai tabela
        funds_df = pd.read_html(resposta, encoding='utf-8')[0]
        return funds_df
    except HTTPError as e:
        # print(f"Erro {e.code}: {e.reason}")
        return None

def data_cleaning(funds_df):
    funds_df = funds_df.dropna(subset=['Preço Atual'])
    funds_df = funds_df.dropna(subset=['Dividend Yield'])
    funds_df = funds_df.dropna(subset=['P/VPA'])
    return funds_df

def data_transform(funds_df):
    def tratar_valor_monetario(valor_str):
        # Remove todos os caracteres não numéricos da string e converte para float
        valor_float = float(re.sub('[^0-9]', '', valor_str))/100
        return valor_float
    def tratar_valor_percentual(valor_str):
        # Remove o símbolo de percentual e converte para float
        valor_float = float(valor_str.replace('%','').replace(',','.'))
        return valor_float
    funds_df['Preço Atual'] = funds_df['Preço Atual'].apply(lambda x: tratar_valor_monetario(x) if isinstance(x, str) else x)
    funds_df['Dividendo'] = funds_df['Dividendo'].apply(lambda x: tratar_valor_monetario(x) if isinstance(x, str) else x)
    funds_df['Dividend Yield'] = funds_df['Dividend Yield'].apply(tratar_valor_percentual)
    funds_df['DY (12M) Acumulado'] = funds_df['DY (12M) Acumulado'].apply(tratar_valor_percentual)
    funds_df['Rentab. Período'] = funds_df['Rentab. Período'].apply(tratar_valor_percentual)
    funds_df['Variação Preço'] = funds_df['Variação Preço'].apply(tratar_valor_percentual)
    funds_df['P/VPA'] = funds_df['P/VPA'] / 100
    return funds_df

def buscar_info_aux(funds_df):
  def get_yahoo_info(ticker):
    try:
        fund = yf.Ticker(ticker).info
    except:
        logging.error(f"Erro ao obter informações do fundo {ticker}")
        return None
    bid = fund.get('bid', 0)
    week_52d_low = fund.get('fiftyTwoWeekLow', 0)
    week_52d_high = fund.get('fiftyTwoWeekHigh', 0)
    avg_50d = fund.get('fiftyDayAverage', 0)
    avg_200d = fund.get('twoHundredDayAverage', 0)
    avg_vol = fund.get('averageVolume', 0)
    prev_close = fund.get('regularMarketPreviousClose', 0)
    # retornar dicionario com as informações
    return {'bid': bid, 'week_52d_low': week_52d_low, 'week_52d_high': week_52d_high, 'avg_50d': avg_50d, 'avg_200d': avg_200d, 'avg_vol': avg_vol, 'prev_close': prev_close}
  def create_aux_columns(funds_df):
      funds_df['bid'] = 0
      funds_df['week_52d_low'] = 0
      funds_df['week_52d_high'] = 0
      funds_df['avg_50d'] = 0
      funds_df['avg_200d'] = 0
      funds_df['avg_vol'] = 0
      funds_df['prev_close'] = 0
      funds_df['dif_preco_ontem_hoje'] = ''
      return funds_df
  def add_preco_teto(funds_df):
    def taxa_desconto():
        url = "https://www.ibge.gov.br/explica/inflacao.php"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        valor_IPCA = soup.find_all("p", {"class": "variavel-dado"})[1].text
        valor_IPCA = float(valor_IPCA.replace(",", ".").strip("%"))
        return valor_IPCA / 100 + 0.06
    funds_df['Preço Teto'] = funds_df['Preço Atual'] * (funds_df['DY (12M) Acumulado'] / 100) / taxa_desconto()
    return funds_df
  funds_df = create_aux_columns(funds_df)
  for fundo in funds_df['Código do fundo']:
    dados_aux = get_yahoo_info(f"{fundo}.SA")
    if dados_aux is None:
      continue
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'bid'] = dados_aux['bid']
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'week_52d_low'] = dados_aux['week_52d_low']
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'week_52d_high'] = dados_aux['week_52d_high']
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'avg_50d'] = dados_aux['avg_50d']
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'avg_200d'] = dados_aux['avg_200d']
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'avg_vol'] = dados_aux['avg_vol']
    funds_df.loc[funds_df['Código do fundo'] == fundo, 'prev_close'] = dados_aux['prev_close']
    dif_preco_anterior = (funds_df.loc[funds_df['Código do fundo'] == fundo, 'Preço Atual'].iloc[0] - funds_df.loc[funds_df['Código do fundo'] == fundo, 'prev_close'].iloc[0])
    if dif_preco_anterior < 0:
      funds_df.loc[funds_df['Código do fundo'] == fundo, 'dif_preco_ontem_hoje'] = 'Desvalorização'
    elif dif_preco_anterior > 0:
      funds_df.loc[funds_df['Código do fundo'] == fundo, 'dif_preco_ontem_hoje'] = 'Valorização'
    else:
      funds_df.loc[funds_df['Código do fundo'] == fundo, 'dif_preco_ontem_hoje'] = 'Sem Alteração'
  funds_df = add_preco_teto(funds_df, )
  return funds_df

def analisar_correlacao(df, cols):
    # Seleciona as colunas desejadas
    df = df[cols]

    # Calcula a matriz de correlação
    correlacao = df.corr()

    # Armazena as correlações médias e fortes em uma lista
    correlacoes_medias_fortes = []
    correlacoes_verificadas = []
    for col in correlacao.columns:
        for index in correlacao.index:
            if index != col:
                valor = correlacao.loc[index, col]
                if valor >= 0.3:
                    correlacao_atual = (index, col, valor)
                    correlacao_invertida = (col, index, valor)
                    if correlacao_atual not in correlacoes_verificadas and correlacao_invertida not in correlacoes_verificadas:
                        correlacoes_medias_fortes.append(correlacao_atual)
                        correlacoes_verificadas.append(correlacao_atual)

    # Exibe as mensagens para as correlações médias e fortes
    for c1, c2, valor in correlacoes_medias_fortes:
        if valor < 0.7:
            logging.info(f"A correlação entre '{c1}' e '{c2}' é média: {valor:.2f}")
        else:
            logging.info(f"A correlação entre '{c1}' e '{c2}' é forte: {valor:.2f}")

def run_analise():
    url = 'https://www.fundsexplorer.com.br/ranking'
    progress_bar.update_bar(0)
    df = extrair_tabela_fundos(url)
    progress_bar.update_bar(20)
    df = df.dropna(how="all")
    df = data_cleaning(df)
    progress_bar.update_bar(40)
    df = data_transform(df)
    progress_bar.update_bar(60)
    df = buscar_info_aux(df)
    df.to_csv('fii_data.csv', index=False)
    progress_bar.update_bar(80)
    progress_bar.update_bar(100)
    logging.info('Análise concluída com sucesso!')

def start_thread():
    analise_thread = Thread(target=run_analise)
    analise_thread.start()

# Definir tema
sg.theme('Reddit')

# Layout
layout = [
    [sg.Text('Analisador de Fundos Imobiliários', font=("Helvetica", 20))],
    [sg.Text()],
    [sg.Button('Iniciar Análise', key='-INICIAR-', size=(15, 2), font=("Helvetica", 14))],
    [sg.Text()],
    [sg.ProgressBar(100, orientation='h', size=(40, 20), key='progressbar', pad=((20, 20), 0))],
]

# Janela
window = sg.Window('Analisador de Fundos Imobiliários', layout, element_justification='center')

# Loop de eventos
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '-INICIAR-':
        progress_bar = window['progressbar']
        start_thread()

window.close()

