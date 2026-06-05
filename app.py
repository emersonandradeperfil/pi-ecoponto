import streamlit as st
import os
import json
import mysql.connector
from google import genai
from google.genai import types
from dotenv import load_dotenv

# ============================================================
#  [CONFIGURAÇÃO] CARREGAMENTO DE AMBIENTE E SECRETS
# ============================================================
# Carrega as variáveis do arquivo .env caso esteja rodando localmente
load_dotenv()

def get_secret(key):
    if key in os.environ:
        return os.environ[key]
    return st.secrets[key]

# Tenta capturar as credenciais necessárias de forma segura
try:
    GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
    DB_HOST = get_secret("DB_HOST")
    DB_USER = get_secret("DB_USER")
    DB_PASSWORD = get_secret("DB_PASSWORD")
    DB_NAME = get_secret("DB_NAME")
except KeyError as e:
    st.error(f"Erro de configuração: A chave {e} não foi encontrada.")
    st.stop()

# Inicialização do cliente da API do Gemini (Inteligência Artificial)
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
#  [BANCO DE DADOS] FUNÇÕES DE CONSULTA SQL (MARIADB AWS)
# ============================================================
def executar_query(query, params=None):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultados
    except Exception as err:
        st.error(f"Erro ao conectar com o banco de dados na AWS: {err}")
        return []

def carregar_bairros_do_banco():
    query = "SELECT DISTINCT bairro FROM vw_materiais_por_ecoponto WHERE bairro IS NOT NULL ORDER BY bairro;"
    dados = executar_query(query)
    return [linha['bairro'] for linha in dados]

def carregar_unidades_do_banco():
    query = "SELECT DISTINCT ecoponto FROM vw_materiais_por_ecoponto ORDER BY ecoponto;"
    dados = executar_query(query)
    return [linha['ecoponto'] for linha in dados]

def buscar_por_unidade_direta(nome_unidade):
    query = """
        SELECT ecoponto, endereco, horario, zona, bairro, materiais_aceitos
        FROM vw_materiais_por_ecoponto
        WHERE ecoponto = %s
    """
    return executar_query(query, (nome_unidade,))

def buscar_ecopontos_por_zona(zona_filtro):
    query = """
        SELECT ecoponto, endereco, horario, zona, bairro, materiais_aceitos
        FROM vw_materiais_por_ecoponto
        WHERE zona = %s
    """
    return executar_query(query, (zona_filtro,))


# ============================================================
#  [INTERFACE] CONFIGURAÇÃO DA ESTRUTURA VISUAL DA PÁGINA
# ============================================================

