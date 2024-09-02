import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Configurações de conexão com o banco de dados
db_user = "postgres"
db_password = "Last$1981"
db_host = "94.130.107.131"
db_port = "5432"
db_name = "auctions_dev"

# Conexão com o banco de dados
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

# Título da aplicação
st.title("Auctions Online")

# Sidebar com filtros
st.sidebar.header("Filtros")

# Carregar os dados do banco de dados
@st.cache_data
def load_data():
    query = """
    SELECT estado, cidade, bairro, modalidade_venda, valor_imovel, regiao
    FROM tbl_imoveis
    """
    return pd.read_sql(query, engine)

df = load_data()

# Filtros dependentes
estado_selecionado = st.sidebar.selectbox("Selecione o estado", df["estado"].unique())
cidades_filtradas = df[df["estado"] == estado_selecionado]["cidade"].unique()
cidade_selecionada = st.sidebar.selectbox("Selecione a cidade", cidades_filtradas)
bairros_filtrados = df[(df["estado"] == estado_selecionado) & (df["cidade"] == cidade_selecionada)]["bairro"].unique()
bairro_selecionado = st.sidebar.selectbox("Selecione o bairro", bairros_filtrados)

# Filtro de slider para valor do imóvel
valor_minimo, valor_maximo = st.sidebar.slider("Valor do Imóvel", 0, 1000000, (0, 1000000))

# Filtro por modalidade de venda
modalidade_selecionada = st.sidebar.selectbox("Modalidade de Venda", df["modalidade_venda"].unique())

# Filtrar o DataFrame com base nos filtros selecionados
df_filtrado = df[
    (df["estado"] == estado_selecionado) &
    (df["cidade"] == cidade_selecionada) &
    (df["bairro"] == bairro_selecionado) &
    (df["valor_imovel"] >= valor_minimo) &
    (df["valor_imovel"] <= valor_maximo) &
    (df["modalidade_venda"] == modalidade_selecionada)
]

# Gráfico de barra pela coluna estado
st.subheader("Distribuição de Imóveis por Estado")
grafico_estado = df_filtrado["estado"].value_counts().plot(kind='bar')
st.pyplot(grafico_estado.figure)

# BIG NUMBER com total de imóveis por região
st.subheader("Total de Imóveis por Região")
total_regiao = df_filtrado.groupby("regiao")["regiao"].count()
st.write(total_regiao)

# Exibir o DataFrame filtrado (opcional)
st.subheader("Imóveis Filtrados")
st.dataframe(df_filtrado)

# Fechar a conexão com o banco de dados
engine.dispose()