import urllib.parse
import streamlit as st

from components.layout import (
    renderizar_estilos_globais,
    renderizar_chat_flutuante,
    renderizar_rodape
)

from database.conexao import (
    buscar_ecopontos_por_zona
)


# ============================================================
# [SESSÃO] BUSCA POR REGIÃO
# ============================================================

st.set_page_config(
    page_title="Região - PI Ecoponto",
    page_icon="🔍",
    layout="wide"
)

renderizar_estilos_globais()


# ============================================================
# TÍTULO
# ============================================================

st.write("🔍 Busca por Região")


# ============================================================
# SELEÇÃO DA REGIÃO
# ============================================================

zona_selecionada = st.selectbox(
    "Selecione uma região para ver todos os ecopontos disponíveis.",
    [
        "Selecione...",
        "Zona Leste",
        "Zona Oeste",
        "Zona Norte",
        "Zona Sul",
        "Centro"
    ],
    key="filtro_zona_regiao"
)


# ============================================================
# BUSCA NO MONGODB
# ============================================================

if zona_selecionada != "Selecione...":

    with st.spinner("Buscando ecopontos da região..."):
        resultados_regiao = buscar_ecopontos_por_zona(
            zona_selecionada
        )

    if resultados_regiao:

        st.success(
            f"Encontramos {len(resultados_regiao)} "
            f"ponto(s) na {zona_selecionada}:"
        )

        # ====================================================
        # ROLAGEM COM CONTAINER NATIVO + CARDS CUSTOMIZADOS
        # ====================================================

        with st.container(height=380):

            for eco in resultados_regiao:

                nome_ecoponto = eco.get('ecoponto', 'Não informado')
                bairro = eco.get('bairro', 'Não informado')
                endereco = eco.get('endereco', 'Não informado')
                horario = eco.get('horario', 'Não informado')
                materiais = eco.get('materiais_aceitos', 'Não informado')

                # Links de localização
                busca_endereco = f"Ecoponto {nome_ecoponto}, {endereco}"
                endereco_codificado = urllib.parse.quote(busca_endereco)

                link_maps = f"https://www.google.com/maps/search/?api=1&query={endereco_codificado}"
                link_waze = f"https://waze.com/ul?q={endereco_codificado}&navigate=yes"

                # HTML limpo para o Streamlit renderizar sem escapar como texto
                card_html = (
                    f'<div style="background-color: var(--secondary-background-color, rgba(150, 150, 150, 0.08)); '
                    f'padding: 16px; margin-bottom: 12px; border-radius: 8px; border: 1px solid var(--border-color, #31333F33); '
                    f'font-family: sans-serif; color: var(--text-color, inherit);">'
                    f'<h3 style="margin: 0 0 10px 0; color: var(--text-color, inherit); font-size: 20px; font-weight: 600;">'
                    f'📍 Ecoponto {nome_ecoponto}</h3>'
                    f'<p style="margin: 6px 0; font-size: 15px; color: var(--text-color, inherit); line-height: 1.4;">'
                    f'🏙️ <b>Bairro:</b> {bairro}</p>'
                    f'<p style="margin: 6px 0; font-size: 15px; color: var(--text-color, inherit); line-height: 1.4;">'
                    f'🏠 <b>Endereço:</b> {endereco}</p>'
                    f'<p style="margin: 6px 0; font-size: 15px; color: var(--text-color, inherit); line-height: 1.4;">'
                    f'🕒 <b>Funcionamento:</b> {horario}</p>'
                    f'<p style="margin: 6px 0; font-size: 15px; color: var(--text-color, inherit); line-height: 1.4;">'
                    f'🗑️ <b>Materiais Aceitos:</b> {materiais}</p>'
                    f'<div style="display: flex; gap: 12px; width: 100%; margin-top: 12px;">'
                    f'<a href="{link_maps}" target="_blank" style="text-decoration: none; color: black; flex: 1;">'
                    f'<div style="display: flex; align-items: center; justify-content: center; gap: 8px; background-color: white; '
                    f'border: 2px solid red; border-radius: 8px; padding: 8px 12px; font-weight: bold; font-size: 14px; cursor: pointer;">'
                    f'<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Google_Maps_icon_%282020%29.svg/500px-Google_Maps_icon_%282020%29.svg.png?_=20200218211225" width="18" height="18"/>'
                    f'Maps</div></a>'
                    f'<a href="{link_waze}" target="_blank" style="text-decoration: none; color: black; flex: 1;">'
                    f'<div style="display: flex; align-items: center; justify-content: center; gap: 8px; background-color: white; '
                    f'border: 2px solid #2db5e0; border-radius: 10px; padding: 8px 12px; font-weight: bold; font-size: 14px; cursor: pointer;">'
                    f'<img src="https://logo-teka.com/wp-content/uploads/2026/01/waze-icon-logo.svg" width="18" height="18"/>'
                    f'Waze</div></a>'
                    f'</div></div>'
                )

                st.markdown(card_html, unsafe_allow_html=True)

    else:

        st.warning(
            f"Nenhum ecoponto ativo encontrado "
            f"para a {zona_selecionada}."
        )


# ============================================================
# COMPONENTES GLOBAIS
# ============================================================

renderizar_chat_flutuante()
renderizar_rodape()