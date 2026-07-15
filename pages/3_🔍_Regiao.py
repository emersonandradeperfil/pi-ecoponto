import urllib.parse
import streamlit as st

from components.layout import renderizar_estilos_globais, renderizar_chat_flutuante, renderizar_rodape
from database.conexao import buscar_ecopontos_por_zona

# ============================================================
#  [SESSÃO] BUSCA POR REGIÃO (ZONA GEOGRÁFICA)
# ============================================================

st.set_page_config(page_title="Região - PI Ecoponto", page_icon="🔍", layout="wide")
renderizar_estilos_globais()

st.write("🔍 Busca por Região")
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

            busca_endereco = f"Ecoponto {eco['ecoponto']}, {eco['endereco']}"
            endereco_codificado = urllib.parse.quote(busca_endereco)

            link_maps = f"https://www.google.com/maps/search/?api=1&query={endereco_codificado}"
            link_waze = f"https://waze.com/ul?q={endereco_codificado}&navigate=yes"

            html_cards += f"""
            <div style="background-color: #111418; padding: 16px; margin-bottom: 12px; border-radius: 8px; border: 1px solid #262730; font-family: sans-serif;">
                <h3 style="margin: 0 0 10px 0; color: white; font-size: 20px; font-weight: 600;">📍 Ecoponto {eco['ecoponto']}</h3>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🏙️ <b>Bairro:</b> {eco.get('bairro', 'Não informado')}</p>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🏠 <b>Endereço:</b> {eco['endereco']}</p>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🕒 <b>Funcionamento:</b> {eco['horario']}</p>
                <p style="margin: 6px 0; font-size: 15px; color: #e0e0e0; line-height: 1.4;">🗑️ <b>Materiais Aceitos:</b> {eco['materiais_aceitos']}</p>
            
                
        
                <div style="display: flex; gap: 12px; width: 100%;">
                    <a href="{link_maps}" target="_blank" style="text-decoration: none; flex: 1;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; 
                                    background-color: #e6e6e6; border: 2px solid red; border-radius: 8px; 
                                    padding: 8px 12px; color: #333333; font-weight: bold; font-size: 14px; cursor: pointer;">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Google_Maps_icon_%282020%29.svg/500px-Google_Maps_icon_%282020%29.svg.png?_=20200218211225" width="18px" height="18px"/>
                            Maps
                        </div>
                    </a>
            
                    <a href="{link_waze}" target="_blank" style="text-decoration: none; flex: 1;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; 
                                    background-color: #e6e6e6; border: 2px solid #2db5e0; border-radius: 10px; 
                                    padding: 8px 12px; color: #333333; font-weight: bold; font-size: 14px; cursor: pointer;">
                            <img src="https://logo-teka.com/wp-content/uploads/2026/01/waze-icon-logo.svg" width="18px" height="18px"/>
                            Waze
                        </div>
                    </a>
                </div>
            
            </div>
            """
        html_cards += '</div>'
        # Renderização do componente HTML customizado no painel do Streamlit
        st.components.v1.html(html_cards, height=370, scrolling=False)
    else:
        st.warning(f"Nenhum ecoponto ativo encontrado para a {zona_selecionada}.")

renderizar_chat_flutuante()
renderizar_rodape()
