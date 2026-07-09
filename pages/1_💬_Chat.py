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
# O botão fica sobreposto (position: absolute) dentro do próprio campo de texto,
# encostado na borda direita — por isso o input ganha um padding-right extra,
# pra o texto digitado não passar por baixo do botão.
st.markdown("""
<style>
[data-testid="InputInstructions"] {
    display: none !important;
}

/* Bloco que contém o input e o botão vira uma linha (flex), lado a lado,
   sem espaço entre eles — assim dá pra "colar" as bordas dos dois e criar
   a sensação de uma peça só, com o botão na ponta direita do campo.
   Usamos [data-testid^="stVerticalBlock"] (com ^, "começa com") pra
   funcionar mesmo se o Streamlit mudar/adicionar sufixos no testid. */
div[data-testid="stForm"] div[data-testid^="stVerticalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: stretch !important;
    gap: 0 !important;
}

/* 1º item da linha = bloco do input → ocupa todo o espaço que sobrar */
div[data-testid="stForm"] div[data-testid^="stVerticalBlock"] > div:first-child {
    flex: 1 1 auto !important;
    min-width: 0 !important;
}

/* 2º item da linha = bloco do botão → largura fixa */
div[data-testid="stForm"] div[data-testid^="stVerticalBlock"] > div:last-child {
    flex: 0 0 56px !important;
    display: flex !important;
}

/* Campo de texto: arredondado só do lado esquerdo, sem borda no lado
   que encosta no botão, pra parecer uma peça só */
div[data-testid="stForm"] input[type="text"] {
    height: 44px !important;
    border-radius: 8px 0 0 8px !important;
    border-right: none !important;
}

/* Botão preenche 100% da altura/largura do seu bloco e arredonda só
   do lado direito */
div[data-testid="stForm"] div[data-testid="stFormSubmitButton"] {
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stForm"] button[kind="formSubmit"] {
    width: 100% !important;
    height: 44px !important;
    border-radius: 0 8px 8px 0 !important;
    background-color: #2e7d32 !important;
    color: white !important;
    border: none !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
div[data-testid="stForm"] button[kind="formSubmit"]:hover {
    background-color: #1b5e20 !important;
}
</style>
""", unsafe_allow_html=True)

with st.form(key="chat_form_inline", clear_on_submit=True):
    prompt_usuario = st.text_input(
        label="Digite sua mensagem",
        placeholder="Digite aqui o que quer descartar e sua região...",
        label_visibility="collapsed"
    )
    botao_enviar = st.form_submit_button(label="➤", use_container_width=True)

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