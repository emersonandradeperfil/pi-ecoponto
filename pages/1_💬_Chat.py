import streamlit as st

from components.layout import renderizar_estilos_globais, renderizar_chat_flutuante, renderizar_rodape
from services.ia_service import chamar_ia_com_fallback, normalizar_zona, PROMPT_SISTEMA_CONSULTOR
from database.conexao import buscar_por_texto_livre, buscar_ecopontos_por_zona

# ============================================================
#  [SESSÃO] ASSISTENTE VIRTUAL (CHATBOT INTEGRADO COM IA)
# ============================================================

st.set_page_config(page_title="Chat - PI Ecoponto", page_icon="💬", layout="wide")
renderizar_estilos_globais()

MENSAGEM_INICIAL = (
    "Olá! Sou o consultor virtual do Ecoponto SP, você sabe o que é um ecoponto ?"
)

JANELA_HISTORICO_IA = 12        # nº máx. de mensagens enviadas à IA por chamada (controle de tokens)

# ------------------------------------------------------------
# Inicialização do estado de sessão
# ------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": MENSAGEM_INICIAL}]
if "dados_coletados" not in st.session_state:
    st.session_state.dados_coletados = {"material": None, "bairro": None, "zona": None}

st.write("💬 Assistente Virtual")

# Cria e gerencia a memória da conversa no estado do Streamlit (session_state)
box_historico = st.container(height=300, border=True)
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
        placeholder="Digite aqui o que quer descartar e sua região...",
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
                    # Envia o histórico (janela recente) para a IA, dando memória de curto prazo.
                    # Exclui a mensagem inicial fixa (índice 0), que é só texto de boas-vindas
                    # e não agrega informação real para a IA.
                    historico_para_ia = st.session_state.messages[1:][-JANELA_HISTORICO_IA:]

                    dados_extraidos = chamar_ia_com_fallback(historico_para_ia, PROMPT_SISTEMA_CONSULTOR)

                    resposta_ia = dados_extraidos.get(
                        "resposta_ao_usuario",
                        "Desculpe, não consegui processar sua mensagem agora. Pode reformular?"
                    )

                    # ── Atualiza os "slots" de dados coletados, sem perder o que já foi dito antes ──
                    if dados_extraidos.get("material"):
                        st.session_state.dados_coletados["material"] = dados_extraidos["material"]
                    if dados_extraidos.get("bairro"):
                        st.session_state.dados_coletados["bairro"] = dados_extraidos["bairro"]
                        st.session_state.dados_coletados["zona"] = None  # bairro tem prioridade sobre zona
                    if dados_extraidos.get("zona") and not st.session_state.dados_coletados["bairro"]:
                        st.session_state.dados_coletados["zona"] = normalizar_zona(dados_extraidos["zona"])

                    material_detectado = st.session_state.dados_coletados["material"]
                    bairro_detectado = st.session_state.dados_coletados["bairro"]
                    zona_detectada = st.session_state.dados_coletados["zona"]

                    pronto_para_buscar = bool(dados_extraidos.get("pronto_para_buscar")) and (
                        bool(material_detectado) and (bool(bairro_detectado) or bool(zona_detectada))
                    )

                    resposta_final = resposta_ia

                    if pronto_para_buscar:
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

                        if ecopontos:
                            resposta_final += (
                                f"<br><br>Encontrei **{len(ecopontos)}** ponto(s) de coleta para "
                                f"**{material_detectado}** em **{label_local}**:<br><br>"
                            )
                            for eco in ecopontos:
                                resposta_final += f"📍 **Ecoponto {eco['ecoponto']}** — {eco['zona']}<br>"
                                resposta_final += f"🏘️ Bairro: {eco.get('bairro', 'Não informado')}<br>"
                                resposta_final += f"🏠 Endereço: {eco['endereco']}<br>"
                                resposta_final += f"🕒 Funcionamento: {eco['horario']}<br>"
                                resposta_final += f"🗑️ Materiais: {eco.get('materiais_aceitos', 'Não informado')}<br><br>"
                        elif label_local:
                            resposta_final += (
                                f"<br><br>Identifiquei **{label_local}**, mas não localizei nenhum "
                                f"ecoponto correspondente no banco de dados."
                            )

                    # Adiciona a resposta da IA no histórico e atualiza a tela
                    st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                    st.rerun()

                except Exception as error_ia:
                    st.error(f"Erro no processamento da Inteligência Artificial: {error_ia}")

renderizar_chat_flutuante()
renderizar_rodape()