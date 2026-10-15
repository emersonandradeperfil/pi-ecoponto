import streamlit as st


from components.layout import (
    renderizar_chat_flutuante,
    renderizar_rodape,
)

from database.baseapi import carregar_dados_analise
from components.graficos import renderizar_barra_abertos_regiao

# ============================================================
#  [INTERFACE] PÁGINA INICIAL (HOME)
# ============================================================

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

try:
    df_chamados = carregar_dados_analise()
    total_geral = len(df_chamados)

    # Função auxiliar para contagens filtradas por texto
    def contar_status(series, termo):
        return series.str.contains(termo, case=False, na=False).sum()

except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados para o painel de análises: {e}")


colu1, colu2 = st.columns(2)

st.markdown(
    """
    <style>
    /* Alinha verticalmente ao centro o conteúdo de TODAS as colunas */
    [data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    h1, h2, p {text-align: center;}

    /* Aumenta o tamanho da fonte dos títulos (h1) */
    h1 {font-size: 150px !important; }
    h2 {font-size: 40px !important;}
    </style>
    """,
    unsafe_allow_html=True
)

with colu1:
    st.title("♻️")
    st.header("Limpeza Urbana SP")
    st.write(
        "*Seu portal inteligente de limpeza urbana*"
    )

with colu2:
    renderizar_barra_abertos_regiao(df_chamados)

st.divider()

# ============================================================
# CARDS CLICÁVEIS DE NAVEGAÇÃO
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
  with st.container(border=True):
    st.markdown("### 💬 Chat")
    st.write("Assistente de IA")
    st.page_link("pages/1_💬_Chat.py", label="Ir", use_container_width=True)

with col2:
  with st.container(border=True):
    st.markdown("### 🏢 Unidade")
    st.write("Unidades do Ecoponto")
    st.page_link("pages/2_🏢_Unidade.py", label="Ir", use_container_width=True)

with col3:
  with st.container(border=True):
    st.markdown("### 🔍 Região")
    st.write("Ecopontos por região")
    st.page_link("pages/3_🔍_Regiao.py", label="Ir", use_container_width=True)

with col4:
  with st.container(border=True):
    st.markdown("### 📊 Análises")
    st.write("Chamados do 156 - SP")
    st.page_link("pages/4_📊_Analises.py", label="Ir", use_container_width=True)

# ============================================================
# COMPONENTES GLOBAIS
# ============================================================

renderizar_chat_flutuante()
renderizar_rodape()