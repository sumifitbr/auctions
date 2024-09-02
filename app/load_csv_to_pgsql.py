import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import os

# Diretório onde os arquivos CSV estão armazenados
files_dir = 'app/files'

# Configurações de conexão com o PostgreSQL
db_user = "postgres"
db_password = "Last$1981"
db_host = "94.130.107.131"
db_port = "5432"
db_name = "auctions_dev"

# Criar a engine de conexão
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

# Nome da tabela final
table_name = "tbl_imoveis"

# Nome do arquivo específico que você deseja processar (ou None para processar todos)
arquivo_especifico = None  # Defina aqui o nome do arquivo ou deixe como None para todos os arquivos
#estado = 'AC'
#arquivo_especifico = f'Lista_imoveis_{estado}.csv'  # Defina aqui o nome do arquivo ou deixe como None para todos os arquivos

# Lista para armazenar DataFrames temporários
dfs = []

# Listar todos os arquivos CSV no diretório ou apenas o arquivo específico
if arquivo_especifico:
    csv_files = [arquivo_especifico] if os.path.exists(os.path.join(files_dir, arquivo_especifico)) else []
else:
    csv_files = [f for f in os.listdir(files_dir) if f.endswith('.csv')]

# Processar os arquivos encontrados
for csv_file in csv_files:
    try:
        # Construir o caminho completo do arquivo
        file_path = os.path.join(files_dir, csv_file)

        # Extrair o estado do nome do arquivo
        estado = csv_file.split('_')[-1].replace('.csv', '')

        # Ler o CSV, pulando as duas primeiras linhas
        df = pd.read_csv(file_path, sep=';', encoding='latin1', skiprows=2)

        # Adicionar coluna com o estado
        df['estado'] = estado

        # Inserir a coluna etl_load_date
        df['etl_load_date'] = datetime.now()

        # Adicionar DataFrame à lista
        dfs.append(df)

        print(f"Dados processados e preparados para o arquivo {csv_file}.")
    except Exception as e:
        print(f"Erro ao processar o arquivo {csv_file}: {e}")

# Filtrar DataFrames que não estão vazios ou completamente preenchidos com NA
dfs = [df for df in dfs if not df.empty and not df.isna().all().all()]

# Verificar se há DataFrames antes de concatenar
if dfs:
    # Concatenar todos os DataFrames
    df_consolidado = pd.concat(dfs, ignore_index=True)

    # Inserir os dados na tabela final no PostgreSQL
    df_consolidado.to_sql(table_name, engine, if_exists='replace', index=False)

    print(f"Dados consolidados inseridos com sucesso na tabela '{table_name}'.")
else:
    print("Nenhum dado foi processado. Verifique os erros e tente novamente.")