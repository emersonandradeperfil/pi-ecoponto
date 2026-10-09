import pandas as pd
import plotly.express as px
import streamlit as st

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_estilos_globais,
    renderizar_rodape,
)

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Análises - PI Ecoponto", page_icon="📊", layout="wide"
)

renderizar_estilos_globais()

st.title("📊 Painel de Análises e Indicadores")
st.write(
    "Acompanhe o desempenho, volume de chamados e métricas dos ecopontos e"
    " serviços de limpeza urbana da cidade de São Paulo."
)

st.divider()

# ============================================================
# [SESSÃO] CARREGAMENTO E TRATAMENTO DOS DADOS (PANDAS)
# ============================================================


@st.cache_data
def carregar_dados_analise():
  caminho_csv = "base_pi_1sem26.csv"

  # Nomes das colunas da sua base
  colunas_base = [
      "Data_Abertura",
      "Data_Atendimento",
      "Canal",
      "Assunto",
      "Servico",
      "Especificacao",
      "Situacao",
      "Orgao",
      "Logradouro",
      "Numero",
      "CEP",
      "Subprefeitura",
      "Distrito",
      "Empresa",
      "Regiao",
      "Prazo_SLA",
  ]

  try:
    df = pd.read_csv(
        caminho_csv,
        names=colunas_base,
        header=0,
        on_bad_lines="skip",
        encoding="utf-8",
        engine="python",
    )
  except Exception:
    df = pd.read_csv(
        caminho_csv,
        names=colunas_base,
        header=0,
        sep=";",
        on_bad_lines="skip",
        encoding="latin1",
        engine="python",
    )

  # Converte as datas de texto para datetime (padrão brasileiro/português)
  # Mapeia meses abreviados do português (jan., fev., mar., etc.)
  meses_pt = {
      "jan.": "Jan",
      "fev.": "Feb",
      "mar.": "Mar",
      "abr.": "Apr",
      "mai.": "May",
      "jun.": "Jun",
      "jul.": "Jul",
      "ago.": "Aug",
      "set.": "Sep",
      "out.": "Oct",
      "nov.": "Nov",
      "dez.": "Dec",
  }

  for mes_pt, mes_en in meses_pt.items():
    df["Data_Abertura"] = (
        df["Data_Abertura"].astype(str).str.replace(mes_pt, mes_en)
    )
    df["Data_Atendimento"] = (
        df["Data_Atendimento"].astype(str).str.replace(mes_pt, mes_en)
    )

  df["dt_abertura"] = pd.to_datetime(
      df["Data_Abertura"], format="%d/%b/%y", errors="coerce"
  )
  df["dt_atendimento"] = pd.to_datetime(
      df["Data_Atendimento"], format="%d/%b/%y", errors="coerce"
  )

  # Equivale à MEDIDA do Power BI: Calcula a duração real do atendimento em dias
  dt_fim = df["dt_atendimento"].fillna(pd.Timestamp.now())
  df["Dias_Atendimento"] = (dt_fim - df["dt_abertura"]).dt.days

  return df


# ============================================================
# PROCESSAMENTO E EXIBIÇÃO DE KPIS E GRÁFICOS
# ============================================================

try:
  df_chamados = carregar_dados_analise()

  # ------------------------------------------------------------
  # COMPUTAÇÃO DAS MÉTRICAS (KPIs)
  # ------------------------------------------------------------
  total_chamados = len(df_chamados)

  # Equivale às MEDIDAS do Power BI para contagem por Situação
  qtd_finalizados = len(
      df_chamados[
          df_chamados["Situacao"].astype(str).str.lower().str.contains("final")
      ]
  )
  qtd_abertos = total_chamados - qtd_finalizados

  # Média equivalente ao AVERAGE(Dias_Atendimento)
  media_dias = round(df_chamados["Dias_Atendimento"].mean(), 1)

  # Exibição dos Cards de KPI
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("📦 Total de Chamados", f"{total_chamados:,}".replace(",", "."))
  col2.metric("🟢 Chamados em Aberto", f"{qtd_abertos:,}".replace(",", "."))
  col3.metric("🔴 Chamados Finalizados", f"{qtd_finalizados:,}".replace(",", "."))
  col4.metric("⏱️ Média SLA Real", f"{media_dias} dias")

  st.divider()

  # ------------------------------------------------------------
  # GRÁFICOS INTERATIVOS (PLOTLY)
  # ------------------------------------------------------------
  st.subheader("📈 Visão Geral por Região")

  col_graf1, col_graf2 = st.columns(2)

  # 1. GRÁFICO DE ROSCA: Distribuição por Região (LESTE, NORTE, SUL, OESTE, CENTRO)
  with col_graf1:
    df_regiao_qtd = (
        df_chamados.groupby("Regiao").size().reset_index(name="Qtd_Chamados")
    )

    fig_rosca = px.pie(
        df_regiao_qtd,
        values="Qtd_Chamados",
        names="Regiao",
        title="<b>Distribuição de Chamados por Região</b>",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_rosca.update_traces(textposition="inside", textinfo="percent+label")
    fig_rosca.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="var(--text-color, #ffffff)"),
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_rosca, use_container_width=True)

  # 2. GRÁFICO DE BARRAS: Média de Dias de Atendimento por Região
  with col_graf2:
    df_media_regiao = (
        df_chamados.groupby("Regiao")["Dias_Atendimento"]
        .mean()
        .round(1)
        .reset_index(name="Media_Dias")
        .sort_values(by="Media_Dias", ascending=False)
    )

    fig_barras = px.bar(
        df_media_regiao,
        x="Regiao",
        y="Media_Dias",
        title="<b>Média de Dias de Atendimento por Região</b>",
        text="Media_Dias",
        color="Regiao",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_barras.update_traces(
        texttemplate="%{text} dias", textposition="outside"
    )
    fig_barras.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="var(--text-color, #ffffff)"),
        showlegend=False,
        xaxis_title="Região",
        yaxis_title="Média (Dias)",
        margin=dict(t=40, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_barras, use_container_width=True)

except Exception as e:
  st.error(
      "Erro ao carregar ou processar o arquivo local 'base_pi_1sem26.csv':"
      f" {e}"
  )

# ============================================================
# COMPONENTES GLOBAIS
# ============================================================
renderizar_chat_flutuante()
renderizar_rodape()