st.markdown("""
    <style>
        iframe[title="st.components.v1.html"] {
            margin-bottom: -50px !important;
        }
        .stMainBlockContainer {
            padding-bottom: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)


st.set_page_config(page_title="PI - Ecoponto", page_icon="🌱", layout="wide")

# Cabeçalho Principal do Portal
st.title("🌱 PI sobre Ecopontos de SP")
st.write("Interaja com o assistente inteligente ou utilize os filtros independentes abaixo.")
st.markdown("---")

# Pré-carregamento dos dados vindos do banco de dados para alimentar os filtros da interface
lista_bairros = carregar_bairros_do_banco()
lista_unidades = carregar_unidades_do_banco()

# ============================================================
#  [SEÇÃO 1] ASSISTENTE VIRTUAL (CHATBOT INTEGRADO COM IA)
# ============================================================
st.subheader("💬 Assistente Virtual")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o seu assistente ambiental. Como posso te ajudar hoje? Pode digitar o que quer descartar e a sua região."}
    ]

# Cria e gerencia a memória da conversa no estado do Streamlit (session_state)
box_historico = st.container(height=300, border=True)
with box_historico:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

# Formulário Inline do Chat (Mantém a caixa de texto presa logo abaixo do histórico)
with st.form(key="chat_form_inline", clear_on_submit=True):
    col_input, col_btn = st.columns([0.92, 0.08])
    with col_input:
        prompt_usuario = st.text_input(
            label="Digite sua mensagem",
            placeholder="Ex: Quero descartar restos de obra e moro na Penha",
            label_visibility="collapsed" # Oculta a legenda padrão do input
        )
    with col_btn:
        botao_enviar = st.form_submit_button(label="Enviar", use_container_width=True)

# Lógica de processamento quando o usuário envia uma nova mensagem
if (botao_enviar or prompt_usuario) and prompt_usuario:
    # 1. Desenha a mensagem enviada pelo usuário na tela e salva no histórico
    with box_historico:
        with st.chat_message("user"):
            st.markdown(prompt_usuario)
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})

    # 2. Processa a resposta da Inteligência Artificial
    with box_historico:
        with st.chat_message("assistant"):
            with st.spinner("Analisando sua solicitação..."):

                # Instrução de prompt para o Gemini extrair os dados em formato estruturado (JSON)
                prompt_sistema = """
                Você é um assistente especialista em triagem de descarte de resíduos da cidade de São Paulo.
                Sua única tarefa é ler a mensagem do usuário e extrair estruturadamente:
                1. O MATERIAL ou objeto que ele deseja descartar (ex: entulho, sofá, lâmpada).
                2. O BAIRRO ou Região que ele mencionou estar ou morar.
                
                Você DEVE responder única e exclusivamente com um objeto JSON válido contendo as chaves 'material' e 'bairro'.
                Se você não conseguir identificar uma das informações, preencha o valor correspondente com null.
                Não inclua nenhuma formatação markdown (como ```json) na resposta.
                """
                config = types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    response_mime_type="application/json",
                    temperature=0.1
                )
                
                try:
                    # Chamada oficial à API do Gemini
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_usuario,
                        config=config
                    )
                    
                    # Decodifica o JSON retornado pela IA
                    dados_extraidos = json.loads(response.text)
                    bairro_detectado = dados_extraidos.get("bairro")
                    material_detectado = dados_extraidos.get("material")
                    
                    # Se a IA conseguiu ler um bairro, busca no banco de dados
                    if bairro_detectado:
                        termo_busca = f"%{bairro_detectado}%"
                        query_chat = "SELECT ecoponto, endereco, horario, zona, materiais_aceitos FROM vw_materiais_por_ecoponto WHERE bairro LIKE %s OR ecoponto LIKE %s"
                        ecopontos = executar_query(query_chat, (termo_busca, termo_busca))
                        
                        # Constrói o texto final de resposta com os ecopontos encontrados
                        if ecopontos:
                            resposta_final = f"Entendi que você quer descartar **{material_detectado or 'seus materiais'}** e está na região de **{bairro_detectado}**.<br><br>"
                            resposta_final += "Aqui estão os pontos de coleta que encontrei para você:<br><br>"
                            for eco in ecopontos:
                                resposta_final += f"📍 **Ecoponto {eco['ecoponto']}** ({eco['zona']})<br>"
                                resposta_final += f"🏠 Endereço: {eco['endereco']}<br>"
                                resposta_final += f"🕒 Funcionamento: {eco['horario']}<br>"
                                resposta_final += f"🗑️ Materiais: {eco.get('materiais_aceitos', 'Não informado')}<br><br>"
                        else:
                            resposta_final = f"Identifiquei que você está em **{bairro_detectado}**, mas não localizei nenhum ecoponto correspondente cadastrado no banco da AWS."
                    else:
                        resposta_final = "Consegui entender o que você quer descartar, mas não captei o seu **bairro**. Pode digitar a sua região ou subprefeitura?"

                    # Adiciona a resposta da IA no histórico e atualiza a tela
                    st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                    st.rerun()

                except Exception as error_ia:
                    st.error(f"Erro no processamento da Inteligência Artificial: {error_ia}")

st.markdown("---")

# ============================================================
#  [SEÇÃO 2] FILTRO: BUSCA POR UNIDADE (SELEÇÃO DIRETA)
# ============================================================
st.subheader("🏢 Busca por Unidade")

unidade_selecionada = st.selectbox(
    "Selecione a unidade:", 
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

st.markdown("---")

# ============================================================
#  [SEÇÃO 3] FILTRO: BUSCA POR REGIÃO (ZONA GEOGRÁFICA)
# ============================================================
st.subheader("🔍 Busca por Região")

zona_selecionada = st.selectbox(
    "Selecione a Região:", 
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

# ============================================================
#  [SEÇÃO 4] WIDGET ADICIONAL: CHAT FLUTUANTE (ECOCHAT)
# ============================================================
URL_DO_CHAT = "https://pi-ecoponto.streamlit.app/?embed=true"

# Estrutura HTML/CSS/JS injetada de forma oculta para criar o botão flutuante redondo (Canto inferior direito)
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
        <iframe src="{URL_DO_CHAT}" width="100%" height="100%" style="border:none;"></iframe>
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

# Renderiza o elemento com height=0 para não criar áreas vazias no rodapé
st.components.v1.html(codigo_html_chat, height=0)

# ============================================================
#  [SEÇÃO 5] RODAPÉ INSTITUCIONAL (CRÉDITOS DO PROJETO)
# ============================================================
st.markdown("---")  # Linha divisória discreta antes do rodapé

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