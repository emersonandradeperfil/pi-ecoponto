import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_estilos_globais,
    renderizar_rodape,
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
# 2. CARREGAMENTO E TRATAMENTO DOS DADOS (PANDAS)
# ============================================================
@st.cache_data
def carregar_dados_analise():
    """
    Carrega o arquivo CSV com suporte a encodings diferentes, trata as datas
    em português e calcula a quantidade de dias de atendimento por chamado.
    """
    caminho_csv = "base_pi_1sem26.csv"

    colunas_base = [
        "Data_Abertura", "Data_Atendimento", "Canal", "Assunto", "Servico",
        "Especificacao", "Situacao", "Orgao", "Logradouro", "Numero", "CEP",
        "Subprefeitura", "Distrito", "Empresa", "Regiao", "Prazo_SLA"
    ]

    try:
        df = pd.read_csv(
            caminho_csv,
            names=colunas_base,
            header=0,
            on_bad_lines="skip",
            encoding="utf-8",
            engine="python"
        )
    except Exception:
        df = pd.read_csv(
            caminho_csv,
            names=colunas_base,
            header=0,
            sep=";",
            on_bad_lines="skip",
            encoding="latin1",
            engine="python"
        )

    # Dicionário para conversão dos meses abreviados do português
    meses_pt = {
        "jan.": "Jan", "fev.": "Feb", "mar.": "Mar", "abr.": "Apr",
        "mai.": "May", "jun.": "Jun", "jul.": "Jul", "ago.": "Aug",
        "set.": "Sep", "out.": "Oct", "nov.": "Nov", "dez.": "Dec"
    }

    for mes_pt, mes_en in meses_pt.items():
        df["Data_Abertura"] = df["Data_Abertura"].astype(str).str.replace(mes_pt, mes_en)
        df["Data_Atendimento"] = df["Data_Atendimento"].astype(str).str.replace(mes_pt, mes_en)

    df["dt_abertura"] = pd.to_datetime(df["Data_Abertura"], format="%d/%b/%y", errors="coerce")
    df["dt_atendimento"] = pd.to_datetime(df["Data_Atendimento"], format="%d/%b/%y", errors="coerce")

    # [CÁLCULO DAX EQUIVALENTE]: Dias de atendimento em relação à data atual (se aberto) ou data de encerramento
    dt_fim = df["dt_atendimento"].fillna(pd.Timestamp.now())
    df["Dias_Atendimento"] = (dt_fim - df["dt_abertura"]).dt.days

    df["Status_Normalizado"] = df["Situacao"].astype(str).str.strip()

    return df

