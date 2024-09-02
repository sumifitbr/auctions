import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Auctions Online",
    page_icon=":house:",  # Alternativamente, você pode usar um caminho para um favicon, por exemplo: "assets/favicon.ico"
)

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
    return username == "admin" and password == "password123"

# Tela de login
def login():
    st.title("Login")

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
    st.title("Auctions Online")

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
              WHEN i.estado IN ('MT','MS','GO','DF') THEN 'Centro-oeste'
              WHEN i.estado IN ('SP','RJ','MG','ES') THEN 'Sudeste'
              WHEN i.estado IN ('PR','SC','RS') THEN 'Sul'
              ELSE 'Favor Classificar' 
            END AS regiao,
            i."Link de acesso" AS link_acesso,
            i.etl_load_date as etl_load_date
          FROM tbl_imoveis i
        )
        SELECT 
          estado,
          cidade,
          bairro,
          modalidade_venda,
          valor_imovel,
          regiao,
          link_acesso,
          max(etl_load_date) as etl_load_date
        FROM leiloes
        group by
            estado,
            cidade,
            bairro,
            modalidade_venda,
            valor_imovel,
            regiao,
            link_acesso
            order by estado
        """
        return pd.read_sql(query, engine)

    df = load_data()

    # Garantir que o DataFrame não esteja vazio antes de definir os filtros
    if df.empty:
        st.write("Nenhum dado disponível.")
    else:
        # Filtros dependentes com dados disponíveis
        estados_disponiveis = sorted(df["estado"].unique())
        estado_selecionado = st.sidebar.selectbox("Selecione o estado", estados_disponiveis)
        cidades_filtradas = sorted(df[df["estado"] == estado_selecionado]["cidade"].unique())
        cidade_selecionada = st.sidebar.selectbox("Selecione a cidade", cidades_filtradas)
        bairros_filtrados = sorted(df[(df["estado"] == estado_selecionado) & (df["cidade"] == cidade_selecionada)]["bairro"].unique())
        bairro_selecionado = st.sidebar.selectbox("Selecione o bairro", bairros_filtrados)

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

        # Se nenhum dado for encontrado após filtragem, mostrar mensagem
        if df_filtrado.empty:
            st.write("Nenhum imóvel encontrado para os critérios selecionados.")
        else:
            # Layout de colunas para exibir a tabela e o gráfico lado a lado
            col1, col2 = st.columns([2, 3])

            with col1:
                st.subheader("Total de Imóveis por Região")
                total_regiao = df.groupby("regiao")["regiao"].count().reset_index(name="Total de Imóveis")
                st.dataframe(total_regiao)

            with col2:
                st.subheader("Distribuição de Imóveis por Estado")
                fig, ax = plt.subplots(figsize=(10, 6))  # Ajusta o tamanho do gráfico
                df.groupby("estado")["estado"].count().plot(kind='bar', ax=ax)
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

            # Drop coluna de etl_load do df_filtrado
            df_filtrado = df_filtrado.drop['etl_load_date']

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
        
        # Exibe data de atualização
        update_date = df['etl_load_date']
        st.sidebar.title(str(update_date).strftime('%Y-%M-%D %H:%M:%S'))

    # Fechar a conexão com o banco de dados
    engine.dispose()