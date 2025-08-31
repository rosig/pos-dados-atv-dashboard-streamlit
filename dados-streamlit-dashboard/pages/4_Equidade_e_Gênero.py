#  ================================================== Importação das bibliotecas  ==================================================

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Equidade de Gênero",
    layout="wide",  # Opção que expande para largura total
    initial_sidebar_state="auto",
)


# 🔹 Função espaçadora fixa
def add_space():
    with st.container():
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)


# 1  ================================================== Título Página  ==================================================

st.markdown(
    """
    <h1 style='text-align: center;'>
        Equidade de Gênero - Freelancers de T.I. no Mundo 
    </h1>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 2, 1])  # proporção: esquerda - centro - direita
with col2:
    st.image("assets/twg_diversidade_ti_desktop1.png")


# 2  ================================================== Leitura Dataframe  ==================================================

df = pd.read_csv("global_freelancers_raw.csv")  # Leitura do Dataframe


# 3  ================================================== Organização e limpeza de dados  ==================================================

# Remoção de Variáveis
df.drop(
    ["freelancer_ID", "name", "language", "is_active", "client_satisfaction"],
    axis=1,
    inplace=True,
)

# Remoção de registros nulos
df.dropna(inplace=True)

# Convertendo os valores (stings) para minúsculo da variável "gênero"
df["gender"] = df["gender"].str.lower()

# Padronização dos valores de 'gender' ('m' por 'male' e 'f' por 'female')
df["gender"] = df["gender"].replace({"m": "male", "f": "female"})

# Conversão da variável 'gender' para o tipo category
df["gender"] = df["gender"].astype("category")

# Simplificação do nome da variável
df.rename(columns={"hourly_rate (USD)": "hourly_rate"}, inplace=True)

# Remoção dos caracteres "USD", " " e $
df["hourly_rate"] = df["hourly_rate"].str.replace(r"USD|\s|\$", "", regex=True)

# Conversão das variáveis "rating"; "age"; "years_of_experience"; "hourly_rate".
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["age"] = pd.to_numeric(df["age"], errors="coerce")
df["years_of_experience"] = pd.to_numeric(df["years_of_experience"], errors="coerce")
df["hourly_rate"] = pd.to_numeric(df["hourly_rate"], errors="coerce")

# Remoção de linhas com valores nulos após conversão
df.dropna(inplace=True)

st.markdown(
    "<h3 style='text-align: center; color: black;'> 🌎Distribuição de freelancers (Países vs Gênero)</h3>",
    unsafe_allow_html=True,
)

# --- Garantir que df tem as colunas certas ---
if "country" not in df.columns or "gender" not in df.columns:
    st.error("❌ O DataFrame precisa ter as colunas 'country' e 'gender'.")
    st.stop()

# --- Criar tabela agregada ---
country_gender = df.groupby(["country", "gender"]).size().unstack(fill_value=0)

# 4  ================================================== Segmentador Continente > País e Gráfico  ==================================================
import unicodedata

# checagens iniciais
if "df" not in globals() and "df" not in locals():
    st.error("❌ DataFrame `df` não encontrado.")
    st.stop()

if "country" not in df.columns or "gender" not in df.columns:
    st.error("❌ O DataFrame precisa ter as colunas 'country' e 'gender'.")
    st.stop()

# agregação de dados com groupby
country_gender = df.groupby(["country", "gender"]).size().unstack(fill_value=0)

if country_gender.empty:
    st.warning("⚠️ country_gender ficou vazio após o groupby.")
    st.stop()

# --------------------------- mapeamento país -> continente (raw) ---------------------------
country_continent_raw = {
    "Canada": "América do Norte",
    "South Korea": "Ásia",
    "Germany": "Europa",
    "Australia": "Oceania",
    "China": "Ásia",
    "United States": "América do Norte",
    "Netherlands": "Europa",
    "Mexico": "América do Norte",
    "Russia": "Europa",
    "France": "Europa",
    "Indonesia": "Ásia",
    "Egypt": "África",
    "Turkey": "Ásia",
    "Argentina": "América do Sul",
    "Spain": "Europa",
    "United Kingdom": "Europa",
    "South Africa": "África",
    "India": "Ásia",
    "Italy": "Europa",
    "Japan": "Ásia",
    "Brazil": "América do Sul",
}

# --------------------------- inserção das bandeiras ---------------------------
flags = {
    "Canada": "https://flagcdn.com/w40/ca.png",
    "South Korea": "https://flagcdn.com/w40/kr.png",
    "Germany": "https://flagcdn.com/w40/de.png",
    "Australia": "https://flagcdn.com/w40/au.png",
    "China": "https://flagcdn.com/w40/cn.png",
    "United States": "https://flagcdn.com/w40/us.png",
    "Netherlands": "https://flagcdn.com/w40/nl.png",
    "Mexico": "https://flagcdn.com/w40/mx.png",
    "Russia": "https://flagcdn.com/w40/ru.png",
    "France": "https://flagcdn.com/w40/fr.png",
    "Indonesia": "https://flagcdn.com/w40/id.png",
    "Egypt": "https://flagcdn.com/w40/eg.png",
    "Turkey": "https://flagcdn.com/w40/tr.png",
    "Argentina": "https://flagcdn.com/w40/ar.png",
    "Spain": "https://flagcdn.com/w40/es.png",
    "United Kingdom": "https://flagcdn.com/w40/gb.png",
    "South Africa": "https://flagcdn.com/w40/za.png",
    "India": "https://flagcdn.com/w40/in.png",
    "Italy": "https://flagcdn.com/w40/it.png",
    "Japan": "https://flagcdn.com/w40/jp.png",
    "Brazil": "https://flagcdn.com/w40/br.png",
}


# --------------------------- função de normalização de limpeza das strings ---------------------------
def normalize(name: str) -> str:
    if not isinstance(name, str):
        return ""
    s = name.strip().lower()
    # remove acentos
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # remove pontuação que possa atrapalhar
    for ch in [".", ",", "'", '"', "(", ")", "-"]:
        s = s.replace(ch, "")
    s = s.replace("  ", " ")
    return s


# --------------------------- criar mapa normalizado a partir do raw ---------------------------
norm_continent_map = {normalize(k): v for k, v in country_continent_raw.items()}
norm_flags_map = {normalize(k): url for k, url in flags.items()}

# --------------------------- mapear os países existentes no country_gender para continentes ---------------------------
country_to_continent = {}
unmapped = []
for pais in country_gender.index:
    cont = norm_continent_map.get(normalize(pais))
    if cont is None:
        unmapped.append(pais)
    country_to_continent[pais] = cont  # pode ser None

# --------------------------- opções de continentes (apenas os presentes nos dados) ---------------------------
present_continents = sorted({c for c in country_to_continent.values() if c})
continentes_options = ["Todos"] + present_continents

# selectbox (começa em "Todos" - que mostra tudo)
continente_selecionado = st.selectbox(
    "Selecione um continente específico (ou mantem a seleção em Todos) para visualizar a informação desejada:",
    options=continentes_options,
    index=0,
)

# --------------------------- filtrar por continente selecionado (usa os países reais do index) ---------------------------
if continente_selecionado == "Todos":
    country_gender_filtered = country_gender.copy()
else:
    paises_filtrados = [
        p for p, c in country_to_continent.items() if c == continente_selecionado
    ]
    if not paises_filtrados:
        st.warning(f"⚠️ Nenhum país mapeado para '{continente_selecionado}'.")
        country_gender_filtered = country_gender.iloc[0:0]  # vazia
    else:
        country_gender_filtered = country_gender.loc[
            country_gender.index.isin(paises_filtrados)
        ]

if country_gender_filtered.empty:
    st.warning("⚠️ Não há dados para o filtro aplicado.")
    # ainda assim mostramos tabela vazia e paramos o plot
    st.dataframe(country_gender_filtered)
    st.stop()

# --------------------------- lista final de países ---------------------------
paises = country_gender_filtered.index.tolist()

#  montar gráfico
fig = go.Figure()
for genero, cor in zip(["male", "female"], ["#1f77b4", "#ff7f0e"]):
    if genero in country_gender_filtered.columns:
        fig.add_trace(
            go.Bar(
                y=paises,
                x=country_gender_filtered[genero],
                name="Homem" if genero == "male" else "Mulher",
                orientation="h",
                marker_color=cor,
            )
        )

# --------------------------- adicionar bandeiras (busca com normalização para evitar mismatch) ---------------------------
for pais in paises:
    img_src = norm_flags_map.get(normalize(pais))
    if img_src:
        fig.add_layout_image(
            dict(
                source=img_src,
                xref="paper",
                yref="y",
                x=-0.05,
                y=pais,
                sizex=0.4,
                sizey=0.6,
                xanchor="right",
                yanchor="middle",
                layer="above",
            )
        )

fig.update_layout(
    title="Distribuição de freelancers (Países vs Gênero)",
    barmode="stack",
    xaxis_title="Quantidade de freelancers",
    yaxis=dict(autorange="reversed", tickfont=dict(color="white")),
    height=500 + len(paises) * 20,
)

# --------------------------- layout em colunas ---------------------------
col1, col2 = st.columns([2, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    total = int(country_gender_filtered.sum().sum())
    hom = (
        int(country_gender_filtered["male"].sum())
        if "male" in country_gender_filtered.columns
        else 0
    )
    mul = (
        int(country_gender_filtered["female"].sum())
        if "female" in country_gender_filtered.columns
        else 0
    )
    st.metric("Total de freelancers", total)
    st.metric("Homens", hom)
    st.metric("Mulheres", mul)

    st.write("**Tabela geral de freelancers por país**")
    st.dataframe(
        country_gender_filtered.sum(axis=1)
        .sort_values(ascending=False)
        .to_frame(name="Quantidade")
    )

# --------------------------- informar países não mapeados (útil para ajustar o dicionário) ---------------------------
if unmapped:
    st.info(
        "⚠️ Alguns países não estão no mapeamento país→continente (adicione-os ao dicionário se quiser filtrar por eles):"
    )
    st.write(unmapped)

st.markdown(
    "<p style='font-size:12px;'><b>Fonte:</b> https://www.kaggle.com/datasets/urvishahir/global-freelancers-raw-dataset </p>",
    unsafe_allow_html=True,
)

# 🔹 Espaço entre gráficos
add_space()

# 5 ================================================== Gráfico de Média de Rating por Gênero e País  ==================================================

with st.container():
    st.markdown(
        "<h3 style='text-align: center; color: black;'></h3>", unsafe_allow_html=True
    )

st.markdown(
    "<h3 style='text-align: center; color: black;'> ⭐ Dados comparativos de Rating x Gênero x País</h3>",
    unsafe_allow_html=True,
)

# --------------------------- Traduzindo os gêneros ---------------------------
df["gender"] = df["gender"].replace({"female": "Mulher", "male": "Homem"})

# --------------------------- Criando seleção com radio ---------------------------
opcao = st.radio("Selecione o gênero:", ("Todos", "Homem", "Mulher"), horizontal=True)

# --------------------------- Filtrando o dataframe de acordo com a escolha ---------------------------
if opcao != "Todos":
    df_filtrado = df[df["gender"] == opcao]
else:
    df_filtrado = df

#  --------------------------- Agrupando por país e gênero e calculando a média do rating ---------------------------
rating_por_pais_genero = (
    df_filtrado.groupby(["country", "gender"])["rating"].mean().reset_index()
)

# Criando gráfico de barras agrupadas
fig = px.bar(
    rating_por_pais_genero,
    x="country",
    y="rating",
    color="gender",
    barmode="group",  # barras lado a lado
    text="rating",
    labels={"country": "País", "rating": "Rating Médio", "gender": "Gênero"},
    title="Média de Rating por Gênero e País",
)

fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig.update_layout(yaxis=dict(range=[0, df["rating"].max() + 1]), xaxis_tickangle=-45)

# --------------------------- Exibindo no Streamlit ---------------------------
st.plotly_chart(fig, use_container_width=True)


# --------------------------- Espaço entre gráficos ---------------------------
add_space()

# 6  ================================================== Gráfico do Valor da Hora x Gênero x Anos de Experiência  ==================================================


with st.container():
    st.markdown(
        "<h3 style='text-align: center; color: black;'></h3>", unsafe_allow_html=True
    )

# --------------------------- Verifica se a coluna hourly_rate está como string ---------------------------
df["hourly_rate"] = df["hourly_rate"].astype(str)

#  --------------------------- Limpeza dos valores ---------------------------
df["hourly_rate"] = (
    df["hourly_rate"]
    .str.replace(
        r"[^\d,\.]", "", regex=True
    )  # remove tudo que não é número, ponto ou vírgula
    .str.replace(".", "", regex=False)  # remove pontos de milhar
    .str.replace(",", ".", regex=False)  # troca vírgula por ponto decimal
)

# --------------------------- Converte para valores numéricos ---------------------------
df["hourly_rate"] = pd.to_numeric(df["hourly_rate"], errors="coerce")


st.markdown(
    "<h3 style='text-align: center; color: black;'> 🖥️ Valor da Hora x Gênero x Anos de Experiência</h3>",
    unsafe_allow_html=True,
)

# --------------------------- Slider para filtrar intervalo de anos de experiência ---------------------------
min_exp = int(df["years_of_experience"].min())
max_exp = int(df["years_of_experience"].max())

anos_exp = st.slider(
    "Arraste os extremos do intervalo de anos de experiência, para saber a média do valor da hora x anos \
        considerando as seguintes categorias: Junior (<=2 anos), Pleno (>2 anos e <5 anos), Senior (>=5 anos e <10 anos) e Master (>=10 anos)",
    min_value=min_exp,
    max_value=max_exp,
    value=(min_exp, max_exp),
)

# --------------------------- Aplica o filtro ---------------------------
df_filtrado = df[
    (df["years_of_experience"] >= anos_exp[0])
    & (df["years_of_experience"] <= anos_exp[1])
]


# --------------------------- Visualização ---------------------------

# Agrupa por anos de experiência e gênero
media_por_genero = (
    df_filtrado.groupby(["years_of_experience", "gender"])["hourly_rate"]
    .mean()
    .round(2)
    .reset_index()
    .rename(
        columns={
            "hourly_rate": "Valor da Hora (R$)",
            "gender": "Gênero",
            "years_of_experience": "Anos de Experiência",
        }
    )
)

# --------------------------- Gráfico usando anos exatos no eixo X ---------------------------
fig = px.bar(
    media_por_genero,
    x="Anos de Experiência",
    y="Valor da Hora (R$)",
    color="Gênero",
    barmode="group",
    text="Valor da Hora (R$)",
    labels={
        "Anos de Experiência": "Anos de Experiência",
        "Valor da Hora (R$)": "Valor da Hora (R$)",
    },
    title="Valor da Hora por Ano de Experiência e Gênero",
)

fig.update_traces(texttemplate="R$ %{y:.2f}", textposition="outside")
fig.update_layout(xaxis_title="Anos de Experiência", yaxis_title="Valor da Hora (R$)")

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    "<p style='font-size:12px;'><b>Fonte:</b> https://www.kaggle.com/datasets/urvishahir/global-freelancers-raw-dataset </p>",
    unsafe_allow_html=True,
)
st.write("")  # linha em branco → cria espaçamento

#  --------------------------- Espaço entre gráficos ---------------------------
add_space()

# 7 ================================================== Visualização da Tabela com dados gerais e filtros  ==================================================

with st.container():
    st.markdown(
        "<h3 style='text-align: center; color: black;'></h3>", unsafe_allow_html=True
    )

# --------------------------- Tradução das colunas ---------------------------
df = df.rename(
    columns={
        "gender": "Gênero",
        "age": "Idade",
        "country": "País",
        "primary_skill": "Habilidade Principal",
        "years_of_experience": "Anos de Experiência",
        "hourly_rate": "Valor Hora (R$)",
        "rating": "Avaliação",
    }
)

# --------------------------- Tradução dos valores de gênero ---------------------------
df["Gênero"] = df["Gênero"].replace({"female": "Mulher", "male": "Homem"})

# --------------------------- Filtros ---------------------------
st.sidebar.header("🔎 Filtros - Tabela Geral")

# --------------------------- Selectbox de gênero ---------------------------
genero = st.sidebar.selectbox(
    "Selecione o gênero:", options=["Todos"] + list(df["Gênero"].unique())
)

# --------------------------- Selectbox de país ---------------------------
pais = st.sidebar.selectbox(
    "Selecione o país:", options=["Todos"] + list(df["País"].unique())
)

# --------------------------- Selectbox de habilidade principal ---------------------------
skill = st.sidebar.selectbox(
    "Selecione a habilidade principal:",
    options=["Todos"] + list(df["Habilidade Principal"].unique()),
)

# ---------------------------- Aplicação dos filtros ---------------------------
df_filtrado = df.copy()

if genero != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Gênero"] == genero]

if pais != "Todos":
    df_filtrado = df_filtrado[df_filtrado["País"] == pais]

if skill != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Habilidade Principal"] == skill]

# --------------------------- Exibição ---------------------------
st.subheader("📋 Tabela Geral de Dados")
st.write(df_filtrado)

st.markdown(
    "<p style='font-size:12px;'><b>Nota:</b> Os dados apresentados são sintéticos e foram construídos com o objetivo de favorecer a aprendizagem na área de Ciência de Dados.</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='font-size:12px;'><b>Fonte:</b> https://www.kaggle.com/datasets/urvishahir/global-freelancers-raw-dataset </p>",
    unsafe_allow_html=True,
)
