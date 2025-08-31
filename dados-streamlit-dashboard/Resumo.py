import streamlit as st

# =====================
# Configuração inicial
# =====================
st.set_page_config(page_title="Panorama Global de Freelancers", layout="wide")

# =====================
# Título principal
# =====================
st.title("📊 Panorama Global de Freelancers")
st.markdown("---")

st.title("Equipe 1")
st.markdown(
    """

  - Guilherme
  - Rodolfo
  - Rosinaldo
  - Wolney

  """
)

# =====================
# Introdução ao dashboard
# =====================
st.header("Bem-vindo")
st.markdown(
    """
Este projeto apresenta uma análise detalhada de freelancers ao redor do mundo.  
Use o menu lateral para navegar entre as abas e explorar diferentes perspectivas:

- **Visão Geral**: Perfil demográfico, distribuição por país, gênero e principais habilidades.  
- **Preço vs Avaliação**: Comparação entre tarifas horárias e ratings dos freelancers.  
- **Habilidades e Satisfação**: Habilidades mais demandadas e nível de satisfação dos clientes.  
- **Equidade e Gênero**: Distribuição de gênero, experiência e oportunidades.
"""
)

# =====================
# Sobre o dataset
# =====================
st.header("Sobre o Dataset")
st.markdown(
    """

**Fonte:** [Kaggle – Global Freelancers Raw Dataset](https://www.kaggle.com/datasets/urvishahir/global-freelancers-raw-dataset?select=global_freelancers_raw.csv)

**Principais informações disponíveis em cada registro:**
- Dados demográficos: nome, gênero, idade, país
- Dados profissionais: habilidade principal, anos de experiência
- Dados de plataforma: tarifa horária (formatos variados), avaliação do cliente e índice de satisfação
- Idioma falado (baseado no país)
- Valores inconsistentes em várias colunas (ex.: gênero, ativo/inativo, satisfação)
"""
)

# =====================
# Rodapé
# =====================
st.markdown("---")
st.info(
    "💡 Navegue pelas abas para explorar insights e análises detalhadas sobre os freelancers globais."
)
