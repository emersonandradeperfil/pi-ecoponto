import streamlit as st
# import pandas as pd

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_estilos_globais,
    renderizar_rodape,
    baixar_csv,
    perido,
)

# from database.conexao import carregar_dados_analise

from database.baseapi import carregar_dados_analise
# from database.regiao import regiaodistrito
from components.graficos import (
    renderizar_tabela_status,
    renderizar_pizza_abertos_regiao,
    renderizar_pizza_finalizados_regiao
)

# from components.graficos import (
#     renderizar_grafico_rosca_abertos,
#     renderizar_grafico_rosca_finalizados,
#     renderizar_tabela_regiao,
#     renderizar_tabela_status,
#     renderizar_tabela_empresa,
#     renderizar_tabela_distrito
# )


# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Análises - PI Ecoponto",
    page_icon="📊",
    layout="wide"
)

renderizar_estilos_globais()

st.title("📊 Análises e Indicadores")
st.write(
    "Análise e métricas operacionais dos chamados do 156 nas subprefeituras e empresas da cidade de São Paulo."
)

# ============================================================
# 2. CARREGAMENTO DOS GRÁFICOS
# ============================================================
try:
    df_chamados = carregar_dados_analise()
    total_geral = len(df_chamados)
    
    # ------------------------------------------------------------
    # SEÇÃO 1: CABEÇALHO
    # ------------------------------------------------------------
    st.markdown(f"### {total_geral:,} chamados ".replace(",", "."))
    perido(df_chamados)

    st.divider()
    # ------------------------------------------------------------
    # SEÇÃO 2: TABELA DE RESUMO POR STATUS
    # ------------------------------------------------------------

    renderizar_tabela_status(df_chamados, total_geral)
    
    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 3: TABELA DE ABERTO POR REGIÃO
    # ------------------------------------------------------------

    colu1, colu2 = st.columns(2)

    with colu1:
        renderizar_pizza_abertos_regiao(df_chamados)
    with colu2:
        renderizar_pizza_finalizados_regiao(df_chamados)

except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados para o painel de análises: {e}")

baixar_csv(df_chamados)

# ============================================================
# 3. COMPONENTES GLOBAIS DE INTERFACE
# ============================================================

renderizar_chat_flutuante()
renderizar_rodape()