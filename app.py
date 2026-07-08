import streamlit as st

from components.layout import (
    renderizar_estilos_globais,
    renderizar_chat_flutuante,
    renderizar_rodape,
)

# ============================================================
#  [INTERFACE] PÁGINA INICIAL (HOME)
# ============================================================

st.set_page_config(page_title="PI - Ecoponto", page_icon="🌱", layout="wide")
renderizar_estilos_globais()

st.title("🌱 PI sobre Ecopontos de SP")
st.write(
    "Bem-vindo! Use o menu lateral para acessar o **Assistente Virtual (Chat)**, "
    "a **Busca por Unidade** ou a **Busca por Região**."
)
st.markdown("---")

st.subheader("Como usar")
st.markdown("""
Clique no ícone ">>" no canto superior esquerdo para abrir o menu e escolha uma das opções de busca:

- **💬 Chat** — converse com o assistente e descreva o que quer descartar e onde você mora.
- **🏢 Unidade** — selecione um ecoponto específico para ver seus detalhes.
- **🔍 Região** — veja todos os ecopontos de uma zona da cidade.
""")

renderizar_chat_flutuante()
renderizar_rodape()
