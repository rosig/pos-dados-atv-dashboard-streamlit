import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sequential

#########################
# GRÁFICO 1
#########################

st.set_page_config(
    page_title="Preço vs Avaliação — Países", page_icon="📊", layout="wide"
)

st.title("Análise de Mercado de Freelancers: Satisfação e Preço")
st.subheader("📊 Top N países — Média do indície de satisfação dos clientes")

DEFAULT_PATH = "global_freelancers_raw.csv"

try:
    df = pd.read_csv(DEFAULT_PATH)
except Exception as e:
    st.error(f"Não foi possível carregar o dataset: {e}")
    st.stop()

df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["country"] = df["country"].astype("string")
df_valid = df.dropna(subset=["rating"]).copy()


ranking = (
    df_valid.groupby("country", dropna=False)
    .agg(
        avg_rating=("rating", "mean"),
        median_rating=("rating", "median"),
        n_freelancers=("rating", "count"),
    )
    .sort_values(["avg_rating", "n_freelancers"], ascending=[False, False])
    .reset_index()
)


max_countries = int(ranking["country"].nunique())
default_top = min(10, max_countries)

chart_ph1 = st.container()

# Slider de filtro
st.caption("Filtros")
top_n = st.slider(
    "Nº de países",
    min_value=1,
    max_value=max_countries,
    value=default_top,
    step=1,
    key="slider_1",
)

top = ranking.head(top_n).copy()
vals = pd.to_numeric(top["avg_rating"], errors="coerce")
countries = top["country"]

cmin = float(vals.min() * 0.90)
cmax = float(vals.max())

fig = go.Figure(
    go.Bar(
        x=vals,
        y=countries,
        orientation="h",
        marker=dict(color=vals, coloraxis="coloraxis"),
        text=[f"{v:.2f}" for v in vals],
        textposition="outside",
    )
)

fig.update_layout(
    # title="Top N países — Média do indície de satisfação dos clientes",
    yaxis=dict(autorange="reversed"),
    coloraxis=dict(
        colorscale=sequential.Sunset,
        cmin=cmin,
        cmax=cmax,
        colorbar=dict(title="Rating"),
    ),
    template="plotly_white",
    margin=dict(l=10, r=10, t=60, b=10),
    height=520,
)

with chart_ph1:
    st.plotly_chart(fig, use_container_width=True)

# with st.expander("📋 Tabela de resultados:"):
#     st.dataframe(top.assign(
#         avg_rating=top["avg_rating"].round(2),
#         median_rating=top["median_rating"].round(2)
#     ))


#########################
# GRÁFICO 2
#########################

st.subheader("💵 Média de preço/hora por país")

df.rename(columns={"hourly_rate (USD)": "hourly_rate"}, inplace=True)  # new

needed_cols = {"country", "hourly_rate", "years_of_experience"}
missing = needed_cols - set(df.columns)
if missing:
    st.error(f"Colunas ausentes no dataset para esta análise: {', '.join(missing)}")
    st.stop()

df_prices = df.copy()
df_prices["hourly_rate"] = pd.to_numeric(df_prices["hourly_rate"], errors="coerce")
df_prices["years_of_experience"] = pd.to_numeric(
    df_prices["years_of_experience"], errors="coerce"
)
df_prices["country"] = df_prices["country"].astype("string")


# Categorização do tempo de experiência
def exp_category(years: float) -> str:
    if years <= 3:
        return "Júnior"
    elif years <= 7:
        return "Pleno"
    else:
        return "Sênior"


df_prices["exp_category"] = df_prices["years_of_experience"].apply(exp_category)

CATEGORIES = ["Todos", "Júnior", "Pleno", "Sênior"]
try:
    selected_cat = st.segmented_control(
        "Categoria de experiência", CATEGORIES, default="Todos"
    )
except Exception:
    selected_cat = st.radio(
        "Categoria de experiência", CATEGORIES, index=0, horizontal=True
    )

if selected_cat != "Todos":
    df_filtered = df_prices[df_prices["exp_category"] == selected_cat]
else:
    df_filtered = df_prices

df_filtered = df_filtered.dropna(subset=["hourly_rate", "country"])

price_by_country = (
    df_filtered.groupby("country", dropna=False)
    .agg(
        avg_hourly_rate=("hourly_rate", "mean"), n_freelancers=("hourly_rate", "count")
    )
    .sort_values(["avg_hourly_rate", "n_freelancers"], ascending=[False, False])
    .reset_index()
)

if price_by_country.empty:
    st.warning("Nenhum dado após aplicar este filtro.")
    st.stop()

chart_ph2 = st.container()

st.caption("Filtros")
max_countries = int(price_by_country["country"].nunique())
default_top = min(10, max_countries)
top_n = st.slider(
    "Nº de países",
    min_value=1,
    max_value=max_countries,
    value=default_top,
    step=1,
    key="slider_2",
)

top_df = price_by_country.head(top_n).copy()

vals = pd.to_numeric(top_df["avg_hourly_rate"], errors="coerce")
countries = top_df["country"]

cmin = float(vals.min() * 0.90) if len(vals) else 0.0
cmax = float(vals.max()) if len(vals) else 1.0

title_suffix = f" — {selected_cat}" if selected_cat != "Todos" else ""
fig_2 = go.Figure(
    go.Bar(
        x=vals,
        y=countries,
        orientation="h",
        marker=dict(color=vals, coloraxis="coloraxis"),
        text=[f"{v:.2f}" for v in vals],
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Média preço/hora: %{x:.2f}<br>Qtd freelancers: %{customdata}<extra></extra>",
        customdata=top_df["n_freelancers"],
    )
)
fig_2.update_layout(
    # title=f"Média de preço/hora por país{title_suffix}",
    yaxis=dict(autorange="reversed"),
    coloraxis=dict(
        colorscale=sequential.Cividis,
        cmin=cmin,
        cmax=cmax,
        colorbar=dict(title="Preço/hora (média)"),
    ),
    template="plotly_white",
    margin=dict(l=10, r=10, t=60, b=10),
    height=560,
)

with chart_ph2:
    st.plotly_chart(fig_2, use_container_width=True)
