import streamlit as st

from components.layout import renderizar_estilos_globais, renderizar_chat_flutuante, renderizar_rodape
from database.conexao import carregar_unidades_do_banco, buscar_por_unidade_direta

# ============================================================
#  [SESSÃO] BUSCA POR UNIDADE (SELEÇÃO DIRETA)
# ============================================================

st.set_page_config(page_title="Unidade - PI Ecoponto", page_icon="🏢", layout="wide")
renderizar_estilos_globais()

st.title("🏢 Busca por Unidade")
# st.write("Selecione um ecoponto para ver seus detalhes.")
# st.markdown("---")

lista_unidades = carregar_unidades_do_banco()

unidade_selecionada = st.selectbox(
    "Selecione uma unidade do ecoponto para ver seus detalhes.",
    ["Selecione..."] + lista_unidades,
    key="filtro_unidade_direta"
)

# Caso uma unidade válida seja selecionada, renderiza o container com as informações dela
if unidade_selecionada != "Selecione...":
    with st.spinner("Carregando dados da unidade..."):
        resultados_unidade = buscar_por_unidade_direta(unidade_selecionada)

    if resultados_unidade:
        eco_u = resultados_unidade[0]
        with st.container(border=True):
            st.markdown(f"### 📍 Ecoponto {eco_u['ecoponto']}")
            st.write(f"🏙️ **Bairro:** {eco_u['bairro']} - {eco_u['zona']}")
            st.write(f"🏠 **Endereço:** {eco_u['endereco']}")
            st.write(f"🕒 **Funcionamento:** {eco_u['horario']}")
            st.write(f"🗑️ **Materiais Aceitos:** {eco_u['materiais_aceitos']}")

renderizar_chat_flutuante()
renderizar_rodape()
