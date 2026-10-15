import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

# Paleta de cores padrão para as regiões
CORES_REGIAO = {
    "SUL": "#1E88E5",
    "LESTE": "#0D47A1",
    "NORTE": "#FF6D00",
    "CENTRO": "#AA00FF",
    "OESTE": "#E91E63"
}

# # Função auxiliar para contagens filtradas por texto
def contar_status(series, termo):
    return series.str.contains(termo, case=False, na=False).sum()

def renderizar_tabela_status(df_chamados, total_geral):
  # 1. Agrupa os dados apenas por Status Normalizado e conta o total
  df_status = (
      df_chamados.groupby("Status_Normalizado")
      .agg(Total_Chamados=("Status_Normalizado", "count"))
      .reset_index()
  )

  # 2. Calcula a porcentagem do total com segurança
  if total_geral > 0:
    df_status["% do Total"] = (
        (df_status["Total_Chamados"] / total_geral) * 100
    ).round(2)
  else:
    df_status["% do Total"] = 0.0

  # 3. Formata os valores numéricos com o padrão brasileiro (ponto nos milhares)
  df_status["Total_Chamados_Fmt"] = df_status["Total_Chamados"].apply(
      lambda x: f"{x:,.0f}".replace(",", ".")
  )
  df_status["% do Total_Fmt"] = df_status["% do Total"].apply(
      lambda x: f"{x:.2f}%".replace(".", ",")
  )

  # 4. Seleciona e renomeia as colunas finais para exibição
  df_status_exibir = df_status[
      ["Status_Normalizado", "Total_Chamados_Fmt", "% do Total_Fmt"]
  ].copy()
  df_status_exibir.columns = ["Status", "Total Chamados", "% do Total"]

  # 5. Renderiza no Streamlit
  st.dataframe(df_status_exibir, use_container_width=True, hide_index=True)

def renderizar_matriz_regiao_status(df_chamados):
  """Renderiza a matriz cruzando Status do Chamado e Regiões com Totais automáticos."""
  st.markdown("### Resumo de Chamados por Região e Status")

  if df_chamados.empty:
    st.warning("Nenhum dado disponível para gerar a matriz.")
    return

  # 1. Garante a coluna de Região caso venha tratada do ETL
  if "Regiao" not in df_chamados.columns and "Distrito" in df_chamados.columns:
    # Se precisar mapear aqui caso não venha pronta
    pass

  # 2. Padroniza o texto do Status em dois grupos principais: "Aberto" e "Finalizado"
  df_chamados["Status_Grupo"] = df_chamados["Status_Normalizado"].apply(
      lambda x: "Aberto" if "Aberto" in str(x) else "Finalizado"
  )

  # 3. Cria a tabela pivotada com totais automáticos (margins=True)
  tabela_resumo = pd.pivot_table(
      df_chamados,
      index="Status_Grupo",
      columns="Regiao",
      values="Número",
      aggfunc="count",
      fill_value=0,
      margins=True,  # Adiciona a linha e coluna de totais
      margins_name="TOTAL",  # Renomeia para TOTAL
  )

  # 4. Organiza a ordem das colunas, mantendo o TOTAL no final
  colunas_base = [
      c
      for c in ["LESTE", "NORTE", "SUL", "OESTE", "CENTRO", "OUTRAS"]
      if c in tabela_resumo.columns
  ]
  colunas_finais = colunas_base + (
      ["TOTAL"] if "TOTAL" in tabela_resumo.columns else []
  )
  tabela_resumo = tabela_resumo[colunas_finais]

  # 5. Reseta o index para virar coluna limpa e renomeia
  tabela_streamlit = tabela_resumo.reset_index().rename(
      columns={"Status_Grupo": "Status"}
  )

  # 6. Formata os números com ponto nos milhares (padrão brasileiro)
  for col in tabela_streamlit.columns:
    if col != "Status":
      tabela_streamlit[col] = tabela_streamlit[col].apply(
          lambda x: f"{x:,.0f}".replace(",", ".")
      )

  # 7. Renderiza no Streamlit sem poluição visual de índice
  st.dataframe(tabela_streamlit, use_container_width=True, hide_index=True)

def renderizar_barra_abertos_regiao(df_chamados):
  """Renderiza um gráfico de rosca com os chamados abertos agrupados por região."""
  # st.markdown("### Chamados Abertos por Região")

  if df_chamados.empty:
    st.warning("Nenhum dado disponível.")
    return

  # 1. Filtra apenas os chamados que estão com status Aberto
  if "Status_Normalizado" in df_chamados.columns:
    df_abertos = df_chamados[
        df_chamados["Status_Normalizado"].str.contains(
            "Aberto", case=False, na=False
        )
    ]
  else:
    st.warning("Coluna de status normalizado não encontrada.")
    return

  if df_abertos.empty:
    st.info("Não há chamados abertos no momento.")
    return

  # 2. Agrupa por Região contando a quantidade
  df_grouped = (
      df_abertos.groupby("Regiao", as_index=False)
      .size()
      .rename(columns={"size": "Quantidade"})
  )

  total_bruto = df_grouped["Quantidade"].sum()
  total_geral = f"{total_bruto:,.0f}".replace(",", ".")

