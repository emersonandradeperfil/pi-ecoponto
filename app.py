import streamlit as st

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_estilos_globais,
    renderizar_rodape,
)

# ============================================================
#  [INTERFACE] PÁGINA INICIAL (HOME)
# ============================================================

st.set_page_config(page_title="PI - Ecoponto", page_icon="🌱", layout="wide")
renderizar_estilos_globais()

# CSS para transformar o container em um card 100% clicável
st.markdown(
    """
    <style>
    /* Torna o container relativo para posicionar o botão por cima */
    div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] {
        position: relative;
    }
    
    /* Faz o botão preencher todo o container e ficar invisível por cima do texto */
    div[data-testid="stPageLink"] a {
        position: absolute !important;
        top: -120px !important;
        left: -16px !important;
        width: calc(100% + 32px) !important;
        height: 180px !important;
        opacity: 0 !important;
        z-index: 10 !important;
        cursor: pointer !important;
    }

    /* Efeito suave de hover no container quando o cursor passa em cima */
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: var(--primary-color, #4CAF50) !important;
        transform: translateY(-3px);
        transition: all 0.2s ease-in-out;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌱 Ecopontos de SP")
st.write(
    "Sistema desenvolvido para ajudar você a encontrar **ecopontos** oficiais "
    "na cidade de **São Paulo**."
)

st.divider()

st.subheader("Como usar")
st.write("Clique em qualquer um dos cartões abaixo para navegar pelo sistema:")

# ============================================================
# CARDS CLICÁVEIS DE NAVEGAÇÃO
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
  with st.container(border=True):
    st.markdown("### 💬 Chat")
    st.write("Converse com o assistente virtual para tirar dúvidas.")
    st.page_link("pages/1_💬_Chat.py", label="Ir", use_container_width=True)

with col2:
  with st.container(border=True):
    st.markdown("### 🏢 Unidade")
    st.write("Selecione um ecoponto específico e veja detalhes.")
    st.page_link("pages/2_🏢_Unidade.py", label="Ir", use_container_width=True)

with col3:
  with st.container(border=True):
    st.markdown("### 🔍 Região")
    st.write("Veja todos os ecopontos disponíveis em uma zona.")
    st.page_link("pages/3_🔍_Regiao.py", label="Ir", use_container_width=True)

with col4:
  with st.container(border=True):
    st.markdown("### 📊 Análises")
    st.write("Acompanhe o painel e os indicadores dos chamados SP156.")
    st.page_link("pages/4_📊_Analises.py", label="Ir", use_container_width=True)

# ============================================================
# COMPONENTES GLOBAIS
# ============================================================

renderizar_chat_flutuante()
renderizar_rodape()