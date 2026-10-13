import plotly.express as px
import plotly.graph_objects as go
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

def renderizar_grafico_rosca_abertos(df_chamados):
    """Renderiza o gráfico de rosca de chamados abertos por região."""
    st.markdown("### Chamados Abertos")
    df_abertos_regiao = (
        df_chamados[df_chamados["Status_Normalizado"].str.contains("Aberto", case=False, na=False)]
        .groupby("Regiao")
        .size()
        .reset_index(name="Qtd_Aberto")
    )
    
    fig = px.pie(
        df_abertos_regiao,
        values="Qtd_Aberto",
        names="Regiao",
        hole=0.6,
        color="Regiao",
        color_discrete_map=CORES_REGIAO
    )
    fig.update_traces(textposition="outside", textinfo="value+percent")
    fig.update_layout(
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF")
    )
    st.plotly_chart(fig, use_container_width=True)

def renderizar_grafico_rosca_finalizados(df_chamados):
    """Renderiza o gráfico de rosca de chamados finalizados por região."""
    st.markdown("### Chamados Finalizados")
    df_finalizados_regiao = (
        df_chamados[df_chamados["Status_Normalizado"].str.contains("Finaliz|Atendido", case=False, na=False)]
        .groupby("Regiao")
        .size()
        .reset_index(name="Qtd_Finalizada")
    )
    
    fig = px.pie(
        df_finalizados_regiao,
        values="Qtd_Finalizada",
        names="Regiao",
        hole=0.6,
        color="Regiao",
        color_discrete_map=CORES_REGIAO
    )
    fig.update_traces(textposition="outside", textinfo="value+percent")
    fig.update_layout(
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF")
    )
    st.plotly_chart(fig, use_container_width=True)

def renderizar_grafico_linha_abertos_media(df_chamados, media_dias_regiao):
    """Renderiza o gráfico de linha combinando Qtd Aberto e Média de Dias por Região."""
    st.markdown("### 📉 Qtd Aberto e Média de Dias (Linha)")
    
    df_linha = (
        df_chamados.groupby("Regiao")
        .agg(Qtd_Aberto=("Status_Normalizado", lambda x: contar_status(x, "Aberto")))
        .reset_index()
    )
    df_linha["Media_Dias"] = df_linha["Regiao"].map(media_dias_regiao).fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_linha["Regiao"], y=df_linha["Qtd_Aberto"],
        mode='lines+markers', name='Qtd Aberto', line=dict(color='#1E88E5', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df_linha["Regiao"], y=df_linha["Media_Dias"],
        mode='lines+markers', name='Média de Dias (Finalizados)', line=dict(color='#0D47A1', width=3)
    ))
    fig.update_layout(
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

def renderizar_grafico_barras_abertos_media(df_chamados, media_dias_regiao):
    """Renderiza o gráfico de barras agrupadas combinando Qtd Aberto e Média de Dias por Região."""
    st.markdown("### 📊 Qtd Aberto e Média de Dias (Barras Agrupadas)")
    
    df_linha = (
        df_chamados.groupby("Regiao")
        .agg(Qtd_Aberto=("Status_Normalizado", lambda x: contar_status(x, "Aberto")))
        .reset_index()
    )
    df_linha["Media_Dias"] = df_linha["Regiao"].map(media_dias_regiao).fillna(0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_linha["Regiao"], y=df_linha["Qtd_Aberto"],
        name='Qtd Aberto', marker_color='#1E88E5'
    ))
    fig.add_trace(go.Bar(
        x=df_linha["Regiao"], y=df_linha["Media_Dias"],
        name='Média de Dias (Finalizados)', marker_color='#0D47A1'
    ))
    fig.update_layout(
        barmode='group',
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#FFFFFF"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

def renderizar_grafico_pizza_abertos(df_chamados):
    """Renderiza o gráfico de rosca de chamados abertos por região."""

    # st.markdown("### Chamados Abertos")
    df_abertos_regiao = (
        df_chamados[df_chamados["Status_Normalizado"].str.contains("Aberto", case=False, na=False)]
        .groupby("Regiao")
        .size()
        .reset_index(name="Qtd_Aberto")
    )
    
    fig = px.pie(
        df_abertos_regiao,
        values="Qtd_Aberto",
        names="Regiao",
        # hole=0.6,
        color="Regiao",
        color_discrete_map=CORES_REGIAO
    )

    fig.update_traces(textposition="inside", textinfo="label+percent")

    fig.update_layout(
        title={

            'text': "Chamados Abertos 156",
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'

        },
        width=200,
        height=200,
        showlegend=False,
        margin=dict(t=20, b=20, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        # font=dict(color="rgba(0,0,0,0)")
    )
    st.plotly_chart(fig, use_container_width=True)

def renderizar_tabela_regiao(df_chamados):

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

def renderizar_tabela_empresa(df_chamados, total_geral):

    
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

def renderizar_tabela_status(df_chamados, total_geral):

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

def renderizar_tabela_distrito(df_chamados):
    df_distritos = (
            df_chamados.groupby("Distrito")
            .size()
            .reset_index(name="Total Chamados")
            .sort_values(by="Total Chamados", ascending=False)
        )
    st.dataframe(df_distritos, use_container_width=True, height=300, hide_index=True)        