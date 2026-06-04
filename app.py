import streamlit as st
import os
import json
import mysql.connector
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Carrega o arquivo .env se estiver rodando localmente no VS Code
load_dotenv()

# --- COMPATIBILIDADE DE CREDENCIAIS (LOCAL VS NUVEM) ---
def get_secret(key):
    if key in os.environ:
        return os.environ[key]
    return st.secrets[key]

# Inicializa as credenciais de forma segura
try:
    GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
    DB_HOST = get_secret("DB_HOST")
    DB_USER = get_secret("DB_USER")
    DB_PASSWORD = get_secret("DB_PASSWORD")
    DB_NAME = get_secret("DB_NAME")
except KeyError as e:
    st.error(f"Erro de configuração: A chave {e} não foi encontrada no ambiente ou nos Secrets.")
    st.stop()

# Inicializa o cliente oficial do Gemini
client = genai.Client(api_key=GEMINI_API_KEY)


# --- FUNÇÕES DE BANCO DE DADOS (MARIADB AWS) ---

def executar_query(query, params=None):
    """Executa de forma genérica consultas no banco de dados da AWS."""
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
    """Busca os bairros cadastrados para alimentar o seletor do portal."""
    query = "SELECT DISTINCT bairro FROM vw_materiais_por_ecoponto WHERE bairro IS NOT NULL ORDER BY bairro;"
    dados = executar_query(query)
    return [linha['bairro'] for linha in dados]

def carregar_unidades_do_banco():
    """Busca o nome de todas as unidades de ecopontos para o filtro direto."""
    query = "SELECT DISTINCT ecoponto FROM vw_materiais_por_ecoponto ORDER BY ecoponto;"
    dados =executar_query(query)
    return [linha['ecoponto'] for linha in dados]

def buscar_por_unidade_direta(nome_unidade):
    """Busca as informações de uma única unidade específica."""
    query = """
        SELECT ecoponto, endereco, horario, zona, bairro, materiais_aceitos
        FROM vw_materiais_por_ecoponto
        WHERE ecoponto = %s
    """
    return executar_query(query, (nome_unidade,))

def buscar_ecopontos_por_zona(zona_filtro):
    """Busca os ecopontos pertencentes a uma determinada zona geográfica."""
    query = """
        SELECT ecoponto, endereco, horario, zona, bairro, materiais_aceitos
        FROM vw_materiais_por_ecoponto
        WHERE zona = %s
    """
    return executar_query(query, (zona_filtro,))


# --- CONFIGURAÇÃO DO PORTAL (STREAMLIT INTERFACE) ---

st.set_page_config(page_title="EcoChat SP - Portal", page_icon="🌱", layout="wide")

st.title("🌱 Portal de Ecopontos - São Paulo")
st.write("Interaja com o assistente inteligente ou utilize os filtros independentes abaixo.")
st.markdown("---")

# Carrega os dados iniciais do banco
lista_bairros = carregar_bairros_do_banco()
lista_unidades = carregar_unidades_do_banco()


# ============================================================
#  1. TOPO: ASSISTENTE VIRTUAL (CHATBOT)
# ============================================================
st.subheader("💬 Assistente Virtual")

# Inicializa o histórico do chat se não existir
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o seu assistente ambiental. Como posso te ajudar hoje? Pode digitar o que quer descartar e a sua região."}
    ]

# Container com altura fixa para o histórico do chat não esticar a tela inteira
box_historico = st.container(height=300, border=True)
with box_historico:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)

