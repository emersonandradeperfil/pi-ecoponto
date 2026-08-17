import urllib.parse

import streamlit as st

from components.layout import (
    renderizar_estilos_globais,
    renderizar_chat_flutuante,
    renderizar_rodape
)

from database.conexao import (
    carregar_unidades_do_banco,
    buscar_por_unidade_direta
)


# ============================================================
# [SESSÃO] BUSCA POR UNIDADE
# ============================================================

st.set_page_config(
    page_title="Unidade - PI Ecoponto",
    page_icon="🏢",
    layout="wide"
)

renderizar_estilos_globais()


# ============================================================
# TÍTULO
# ============================================================

st.write("🏢 Busca por Unidade")


# ============================================================
# CARREGA UNIDADES DO MONGODB
# ============================================================

lista_unidades = carregar_unidades_do_banco()


unidade_selecionada = st.selectbox(
    "Selecione uma unidade do ecoponto para ver seus detalhes.",
    ["Selecione..."] + lista_unidades,
    key="filtro_unidade_direta"
)


# ============================================================
# BUSCA UNIDADE SELECIONADA
# ============================================================

if unidade_selecionada != "Selecione...":

    with st.spinner("Carregando dados da unidade..."):

        resultados_unidade = buscar_por_unidade_direta(
            unidade_selecionada
        )


    if resultados_unidade:

        eco_u = resultados_unidade[0]


        # ====================================================
        # LINKS DE NAVEGAÇÃO
        # ====================================================

        busca_endereco = (
            f"Ecoponto {eco_u['ecoponto']}, "
            f"{eco_u['endereco']}"
        )

        endereco_codificado = urllib.parse.quote(
            busca_endereco
        )


        link_maps = (
            "https://www.google.com/maps/search/"
            f"?api=1&query={endereco_codificado}"
        )

        link_waze = (
            "https://waze.com/ul"
            f"?q={endereco_codificado}&navigate=yes"
        )


        # ====================================================
        # CARD DO ECOPONTO
        # ====================================================

        with st.container(border=True):

            st.markdown(
                f"### 📍 Ecoponto {eco_u['ecoponto']}"
            )

            st.write(
                f"🏙️ **Bairro:** "
                f"{eco_u.get('bairro', 'Não informado')} "
                f"- {eco_u.get('zona', 'Não informado')}"
            )

            st.write(
                f"🏠 **Endereço:** "
                f"{eco_u.get('endereco', 'Não informado')}"
            )

            st.write(
                f"🕒 **Funcionamento:** "
                f"{eco_u.get('horario', 'Não informado')}"
            )

            st.write(
                f"🗑️ **Materiais Aceitos:** "
                f"{eco_u.get('materiais_aceitos', 'Não informado')}"
            )


            # =================================================
            # BOTÕES
            # =================================================

            col1, col2 = st.columns(2)


            with col1:

                st.markdown(
                    f'<a href="{link_maps}" target="_blank" style="text-decoration: none; color: black;">'
                    f'<div style="display: flex; align-items: center; justify-content: center; '
                    f'background-color: #e6e6e6; border: 2px solid red; border-radius: 8px; '
                    f'padding: 8px 16px; font-weight: bold; cursor: pointer;">'
                    f'<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Google_Maps_icon_%282020%29.svg/500px-Google_Maps_icon_%282020%29.svg.png?_=20200218211225" width="20" height="20" style="margin-right:8px;"/>'
                    f'Maps'
                    f'</div>'
                    f'</a>',
                    unsafe_allow_html=True
                )


            with col2:

                st.markdown(
                    f'<a href="{link_waze}" target="_blank" style="text-decoration: none; color: black;">'
                    f'<div style="display: flex; align-items: center; justify-content: center; '
                    f'background-color: #e6e6e6; border: 2px solid #2db5e0; border-radius: 10px; '
                    f'padding: 8px 16px; font-weight: bold; cursor: pointer;">'
                    f'<img src="https://logo-teka.com/wp-content/uploads/2026/01/waze-icon-logo.svg" width="20" height="20" style="margin-right:8px;"/>'
                    f'Waze'
                    f'</div>'
                    f'</a>',
                    unsafe_allow_html=True
                )


# ============================================================
# COMPONENTES GLOBAIS
# ============================================================

renderizar_chat_flutuante()
renderizar_rodape()