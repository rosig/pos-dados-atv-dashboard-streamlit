# app.py
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

warnings.filterwarnings("ignore")


st.set_page_config(page_title="Habilidades e Satisfação", layout="wide")
sns.set_theme(style="whitegrid")

DATA_PATH = "./global_freelancers_raw.csv"


@st.cache_data(show_spinner=True)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    text_cols = ["gender", "gender_cat", "country", "language", "primary_skill"]
    for c in text_cols:
        if c in df.columns:
            df[c] = (
                df[c]
                .astype(str)
                .str.strip()
                .replace({"nan": np.nan})  # se entrou "nan" como string
            )

    df.rename(columns={"hourly_rate (USD)": "hourly_rate_usd"}, inplace=True)

    for c in [
        "age",
        "years_of_experience",
        "hourly_rate_usd",
        "rating",
        "client_satisfaction",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["gender"] = df["gender"].str.strip().str.lower()
    df["gender"] = df["gender"].apply(
        lambda x: (
            "Female"
            if str(x).upper().startswith("F")
            else ("Male" if str(x).upper().startswith("M") else x)
        )
    )

    return df


df = load_data(DATA_PATH)

required = {
    "gender",
    "country",
    "primary_skill",
    "hourly_rate_usd",
    "rating",
    "client_satisfaction",
    "years_of_experience",
}
missing = required - set(df.columns)
if missing:
    st.error(f"Seu CSV não tem as colunas esperadas: {', '.join(sorted(missing))}")
    st.stop()


# Sidebar — Filtros e opções
st.sidebar.header("Filtros")

# Filtros básicos
countries = sorted(df["country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "País(es)", countries, default=countries[:10]
)

languages = (
    sorted(df["language"].dropna().unique().tolist())
    if "language" in df.columns
    else []
)
selected_languages = st.sidebar.multiselect(
    "Idioma(s)", languages, default=languages[:10] if languages else []
)

genders = sorted(df["gender"].dropna().unique().tolist())
selected_genders = st.sidebar.multiselect("Gênero(s)", genders, default=genders)

# Aplicar filtros
df_filt = df.copy()
if selected_countries:
    df_filt = df_filt[df_filt["country"].isin(selected_countries)]
if selected_languages and "language" in df_filt.columns:
    df_filt = df_filt[df_filt["language"].isin(selected_languages)]
if selected_genders:
    df_filt = df_filt[df_filt["gender"].isin(selected_genders)]

# Controles para os gráficos
st.sidebar.header("Parâmetros dos gráficos")
top_n_countries = st.sidebar.slider("Top N países (para Heatmap)", 5, 30, 12)
top_n_skills = st.sidebar.slider("Top N skills (para Heatmap e gráficos)", 5, 30, 12)
min_obs_skill = st.sidebar.slider(
    "Mín. amostras por skill (satisfação média)", 5, 200, 20, step=5
)

normalize_gender = st.sidebar.radio(
    "Distribuição por gênero", ["Contagem absoluta", "Percentual por skill"], index=1
)

premium_rule = st.sidebar.selectbox(
    "Critério de 'Premium'",
    ["Top 25% por hourly_rate_usd", "Rating >= 4.8", "Top 25% por years_of_experience"],
    index=0,
)

top_n_premium_skills = st.sidebar.slider("Top N skills (Premium)", 5, 30, 10)


def top_by_total(df, key, n):
    """Retorna os N valores mais frequentes para uma coluna categórica."""
    return df[key].value_counts().head(n).index


def fig_ax():
    fig, ax = plt.subplots(figsize=(10, 6))
    return fig, ax


# Header principal
st.title("Habilidades e Satisfação")

# 1) Heatmap — frequência de habilidades por país
st.subheader("Heatmap: Frequência de Habilidades por País")

heatmap_data = pd.crosstab(df["primary_skill"], df["country"])

if heatmap_data.empty:
    st.warning("Sem dados disponíveis para o Heatmap.")
else:
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap="Blues", linewidths=0.5, ax=ax)
    ax.set_xlabel("País")
    ax.set_ylabel("Habilidade")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    st.pyplot(fig)

    with st.expander("Ver dados brutos (Heatmap)"):
        st.dataframe(heatmap_data)


# 2) Gráfico de barras — satisfação média por primary_skill
st.subheader("Satisfação média por habilidade (primary_skill)")

sat_df = df_filt.groupby("primary_skill", as_index=False).agg(
    media_satisfacao=("client_satisfaction", "mean"), n=("client_satisfaction", "count")
)

skill_satisfaction = (
    df.groupby("primary_skill")["client_satisfaction"]
    .mean()
    .sort_values(ascending=False)
)

if skill_satisfaction.empty:
    st.warning("Sem dados disponíveis para calcular a satisfação por habilidade.")
else:
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(
        x=skill_satisfaction.values,
        y=skill_satisfaction.index,
        palette="coolwarm",
        ax=ax,
    )
    ax.set_title("Média de satisfação do cliente por habilidade")
    ax.set_xlabel("Satisfação média")
    ax.set_ylabel("Habilidade")
    st.pyplot(fig)

    with st.expander("Ver dados brutos (Satisfação por habilidade)"):
        st.dataframe(skill_satisfaction.reset_index())

    with st.expander("Dados usados (download)"):
        st.dataframe(skill_satisfaction.reset_index())
        st.download_button(
            "Baixar CSV (satisfação por skill)",
            skill_satisfaction.reset_index().to_csv(index=False).encode("utf-8"),
            file_name="satisfacao_por_skill.csv",
            mime="text/csv",
        )


# 3) Distribuição das habilidades por gênero
st.subheader("Distribuição das habilidades por gênero")

dist_df = pd.crosstab(df_filt["primary_skill"], df_filt["gender"])
dist_df = dist_df.loc[
    dist_df.sum(axis=1).sort_values(ascending=False).head(top_n_skills).index
]

if normalize_gender == "Percentual por skill":
    dist_plot = dist_df.div(dist_df.sum(axis=1), axis=0) * 100
    ylabel = "Percentual (%)"
else:
    dist_plot = dist_df
    ylabel = "Contagem"

if dist_plot.empty:
    st.info("Sem dados suficientes para a distribuição por gênero.")
else:
    fig, ax = fig_ax()
    bottom = np.zeros(len(dist_plot))
    for col in dist_plot.columns:
        ax.barh(dist_plot.index, dist_plot[col], left=bottom, label=col)
        bottom += dist_plot[col].values
    ax.set_xlabel(ylabel)
    ax.set_ylabel("Habilidade")
    ax.set_title("Distribuição das habilidades por gênero")
    ax.legend(title="Gênero", bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)

    with st.expander("Dados usados (download)"):
        st.dataframe(dist_plot)
        st.download_button(
            "Baixar CSV (distribuição por gênero)",
            dist_plot.to_csv().encode("utf-8"),
            file_name="distribuicao_habilidade_genero.csv",
            mime="text/csv",
        )


# 4) Habilidades mais recorrentes entre freelancers “Premium”
st.subheader("Habilidades mais recorrentes entre freelancers “Premium”")

prem_mask = None
if premium_rule == "Top 25% por hourly_rate_usd":
    thr = df_filt["hourly_rate_usd"].quantile(0.75)
    prem_mask = df_filt["hourly_rate_usd"] >= thr
    criterio_txt = f"hourly_rate_usd ≥ P75 ({thr:.2f})"
elif premium_rule == "Rating >= 4.8":
    prem_mask = df_filt["rating"] >= 4.8
    criterio_txt = "rating ≥ 4.8"
else:  # Top 25% por years_of_experience
    thr = df_filt["years_of_experience"].quantile(0.75)
    prem_mask = df_filt["years_of_experience"] >= thr
    criterio_txt = f"years_of_experience ≥ P75 ({thr:.1f})"

df_premium = df_filt[prem_mask].copy()

if df_premium.empty:
    st.info("Nenhum freelancer atende ao critério 'Premium' com os filtros atuais.")
else:
    top_prem_skills = (
        df_premium["primary_skill"]
        .value_counts()
        .head(top_n_premium_skills)
        .sort_values(ascending=True)
    )

    fig, ax = fig_ax()
    ax.barh(top_prem_skills.index, top_prem_skills.values)
    ax.set_xlabel("Contagem (Premium)")
    ax.set_ylabel("Habilidade")
    ax.set_title(f"Habilidades mais recorrentes — Premium ({criterio_txt})")
    for i, v in enumerate(top_prem_skills.values):
        ax.text(v, i, str(v), va="center", ha="left", fontsize=9)
    st.pyplot(fig)

    with st.expander("Dados usados (download)"):
        st.dataframe(top_prem_skills.rename("count"))
        st.download_button(
            "Baixar CSV (skills premium)",
            top_prem_skills.to_csv(header=True).encode("utf-8"),
            file_name="skills_premium.csv",
            mime="text/csv",
        )
