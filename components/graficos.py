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
    
    def contar_status(series, termo):
        return series.str.contains(termo, case=False, na=False).sum()

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
    
    def contar_status(series, termo):
        return series.str.contains(termo, case=False, na=False).sum()

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



