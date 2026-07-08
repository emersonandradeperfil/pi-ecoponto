import streamlit as st

from components.layout import renderizar_estilos_globais, renderizar_chat_flutuante, renderizar_rodape
from database.conexao import buscar_ecopontos_por_zona

# ============================================================
#  [SESSÃO] BUSCA POR REGIÃO (ZONA GEOGRÁFICA)
# ============================================================

st.set_page_config(page_title="Região - PI Ecoponto", page_icon="🔍", layout="wide")
renderizar_estilos_globais()

# st.title("🔍 Região")
# st.write("Selecione uma região para ver todos os ecopontos disponíveis.")
# st.markdown("---")

zona_selecionada = st.selectbox(
    "Selecione uma região para ver todos os ecopontos disponíveis.",
    ["Selecione...", "Zona Leste", "Zona Oeste", "Zona Norte", "Zona Sul", "Centro"],
    key="filtro_zona_regiao"
)

# Caso uma região seja selecionada, renderiza os ecopontos em formato de "cards HTML" customizados
if zona_selecionada != "Selecione...":
    with st.spinner("Buscando ecopontos da região..."):
        resultados_regiao = buscar_ecopontos_por_zona(zona_selecionada)

    if resultados_regiao:
        st.success(f"Encontramos {len(resultados_regiao)} ponto(s) na {zona_selecionada}:")

        # Elemento container HTML com scroll fixado em max-height: 350px
        html_cards = """
        <div style="max-height: 350px; overflow-y: auto; padding: 15px; padding-bottom: 25px; padding-right: 10px; border: 1px solid #262730; border-bottom: 4px solid #2e7d32; background-color: #1e2229;">
        """

        # Loop para injetar cada ecoponto retornado do banco de dados na estrutura visual estilizada
        for eco in resultados_regiao:
            html_cards += f"""
            <div style="background-color: #111418; padding: 16px; margin-bottom: 12px; border-radius: 8px; border: 1px solid #262730; font-family: sans-serif;">
                <h3 style="margin: 0 0 10px 0; color: white; font-size: 20px; font-weight: 600;">📍 Ecoponto {eco['ecoponto']}</h3>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🏙️ <b>Bairro:</b> {eco.get('bairro', 'Não informado')}</p>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🏠 <b>Endereço:</b> {eco['endereco']}</p>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🕒 <b>Funcionamento:</b> {eco['horario']}</p>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🗑️ <b>Materiais Aceitos:</b> {eco['materiais_aceitos']}</p>
            </div>
            """
        html_cards += '</div>'
        # Renderização do componente HTML customizado no painel do Streamlit
        st.components.v1.html(html_cards, height=370, scrolling=False)
    else:
        st.warning(f"Nenhum ecoponto ativo encontrado para a {zona_selecionada}.")

renderizar_chat_flutuante()
renderizar_rodape()
