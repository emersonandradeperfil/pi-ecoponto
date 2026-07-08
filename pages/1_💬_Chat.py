import streamlit as st

from components.layout import renderizar_estilos_globais, renderizar_chat_flutuante, renderizar_rodape
from services.ia_service import chamar_ia_com_fallback, normalizar_zona, PROMPT_SISTEMA_EXTRACAO
from database.conexao import buscar_por_texto_livre, buscar_ecopontos_por_zona

# ============================================================
#  [SESSÃO] ASSISTENTE VIRTUAL (CHATBOT INTEGRADO COM IA)
# ============================================================

st.set_page_config(page_title="Chat - PI Ecoponto", page_icon="💬", layout="wide")
renderizar_estilos_globais()

st.title("💬 Assistente Virtual")
st.write("Digite o que você quer descartar e onde você mora (bairro ou zona).")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o seu assistente ambiental. Como posso te ajudar hoje? Pode digitar o que quer descartar e a sua região."}
    ]

# Cria e gerencia a memória da conversa no estado do Streamlit (session_state)
box_historico = st.container(height=400, border=True)
with box_historico:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

# CSS específico do formulário de chat inline (esconde hint, estiliza input+botão)
st.markdown("""
<style>
[data-testid="InputInstructions"] {
    display: none !important;
}
div[data-testid="stForm"] > div[data-testid="stVerticalBlock"] {
    gap: 0.4rem !important;
}
div[data-testid="stForm"] input[type="text"] {
    padding-right: 1rem !important;
    border-radius: 8px 8px 0 0 !important;
    border-bottom: none !important;
}
div[data-testid="stForm"] button[kind="formSubmit"] {
    width: 100% !important;
    border-radius: 0 0 8px 8px !important;
    background-color: #2e7d32 !important;
    color: white !important;
    border: none !important;
    padding: 0.45rem 1rem !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
div[data-testid="stForm"] button[kind="formSubmit"]:hover {
    background-color: #1b5e20 !important;
}
div[data-testid="stFormSubmitButton"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)

with st.form(key="chat_form_inline", clear_on_submit=True):
    prompt_usuario = st.text_input(
        label="Digite sua mensagem",
        placeholder="Ex: Quero descartar restos de obra e moro na Penha",
        label_visibility="collapsed"
    )
    botao_enviar = st.form_submit_button(label="✉️  Enviar mensagem", use_container_width=True)

# Lógica de processamento quando o usuário envia uma nova mensagem
if botao_enviar and prompt_usuario:
    # 1. Adiciona imediatamente a mensagem do usuário na tela e no histórico
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    with box_historico:
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

    # 2. Processa a resposta da Inteligência Artificial
    with box_historico:
        with st.chat_message("assistant"):
            with st.spinner("Analisando sua solicitação..."):
                try:
                    # Chama a IA com fallback automático (Gemini → Groq/Llama)
                    dados_extraidos = chamar_ia_com_fallback(prompt_usuario, PROMPT_SISTEMA_EXTRACAO)
                    bairro_detectado = dados_extraidos.get("bairro")
                    zona_detectada = normalizar_zona(dados_extraidos.get("zona"))
                    material_detectado = dados_extraidos.get("material")

                    # ── Tem bairro (com ou sem zona) → busca sempre em nome + bairro ──
                    if bairro_detectado:
                        ecopontos = buscar_por_texto_livre(f"%{bairro_detectado}%")
                        label_local = bairro_detectado

                    # ── Só zona, sem bairro → traz todos da região ──
                    elif zona_detectada:
                        ecopontos = buscar_ecopontos_por_zona(zona_detectada)
                        label_local = zona_detectada

                    else:
                        ecopontos = []
                        label_local = None

                    # ── Monta a resposta ──
                    if ecopontos:
                        resposta_final = f"Entendi que você quer descartar **{material_detectado or 'seus materiais'}** e está em **{label_local}**.<br><br>"
                        resposta_final += f"Encontrei **{len(ecopontos)}** ponto(s) de coleta para você:<br><br>"
                        for eco in ecopontos:
                            resposta_final += f"📍 **Ecoponto {eco['ecoponto']}** — {eco['zona']}<br>"
                            resposta_final += f"🏘️ Bairro: {eco.get('bairro', 'Não informado')}<br>"
                            resposta_final += f"🏠 Endereço: {eco['endereco']}<br>"
                            resposta_final += f"🕒 Funcionamento: {eco['horario']}<br>"
                            resposta_final += f"🗑️ Materiais: {eco.get('materiais_aceitos', 'Não informado')}<br><br>"
                    elif label_local:
                        resposta_final = f"Identifiquei **{label_local}**, mas não localizei nenhum ecoponto correspondente no banco de dados."
                    else:
                        resposta_final = "Consegui entender o que você quer descartar, mas não captei seu **bairro ou região**. Pode informar onde você mora ou a zona (ex: Zona Leste, ZS)?"

                    # Adiciona a resposta da IA no histórico e atualiza a tela
                    st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                    st.rerun()

                except Exception as error_ia:
                    st.error(f"Erro no processamento da Inteligência Artificial: {error_ia}")

renderizar_chat_flutuante()
renderizar_rodape()