# Entrada de texto do chat do usuário
if prompt_usuario := st.chat_input("Ex: Quero descartar restos de obra e moro na Penha"):
    with box_historico:
        with st.chat_message("user"):
            st.markdown(prompt_usuario)
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})

    with box_historico:
        with st.chat_message("assistant"):
            with st.spinner("Analisando sua solicitação..."):
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
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt_usuario,
                        config=config
                    )
                    
                    dados_extraidos = json.loads(response.text)
                    bairro_detectado = dados_extraidos.get("bairro")
                    material_detectado = dados_extraidos.get("material")
                    
                    # Para a query do chat, buscamos ecopontos pelo bairro detectado pela IA
                    if bairro_detectado:
                        # Reutiliza uma query simples de correspondência por bairro
                        query_chat = "SELECT ecoponto, endereco, horario, zona, materiais_aceitos FROM vw_materiais_por_ecoponto WHERE bairro = %s"
                        ecopontos = executar_query(query_chat, (bairro_detectado,))
                        
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
                    
                    st.markdown(resposta_final, unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                    st.rerun()
                    
                except Exception as error_ia:
                    st.error(f"Erro no processamento da Inteligência Artificial: {error_ia}")

st.markdown("---")


# ============================================================
#  2. MEIO: BUSCA POR UNIDADE (BAIRRO DIRETO)
# ============================================================
st.subheader("🏢 Busca por Unidade")

unidade_selecionada = st.selectbox(
    "Selecione a Unidade ou Unidade do Bairro:", 
    ["Selecione..."] + lista_unidades,
    key="filtro_unidade_direta" # Garante independência de estado
)

# Renderiza o resultado imediatamente abaixo do seletor de unidade
if unidade_selecionada != "Selecione...":
    with st.spinner("Carregando dados da unidade..."):
        resultados_unidade = buscar_por_unidade_direta(unidade_selecionada)
        
    if resultados_unidade:
        eco_u = resultados_unidade[0]
        with st.container(border=True):
            st.markdown(f"### 📍 Ecoponto {eco_u['ecoponto']} ({eco_u['zona']})")
            st.write(f"🏠 **Endereço:** {eco_u['endereco']}")
            st.write(f"🕒 **Funcionamento:** {eco_u['horario']}")
            st.info(f"🗑️ **Materiais Aceitos:** {eco_u['materiais_aceitos']}")

st.markdown("---")


# ============================================================
#  3. BASE: BUSCA POR REGIÃO (ZONA GEOGRÁFICA)
# ============================================================
st.subheader("🔍 Busca por Região")

zona_selecionada = st.selectbox(
    "Selecione a Região (Zona):", 
    ["Selecione...", "Zona Leste", "Zona Oeste", "Zona Norte", "Zona Sul", "Centro"],
    key="filtro_zona_regiao" # Garante independência de estado
)

# Renderiza o resultado compacto com scroll imediatamente abaixo do seletor de zona
if zona_selecionada != "Selecione...":
    with st.spinner("Buscando ecopontos da região..."):
        resultados_regiao = buscar_ecopontos_por_zona(zona_selecionada)
        
    if resultados_regiao:
        st.success(f"Encontramos {len(resultados_regiao)} ponto(s) na {zona_selecionada}:")
        
        # Container HTML com rolagem (scroll) para economizar espaço em tela
        html_cards = '<div style="max-height: 350px; overflow-y: auto; padding-right: 10px; border: 1px solid #e6e6e6; border-radius: 8px; padding: 15px; background-color: #1e2229;">'
        
        for eco in resultados_regiao:
            html_cards += f"""
            <div style="background-color: #111418; border: 1px solid white; padding: 12px; margin-bottom: 12px; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <h4 style="margin: 0 0 5px 0; color: white;">📍 Ecoponto {eco['ecoponto']}</h4>
                <p style="margin: 3px 0; font-size: 14px; color: white;">🏠 <b>Endereço:</b> {eco['endereco']}</p>
                <p style="margin: 3px 0; font-size: 14px; color: white;">🕒 <b>Funcionamento:</b> {eco['horario']}</p>
                <p style="margin: 3px 0; font-size: 14px; color: white;">🗑️ <b>Aceita:</b> {eco['materiais_aceitos']}</p>
            </div>
            """
        html_cards += '</div>'
        st.components.v1.html(html_cards, height=370, scrolling=False)
    else:
        st.warning(f"Nenhum ecoponto ativo encontrado para a {zona_selecionada}.")


# ============================================================
#  4. CHAT FLUTUANTE (MANTIDO CONFORME REQUISITOS ANTERIORES)
# ============================================================
URL_DO_CHAT = "http://localhost:8501/?embed=true"

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
st.components.v1.html(codigo_html_chat, height=0)