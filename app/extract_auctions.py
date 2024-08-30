import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import requests
import io

# Download do arquivo CSV
url = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_geral.csv"
response = requests.get(url)
response.raise_for_status()  # Levanta uma exceção em caso de erro na requisição

# Ler o CSV diretamente da resposta
csv_data = io.StringIO(response.text)
df = pd.read_csv(csv_data, sep=';', encoding='latin1', skiprows=2)

# Listar as colunas do DataFrame
print("Colunas no DataFrame:")
print(df.columns)

# Lista de colunas
# header = 'N° do imóvel;UF;Cidade;Bairro;Endereço;Preço;Valor de avaliação;Desconto;Descrição;Modalidade de venda;Link de acesso'

# Inserir a coluna etl_load_date
df['etl_load_date'] = datetime.now().strftime('%Y-%M-%d %H:%M:%S')
print(df.head(1))

# Configurações de conexão com o PostgreSQL
db_user = "seu_usuario"
db_password = "sua_senha"
db_host = "seu_host"
db_port = "5432"
db_name = "seu_banco"

# Criar a engine de conexão
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Inserir os dados no PostgreSQL
table_name = "tabela_imoveis"
df.to_sql(table_name, engine, if_exists='replace', index=False)
print(f"Dados inseridos com sucesso na tabela '{table_name}'.")