#   # 3. Cria o gráfico de barra com Plotly Express

  fig = px.bar(
        df_grouped,
        x="Regiao",
        y="Quantidade",
        color="Regiao",
        color_discrete_map=CORES_REGIAO,
        text="Quantidade"  # Exibe o valor numérico junto à barra
    )

# Ajustes finos de layout para o gráfico de barras em 180x180px
  fig.update_layout(
      width=180,
      height=180,
      margin=dict(t=30, b=25, l=10, r=10),  # b=25 garante espaço para os nomes das regiões embaixo
      showlegend=False,
      separators=",.",
      title=dict(
          text=f"{total_geral} chamados em aberto do 156",
          x=0.5,            
          xanchor="center", 
      ),
      xaxis=dict(
        title=None, showgrid=False),                      # Remove o rótulo padrão do eixo X para economizar espaço
      yaxis=dict(title=None, showticklabels=False, showgrid=False) # Oculta os números do eixo Y (já que usamos o 'text' nas barras)
  )
  
  # Ajusta a posição e o tamanho do texto nas barras
  fig.update_traces(
      textposition="inside",
      textfont=dict(size=9)
  )

  # 4. Exibe no Streamlit
  st.plotly_chart(fig, use_container_width=True)

def renderizar_pizza_finalizados_regiao(df_chamados):
  """Renderiza um gráfico de rosca com os chamados abertos agrupados por região."""
  # st.markdown("### Chamados Abertos por Região")

  if df_chamados.empty:
    st.warning("Nenhum dado disponível.")
    return

  # 1. Filtra apenas os chamados que estão com status Aberto
  if "Status_Normalizado" in df_chamados.columns:
    df_abertos = df_chamados[
        df_chamados["Status_Normalizado"].str.contains(
            "Finalizada", case=False, na=False
        )
    ]
  else:
    st.warning("Coluna de status normalizado não encontrada.")
    return

  if df_abertos.empty:
    st.info("Não há chamados finalizados no momento.")
    return

  # 2. Agrupa por Região contando a quantidade
  df_grouped = (
      df_abertos.groupby("Regiao", as_index=False)
      .size()
      .rename(columns={"size": "Quantidade"})
  )

  # 3. Cria o gráfico de pizza/rosca com Plotly Express
  fig = px.pie(
      df_grouped,
      names="Regiao",
      values="Quantidade",
    # hole=0.4,  # Deixa o centro vazado estilo gráfico de rosca (donut)
      color="Regiao",
      color_discrete_map=CORES_REGIAO,
  )

  # Ajustes finos de layout para ficar bonito no tema escuro/claro
  fig.update_layout(
    width=300,
    height=300,
    margin=dict(t=30, b=10, l=10, r=10),  # Margens reduzidas para caber no espaço pequeno
    showlegend=False,
    separators=",.",
    title=dict(
        text="Chamados finalizados",
        x=0.5,            # Centraliza horizontalmente (0.5 = meio)
        xanchor="center", # Garante que o ponto de ancoragem seja o centro
    )
)

  fig.update_traces(textinfo="label+value+percent", textposition="inside")

  #4. Exibe no Streamlit
  st.plotly_chart(fig, use_container_width=True)

def renderizar_pizza_abertos_regiao(df_chamados):
  """Renderiza um gráfico de rosca com os chamados abertos agrupados por região."""
  # st.markdown("### Chamados Abertos por Região")

  if df_chamados.empty:
    st.warning("Nenhum dado disponível.")
    return

  # 1. Filtra apenas os chamados que estão com status Aberto
  if "Status_Normalizado" in df_chamados.columns:
    df_abertos = df_chamados[
        df_chamados["Status_Normalizado"].str.contains(
            "Aberto", case=False, na=False
        )
    ]
  else:
    st.warning("Coluna de status normalizado não encontrada.")
    return

  if df_abertos.empty:
    st.info("Não há chamados abertos no momento.")
    return

  # 2. Agrupa por Região contando a quantidade
  df_grouped = (
      df_abertos.groupby("Regiao", as_index=False)
      .size()
      .rename(columns={"size": "Quantidade"})
  )

  # 3. Cria o gráfico de pizza/rosca com Plotly Express
  fig = px.pie(
      df_grouped,
      names="Regiao",
      values="Quantidade",
    # hole=0.4,  # Deixa o centro vazado estilo gráfico de rosca (donut)
      color="Regiao",
      color_discrete_map=CORES_REGIAO,
  )

  # Ajustes finos de layout para ficar bonito no tema escuro/claro
  fig.update_layout(
    width=300,
    height=300,
    margin=dict(t=30, b=10, l=10, r=10),  # Margens reduzidas para caber no espaço pequeno
    showlegend=False,
    separators=",.",
    title=dict(
        text="Chamados em Aberto",
        x=0.5,            # Centraliza horizontalmente (0.5 = meio)
        xanchor="center", # Garante que o ponto de ancoragem seja o centro
    )
)

  fig.update_traces(textinfo="label+value+percent", textposition="inside")

  #4. Exibe no Streamlit
  st.plotly_chart(fig, use_container_width=True)