import os
import streamlit as st
import pandas as pd

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_estilos_globais,
    renderizar_rodape,
    baixar_csv
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

st.title("📊 Análises e Indicadores (SP 156)")
st.write(
    "Acompanhe o desempenho, volume de chamados e métricas operacionais "
    "das empresas e subprefeituras da cidade de São Paulo."
)

# ============================================================
# 2. CARREGAMENTO DOS GRÁFICOS
# ============================================================
try:
    df_chamados = carregar_dados_analise()
    total_geral = len(df_chamados)
    # de_para_regiao = regiaodistrito()
    

    # ------------------------------------------------------------
    # SEÇÃO 1: CABEÇALHO
    # ------------------------------------------------------------
    st.markdown(f"### Chamados: {total_geral:,} ".replace(",", "."))

    # Pega a menor data real e a maior data (filtrando para não pegar os chamados agendados no futuro)
    if "Data de Abertura" in df_chamados.columns:
        s = df_chamados.loc[
            df_chamados["Data de Abertura"] <= pd.Timestamp.today(), "Data de Abertura"
        ]
    if not s.empty:
        st.write(f"Período: De {s.min():%d/%m/%Y} até {s.max():%d/%m/%Y}")

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