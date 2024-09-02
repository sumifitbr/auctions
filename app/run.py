import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt

# Configurações de conexão com o banco de dados
db_user = "postgres"
db_password = "Last$1981"
db_host = "94.130.107.131"
db_port = "5432"
db_name = "auctions_dev"

# Conexão com o banco de dados
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(connection_string)

# Função de autenticação
def authenticate(username, password):
    if username == "admin" and password == "password123":
        return True
    return False

# Tela de login
def login():
    st.title("Auctions - Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.query_params = {"authenticated": "true"}
        else:
            st.error("Usuário ou senha incorretos.")

# Verificar se o usuário está autenticado
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if st.session_state.authenticated or st.query_params.get("authenticated") == ["true"]:
    st.session_state.authenticated = True

if not st.session_state.authenticated:
    login()
else:
    # Título da aplicação
    st.sidebar.title("Auctions Online")

    # Sidebar com filtros
    st.sidebar.header("Filtros")

    # Carregar os dados do banco de dados
    @st.cache_data
    def load_data():
        query = """
        WITH leiloes AS (
          SELECT 
            i.estado AS estado,
            i."Cidade" AS cidade,
            i."Bairro" AS bairro,
            i."Modalidade de venda" AS modalidade_venda,
            REPLACE(REPLACE(i."Valor de avaliação", '.', ''), ',', '.')::FLOAT AS valor_imovel,
            CASE 
              WHEN i.estado IN ('AM','RR','AP','PA','TO','RO','AC') THEN 'Norte'
              WHEN i.estado IN ('MA','PI','CE','RN','PE','PB','SE','AL','BA') THEN 'Nordeste'
              WHEN i.estado IN ('MT','MS','GO') THEN 'Centro-oeste'
              WHEN i.estado IN ('SP','RJ','MG','ES') THEN 'Sudeste'
              WHEN i.estado IN ('PR','SC','RS') THEN 'Sul'
              ELSE 'Favor Classificar' 
            END AS regiao,
            i."Link de acesso" AS link_acesso
          FROM tbl_imoveis i
        )
        SELECT 
          estado,
          cidade,
          bairro,
          modalidade_venda,
          valor_imovel,
          regiao,
          link_acesso
        FROM leiloes
        """
        return pd.read_sql(query, engine)

    df = load_data()

    # Filtros dependentes
    estado_selecionado = st.sidebar.selectbox("Selecione o estado", sorted(df["estado"].unique()))
    cidades_filtradas = df[df["estado"] == estado_selecionado]["cidade"].unique()
    cidade_selecionada = st.sidebar.selectbox("Selecione a cidade", sorted(cidades_filtradas))
    bairros_filtrados = df[(df["estado"] == estado_selecionado) & (df["cidade"] == cidade_selecionada)]["bairro"].unique()
    bairro_selecionado = st.sidebar.selectbox("Selecione o bairro", sorted(bairros_filtrados))

    # Filtro de slider para valor do imóvel
    valor_minimo, valor_maximo = st.sidebar.slider("Valor do Imóvel", 0, 1000000, (0, 1000000))

    # Filtro por modalidade de venda
    modalidade_selecionada = st.sidebar.selectbox("Modalidade de Venda", sorted(df["modalidade_venda"].unique()))

    # Filtrar o DataFrame com base nos filtros selecionados
    df_filtrado = df[
        (df["estado"] == estado_selecionado) &
        (df["cidade"] == cidade_selecionada) &
        (df["bairro"] == bairro_selecionado) &
        (df["valor_imovel"] >= valor_minimo) &
        (df["valor_imovel"] <= valor_maximo) &
        (df["modalidade_venda"] == modalidade_selecionada)
    ]

    # Verificar se o DataFrame filtrado está vazio
    if df_filtrado.empty:
        st.write("Nenhum imóvel encontrado para os critérios selecionados.")
    else:
        # Layout de colunas para exibir a tabela e o gráfico lado a lado
        col1, col2 = st.columns([2, 3])

        with col1:
            st.subheader("Total de Imóveis por Região")
            total_regiao = df_filtrado.groupby("regiao")["regiao"].count().reset_index(name="Total de Imóveis")
            st.dataframe(total_regiao)

        with col2:
            st.subheader("Distribuição de Imóveis por Estado")
            fig, ax = plt.subplots(figsize=(10, 6))  # Ajusta o tamanho do gráfico
            df_filtrado.groupby("estado")["estado"].count().plot(kind='bar', ax=ax)
            ax.set_ylabel("Número de Imóveis")
            ax.set_xlabel("Estado")
            st.pyplot(fig)

        # Ajustar rótulos e formatação
        df_filtrado = df_filtrado.rename(columns={
            "estado": "Estado",
            "cidade": "Cidade",
            "bairro": "Bairro",
            "modalidade_venda": "Modalidade de Venda",
            "valor_imovel": "Valor Imóvel",
            "regiao": "Região",
            "link_acesso": "Link"
        })

        # Formatação do valor do imóvel para BRL
        df_filtrado["Valor Imóvel"] = df_filtrado["Valor Imóvel"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Tornar os links clicáveis com label "SAIBA MAIS"
        df_filtrado["Link"] = df_filtrado["Link"].apply(lambda x: f'<a href="{x}" target="_blank">SAIBA MAIS</a>')

        # Exibir a tabela de imóveis filtrados com ajustes de largura
        st.subheader("Imóveis Filtrados")
        st.markdown(
            df_filtrado.to_html(escape=False, index=False), 
            unsafe_allow_html=True
        )

    # Botão para logout
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.query_params = {"authenticated": "false"}

    # Fechar a conexão com o banco de dados
    engine.dispose()