# ============================================================
# 3. EXIBIÇÃO EM COLUNA ÚNICA (LAYOUT VERTICAL)
# ============================================================
try:
    df_chamados = carregar_dados_analise()
    total_geral = len(df_chamados)

    # Função auxiliar para contagens filtradas por texto
    def contar_status(series, termo):
        return series.str.contains(termo, case=False, na=False).sum()

    # Mapeamento de cores igual ao Power BI
    cores_regiao = {
        "SUL": "#1E88E5",
        "LESTE": "#0D47A1",
        "NORTE": "#FF6D00",
        "CENTRO": "#AA00FF",
        "OESTE": "#E91E63"
    }

    # ------------------------------------------------------------
    # SEÇÃO 1: TABELAS E RESUMOS
    # ------------------------------------------------------------
    
    # 2. Resumo por Status
    # st.markdown("### 📌 Resumo por Status")
    # 'total_geral' ou 'len(df_chamados)' traz o total de chamados da base
    st.markdown(f"### {len(df_chamados):,} Chamados".replace(",", "."))
    st.write( "2º trimestre de 2026" )

    df_status = (
        df_chamados.groupby("Status_Normalizado")
        .agg(
            Total_Chamados=("Status_Normalizado", "count"),
            Media_Dias=("Dias_Atendimento", "mean")
        )
        .reset_index()
    )
    df_status["% do Total"] = (df_status["Total_Chamados"] / total_geral * 100).round(2).astype(str) + "%"
    # df_status["Média de Dias"] = df_status["Media_Dias"].round(0).fillna(0).astype(int)
        
    df_status_exibir = df_status[["Status_Normalizado", "Total_Chamados", "% do Total"]]
    df_status_exibir.columns = ["Status", "Total Chamados", "% do Total"]
    st.dataframe(df_status_exibir, use_container_width=True, hide_index=True)
    
    st.divider()


    # Criamos 2 colunas para os gráficos de rosca
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico 1: Rosca - Qtd Aberto por Região
            st.markdown("### Chamados Abertos")
            df_abertos_regiao = (
                df_chamados[df_chamados["Status_Normalizado"].str.contains("Aberto", case=False, na=False)]
                .groupby("Regiao")
                .size()
                .reset_index(name="Qtd_Aberto")
            )
            fig_rosca_abertos = px.pie(
                df_abertos_regiao,
                values="Qtd_Aberto",
                names="Regiao",
                hole=0.6,
                color="Regiao",
                color_discrete_map=cores_regiao
            )
            fig_rosca_abertos.update_traces(textposition="outside", textinfo="value+percent")
            # fig_rosca_abertos.update_layout(
            #     # margin=dict(t=20, b=20, l=10, r=10),
            #     # paper_bgcolor="rgba(0,0,0,0)",
            #     # plot_bgcolor="rgba(0,0,0,0)",
            #     # font=dict(color="#FFFFFF")
            # )
            st.plotly_chart(fig_rosca_abertos, use_container_width=True)
    
    with col_graf2:
        # Gráfico 2: Rosca - Qtd Finalizada por Região
            st.markdown("### Chamados Finalizados")
            df_finalizados_regiao = (
                df_chamados[df_chamados["Status_Normalizado"].str.contains("Finaliz|Atendido", case=False, na=False)]
                .groupby("Regiao")
                .size()
                .reset_index(name="Qtd_Finalizada")
            )
            fig_rosca_final = px.pie(
                df_finalizados_regiao,
                values="Qtd_Finalizada",
                names="Regiao",
                hole=0.6,
                color="Regiao",
                color_discrete_map=cores_regiao
            )
            fig_rosca_final.update_traces(textposition="outside", textinfo="value+percent")
            # fig_rosca_final.update_layout(
            #     margin=dict(t=20, b=20, l=10, r=10),
            #     paper_bgcolor="rgba(0,0,0,0)",
            #     plot_bgcolor="rgba(0,0,0,0)",
            #     font=dict(color="#FFFFFF")
            # )
            st.plotly_chart(fig_rosca_final, use_container_width=True)
    
    st.divider()

    # ============================================================
    # 4. Matriz por Região
    # ============================================================
    st.markdown("### Resumo por Região")

    # 1. Criamos um DataFrame filtrado contendo apenas os chamados concluídos/finalizados com data de atendimento
    df_finalizados = df_chamados[
        (df_chamados["Status_Normalizado"].str.contains("Finaliz|Atendido", case=False, na=False)) &
        (df_chamados["dt_atendimento"].notna())
    ].copy()

    # 2. Calculamos a diferença de dias reais de atendimento (Data Encerramento - Data Abertura)
    df_finalizados["Dias_Atendimento_Real"] = (
        df_finalizados["dt_atendimento"] - df_finalizados["dt_abertura"]
    ).dt.days

    # 3. Calculamos a média de dias de atendimento por região apenas para este grupo
    media_dias_finalizados = (
        df_finalizados.groupby("Regiao")["Dias_Atendimento_Real"]
        .mean()
        .round(0)
        .fillna(0)
        .astype(int)
    )

    # 4. Montamos a matriz principal agrupando todos os chamados por região
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

    # 5. Mapeamos a média de dias apenas dos finalizados para dentro da nossa matriz principal
    df_regiao_matriz["Média de Dias"] = df_regiao_matriz["Regiao"].map(media_dias_finalizados).fillna(0).astype(int)

    # 6. Selecionamos e renomeamos as colunas para exibição na tabela (sem % do Total)
    df_regiao_matriz_exibir = df_regiao_matriz[[
        "Regiao", "Qtd_Distritos","Média de Dias", "Qtd_Finalizada", "Qtd_Aberto", 
        "Qtd_Cancelada", "Total_Chamados"
    ]]

    df_regiao_matriz_exibir.columns = [
        "Região", "Qtd Distritos","Média de Dias", "Qtd Finalizada", "Qtd Aberto", 
        "Qtd Cancelada", "Total Chamados"
    ]

    st.dataframe(df_regiao_matriz_exibir, use_container_width=True, hide_index=True)

    st.divider()

    # 3. Resumo por Empresa Contratada
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

    # 1. Total Chamados por Distrito
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
# 4. COMPONENTES GLOBAIS DE INTERFACE
# ============================================================
renderizar_chat_flutuante()
renderizar_rodape()