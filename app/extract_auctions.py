import time
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import requests
import io
import os

# Criar a pasta para armazenar os arquivos, se não existir
os.makedirs('app/files', exist_ok=True)

# Lista de estados
#estados = ["AL", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]
estados = ["AL"]

# URL base fixa
url_base = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_"

#https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_AL.csv
#https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_AL.csv
# Configurações de conexão com o PostgreSQL
db_user = "postgres"
db_password = "Last@1981"
db_host = "94.130.107.131"
db_port = "5432"
db_name = "auction_dev"

# Criar a engine de conexão
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Nome da tabela final
table_name = "public.tbl_imoveis"

# Lista para armazenar DataFrames temporários
dfs = []

# Configuração do User-Agent e outros cabeçalhos
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

# Função para tentar fazer o download com re-tentativas
def download_file(url, file_path, headers, retries=3, delay=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Levanta uma exceção em caso de erro na requisição
            with open(file_path, 'w', encoding='latin1') as file:
                file.write(response.text)
            return True
        except requests.exceptions.RequestException as e:
            print(f"Erro na tentativa {attempt + 1} ao baixar o arquivo {url}: {e}")
            time.sleep(delay)  # Aguardar antes de tentar novamente
    return False

for estado in estados:
    # Construir a URL completa para o estado
    url = f"{url_base}{estado}.csv"
    file_path = f'app/files/Lista_imoveis_{estado}.csv'

    if download_file(url, file_path, headers):
        try:
            # Ler o CSV diretamente do arquivo salvo, pulando as duas primeiras linhas
            df = pd.read_csv(file_path, sep=';', encoding='latin1', skiprows=2)

            # Adicionar coluna com o estado
            df['estado'] = estado

            # Inserir a coluna etl_load_date
            df['etl_load_date'] = datetime.now()

            # Adicionar DataFrame à lista
            dfs.append(df)

            print(f"Dados processados e preparados para o estado {estado}.")
        except Exception as e:
            print(f"Erro ao processar os dados para o estado {estado}: {e}")
    else:
        print(f"Falha ao baixar o arquivo para o estado {estado} após várias tentativas.")

# Verificar se há DataFrames antes de concatenar
if dfs:
    # Concatenar todos os DataFrames
    df_consolidado = pd.concat(dfs, ignore_index=True)

    # Inserir os dados na tabela final no PostgreSQL
    df_consolidado.to_sql(table_name, engine, if_exists='replace', index=False)

    print(f"Dados consolidados inseridos com sucesso na tabela '{table_name}'.")