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
# 2. CARREGAMENTO E PROCESSAMENTO DOS DADOS
# ============================================================
try:
    df_chamados = carregar_dados_analise()
    total_geral = len(df_chamados)

    # Função auxiliar para contagens filtradas por texto
    def contar_status(series, termo):
        return series.str.contains(termo, case=False, na=False).sum()

    # ------------------------------------------------------------
    # SEÇÃO 1: TABELA DE RESUMO POR STATUS
    # ------------------------------------------------------------
    st.markdown(f"### {total_geral:,} Chamados".replace(",", "."))
    st.write("2º trimestre de 2026")

    df_status = (
        df_chamados.groupby("Status_Normalizado")
        .agg(
            Total_Chamados=("Status_Normalizado", "count"),
            Media_Dias=("Dias_Atendimento", "mean")
        )
        .reset_index()
    )
    df_status["% do Total"] = (df_status["Total_Chamados"] / total_geral * 100).round(2).astype(str) + "%"
        
    df_status_exibir = df_status[["Status_Normalizado", "Total_Chamados", "% do Total"]]
    df_status_exibir.columns = ["Status", "Total Chamados", "% do Total"]
    st.dataframe(df_status_exibir, use_container_width=True, hide_index=True)
    
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

    # 1. DataFrame filtrado apenas para finalizados com data de atendimento válida
    df_finalizados = df_chamados[
        (df_chamados["Status_Normalizado"].str.contains("Finaliz|Atendido", case=False, na=False)) &
        (df_chamados["dt_atendimento"].notna())
    ].copy()

    # 2. Dias reais de atendimento (Data Encerramento - Data Abertura)
    df_finalizados["Dias_Atendimento_Real"] = (
        df_finalizados["dt_atendimento"] - df_finalizados["dt_abertura"]
    ).dt.days

    # 3. Média de dias por região
    media_dias_finalizados = (
        df_finalizados.groupby("Regiao")["Dias_Atendimento_Real"]
        .mean()
        .round(0)
        .fillna(0)
        .astype(int)
    )

    # 4. Montagem da matriz principal
    df_regiao_matriz = (
        df_chamados.groupby("Regiao")
        .agg(
            Qtd_Distritos=("Distrito", "nunique"),
            Qtd_Aberto=("Status_Normalizado", lambda x: contar_status(x, "Aberto")),
            Qtd_Finalizada=("Status_Normalizado", lambda x: contar_status(x, "Finaliz|Atendido")),
            Qtd_Cancelada=("Status_Normalizado", lambda x: contar_status(x, "Cancel")),
            Total_Chamados=("Status_Normalizado", "count")
        )
        .reset_index()
    )

    # 5. Mapeamento da média de dias
    df_regiao_matriz["Média de Dias"] = df_regiao_matriz["Regiao"].map(media_dias_finalizados).fillna(0).astype(int)

    # 6. Seleção e ordenação de colunas para exibição
    df_regiao_matriz_exibir = df_regiao_matriz[[
        "Regiao", "Qtd_Distritos", "Média de Dias", "Qtd_Finalizada", "Qtd_Aberto", 
        "Qtd_Cancelada", "Total_Chamados"
    ]]

    df_regiao_matriz_exibir.columns = [
        "Região", "Qtd Distritos", "Média de Dias", "Qtd Finalizada", "Qtd Aberto", 
        "Qtd Cancelada", "Total Chamados"
    ]

    st.dataframe(df_regiao_matriz_exibir, use_container_width=True, hide_index=True)

    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 4: RESUMO POR EMPRESA CONTRATADA
    # ------------------------------------------------------------
    st.markdown("### Resumo por Empresa")
    df_empresa = (
        df_chamados.groupby("Empresa")
        .agg(
            Qtd_Finalizada=("Status_Normalizado", lambda x: contar_status(x, "Finaliz|Atendido")),
            Qtd_Aberto=("Status_Normalizado", lambda x: contar_status(x, "Aberto")),
            Qtd_Cancelada=("Status_Normalizado", lambda x: contar_status(x, "Cancel")),
            Total_Chamados=("Status_Normalizado", "count")
        )
        .reset_index()
    )
    df_empresa["% do Total"] = (df_empresa["Total_Chamados"] / total_geral * 100).round(2).astype(str) + "%"
    df_empresa.columns = ["Empresa", "Qtd Finalizada", "Qtd Aberto", "Qtd Cancelada", "Total Chamados", "% do Total"]
    st.dataframe(df_empresa, use_container_width=True, hide_index=True)

    st.divider()

    # ------------------------------------------------------------
    # SEÇÃO 5: CHAMADOS POR DISTRITO
    # ------------------------------------------------------------
    st.markdown("### Chamados por Distrito")
    df_distritos = (
        df_chamados.groupby("Distrito")
        .size()
        .reset_index(name="Total Chamados")
        .sort_values(by="Total Chamados", ascending=False)
    )
    st.dataframe(df_distritos, use_container_width=True, height=300, hide_index=True)

except Exception as e:
    st.error(f"Erro ao carregar ou processar os dados para o painel de análises: {e}")

# ============================================================
# 3. COMPONENTES GLOBAIS DE INTERFACE
# ============================================================
renderizar_chat_flutuante()
renderizar_rodape()