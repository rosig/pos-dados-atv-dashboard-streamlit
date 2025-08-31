import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px

# =====================
# Configuração inicial
# =====================
st.set_page_config(page_title="Panorama Global de Freelancers", layout="wide")


# Carregar dataset
@st.cache_data
def load_data():
    df = pd.read_csv("global_freelancers_raw.csv")

    # Normalizar coluna de gênero
    df["gender"] = (
        df["gender"]
        .astype(str)  # garantir string
        .str.strip()  # remover espaços extras
        .str.upper()  # padronizar para maiúsculas
        .str[0]  # pegar apenas a primeira letra
        .map({"F": "Female", "M": "Male"})  # mapear
    )

    return df


df = load_data()

# =====================
# ABA 1 - Visão Geral
# =====================
st.title("🌍 Panorama Global de Freelancers")
st.markdown("### Visão Geral dos Freelancers")
st.markdown("---")

# KPIs principais
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total de Freelancers", f"{df.shape[0]:,}")

with col2:
    st.metric("Países Representados", df["country"].nunique())

with col3:
    st.metric("Habilidades Únicas", df["primary_skill"].nunique())

st.markdown("---")

# =====================
# Distribuição por país
# =====================
st.subheader("Distribuição de Freelancers por País")
country_counts = df["country"].value_counts().reset_index()
country_counts.columns = ["country", "count"]

fig_country = px.bar(
    country_counts.head(15),
    x="country",
    y="count",
    text="count",
    title="Top 15 Países com Mais Freelancers",
    color="count",
    color_continuous_scale="Blues",
)
fig_country.update_traces(textposition="outside")
st.plotly_chart(fig_country, use_container_width=True)

# =====================
# Distribuição por gênero
# =====================
st.subheader("Distribuição de Freelancers por Gênero")
fig_gender = px.pie(
    df,
    names="gender",
    title="Distribuição por Gênero",
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.RdBu,
)
st.plotly_chart(fig_gender, use_container_width=True)

# =====================
# Wordcloud de habilidades
# =====================
st.subheader("Principais Habilidades")
skills = df["primary_skill"].dropna().astype(str).values
text = " ".join(skills)

wordcloud = WordCloud(
    width=800, height=400, background_color="white", colormap="viridis"
).generate(text)

fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# =====================
# Boxplot da experiência
# =====================
st.subheader("Experiência (anos) por Gênero")
fig_exp = px.box(
    df,
    x="gender",
    y="years_of_experience",
    color="gender",
    points="all",
    title="Distribuição de Experiência por Gênero",
    color_discrete_sequence=px.colors.sequential.Teal,
)
st.plotly_chart(fig_exp, use_container_width=True)
