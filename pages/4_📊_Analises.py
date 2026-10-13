import streamlit as st

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_estilos_globais,
    renderizar_rodape,
)

from database.conexao import carregar_dados_analise

from components.graficos import (
    renderizar_grafico_rosca_abertos,
    renderizar_grafico_rosca_finalizados,
    renderizar_tabela_regiao,
    renderizar_tabela_status,
    renderizar_tabela_empresa,
    renderizar_tabela_distrito
)

# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ============================================================
st.set_page_config(
    page_title="Análises - PI Ecoponto",
    page_icon="📊",
    layout="wide"
)

renderizar_estilos_globais()

st.title("📊 Análises e Indicadores (SP 156)")
st.write(
    "Acompanhe o desempenho, volume de chamados e métricas operacionais "
    "das empresas e subprefeituras da cidade de São Paulo."
)

st.divider()

# ============================================================
# 2. CARREGAMENTO DOS GRÁFICOS
# ============================================================
try:
    df_chamados = carregar_dados_analise()
    total_geral = len(df_chamados)

    # ------------------------------------------------------------
    # SEÇÃO 1: TABELA DE RESUMO POR STATUS
    # ------------------------------------------------------------
    renderizar_tabela_status(df_chamados, total_geral)

    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 2: GRÁFICOS DE ROSCA (VIA COMPONENTE MODULAR)
    # ------------------------------------------------------------
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        renderizar_grafico_rosca_abertos(df_chamados)
    
    with col_graf2:
        renderizar_grafico_rosca_finalizados(df_chamados)
    
    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 3: MATRIZ POR REGIÃO
    # ------------------------------------------------------------
    st.markdown("### Resumo por Região")
    renderizar_tabela_regiao(df_chamados)

    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 4: RESUMO POR EMPRESA CONTRATADA
    # ------------------------------------------------------------
    st.markdown("### Resumo por Empresa")
    renderizar_tabela_empresa(df_chamados, total_geral)

    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 5: CHAMADOS POR DISTRITO
    # ------------------------------------------------------------
    st.markdown("### Chamados por Distrito")
    renderizar_tabela_distrito(df_chamados)

except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados para o painel de análises: {e}")

# ============================================================
# 3. COMPONENTES GLOBAIS DE INTERFACE
# ============================================================
# renderizar_chat_flutuante()
renderizar_rodape()