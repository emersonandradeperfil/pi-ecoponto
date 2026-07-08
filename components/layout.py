import streamlit as st

# ============================================================
#  [INTERFACE] ELEMENTOS VISUAIS COMPARTILHADOS ENTRE PÁGINAS
# ============================================================


def renderizar_estilos_globais():
    """CSS aplicado em todas as páginas (ajustes finos de espaçamento)."""
    st.markdown("""
        <style>
            /* Remove vão extra no rodapé da página */
            .stMainBlockContainer {
                padding-bottom: 2rem !important;
            }
            /* Alinha botão Enviar verticalmente com o input */
            div[data-testid="column"]:last-child .stFormSubmitButton button {
                margin-top: 0px;
                height: 38px;
            }

        </style>
    """, unsafe_allow_html=True)


def renderizar_chat_flutuante():
    """Botão + iframe flutuante do EcoChat (canto inferior direito)."""
    # URL_DO_CHAT = "https://pi-ecoponto.streamlit.app/?embed=true"
    url_do_chat = "http://localhost:5500/?embed=true"

    codigo_html_chat = f"""
    <div id="chat-circle" onclick="toggleChat()">
        <span>💬 EcoChat</span>
    </div>
    <div class="chat-box" id="chat-box" style="display: none;">
        <div class="chat-box-header">
            🌱 EcoChat SP - Assistente
            <span class="chat-box-toggle" onclick="toggleChat()">X</span>
        </div>
        <div class="chat-box-body">
            <iframe src="{url_do_chat}" width="100%" height="100%" style="border:none;"></iframe>
        </div>
    </div>
    <style>
    #chat-circle {{ position: fixed; bottom: 30px; right: 30px; background: #2e7d32; color: white; padding: 15px 25px; border-radius: 50px; cursor: pointer; box-shadow: 0px 4px 15px rgba(0,0,0,0.3); z-index: 999999; font-family: 'Source Sans Pro', sans-serif; font-weight: bold; transition: all 0.3s ease; }}
    #chat-circle:hover {{ background: #1b5e20; transform: scale(1.05); }}
    .chat-box {{ position: fixed; bottom: 100px; right: 30px; width: 420px; height: 550px; background: white; box-shadow: 0px 5px 35px rgba(0,0,0,0.4); border-radius: 12px; overflow: hidden; z-index: 999999; display: flex; flex-direction: column; font-family: 'Source Sans Pro', sans-serif; }}
    .chat-box-header {{ background: #2e7d32; color: white; padding: 15px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }}
    .chat-box-toggle {{ cursor: pointer; padding: 5px 10px; background: rgba(0,0,0,0.2); border-radius: 5px; }}
    .chat-box-body {{ flex-grow: 1; height: 100%; background: #f9f9f9; }}
    </style>
    <script>
    function toggleChat() {{
        var chatBox = document.getElementById("chat-box");
        chatBox.style.display = (chatBox.style.display === "none") ? "block" : "none";
    }}
    </script>
    """
    st.components.v1.html(codigo_html_chat, height=0)


def renderizar_rodape():
    """Rodapé institucional com os créditos do projeto."""
    st.markdown("---")
    texto_rodape = """
    <div style="text-align: center; margin-top: 20px; padding: 10px; font-family: sans-serif;">
        <p style="margin: 0; font-size: 14px; color: #a3a8b4; font-weight: 500;">
            <b>PI | TIA | Senac Lapa Tito</b>
        </p>
        <p style="margin: 5px 0 0 0; font-size: 13px; color: #828794;">
            <b>Integrantes:</b> Emerson, Lucas, Paola, Luiz e Wesley
        </p>
    </div>
    """
    st.markdown(texto_rodape, unsafe_allow_html=True)
