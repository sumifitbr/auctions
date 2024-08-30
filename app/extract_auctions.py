import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import requests
import io

# Lista de estados
estados = ["AL", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]

# URL base fixa
url_base = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_"

# Configurações de conexão com o PostgreSQL
db_user = "seu_usuario"
db_password = "sua_senha"
db_host = "seu_host"
db_port = "5432"
db_name = "seu_banco"

# Criar a engine de conexão
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

for estado in estados:
    # Construir a URL completa para o estado
    url = f"{url_base}{estado}.csv"

    try:
        # Download do arquivo CSV
        response = requests.get(url)
        response.raise_for_status()  # Levanta uma exceção em caso de erro na requisição

        # Ler o CSV diretamente da resposta, pulando as duas primeiras linhas
        csv_data = io.StringIO(response.text)
        df = pd.read_csv(csv_data, sep=';', encoding='latin1', skiprows=2)

        # Listar as colunas do DataFrame
        print(f"Colunas no DataFrame para o estado {estado}:")
        print(df.columns)

        # Inserir a coluna etl_load_date
        df['etl_load_date'] = datetime.now()

        # Nome da tabela no PostgreSQL
        table_name = f"tabela_imoveis_{estado.lower()}"
        
        # Inserir os dados no PostgreSQL
        df.to_sql(table_name, engine, if_exists='replace', index=False)

        print(f"Dados inseridos com sucesso na tabela '{table_name}' para o estado {estado}.")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar ou processar os dados para o estado {estado}: {e}")
