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
# Se estiver local, busca no os.environ. Se estiver no Streamlit Cloud, busca no st.secrets.
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

# --- FUNÇÃO PARA CONECTAR AO MARIADB (AWS) ---
def buscar_ecopontos_no_banco(bairro_filtro):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5 # Define timeout para não travar a aplicação se a AWS sumir
        )
        cursor = conn.cursor(dictionary=True)
        
        # Query utilizando a View do seu banco 'ecoponto'
        query = """
            SELECT ecoponto, endereco, horario_seg_sab, zona 
            FROM vw_ecopontos_completo 
            WHERE bairro LIKE %s;
        """
        cursor.execute(query, (f"%{bairro_filtro}%",))
        resultados = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return resultados
    except Exception as err:
        st.error(f"Erro ao conectar com o banco de dados na AWS: {err}")
        return None

# --- CONFIGURAÇÃO DA INTERFACE STREAMLIT ---
st.set_page_config(page_title="EcoChat SP", page_icon="🌱", layout="centered")

st.title("🌱 EcoChat - Inteligência de Ecopontos")
st.write("Diga o que você deseja descartar e o seu bairro em São Paulo para encontrar o ecoponto mais próximo!")

# Inicializa o histórico de mensagens do chat se não existir
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o seu assistente ambiental. Como posso te ajudar hoje? Pode digitar o que quer descartar e a sua região."}
    ]

# Renderiza o histórico de mensagens na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Captura a entrada de texto do usuário na caixa de chat
if prompt_usuario := st.chat_input("Ex: Quero descartar restos de obra e moro na Penha"):
    # Adiciona e mostra a mensagem do usuário na tela
    with st.chat_message("user"):
        st.write(prompt_usuario)
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})

    # Bloco de resposta do assistente
    with st.chat_message("assistant"):
        with st.spinner("Analisando sua solicitação..."):
            
            # 1. Configura a Instrução do Sistema para a LLM (Abordagem A)
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
                temperature=0.1 # Temperatura baixa para manter a IA estrita ao formato
            )
            
            try:
                # Chama o modelo Gemini 1.5 Flash
                response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt_usuario,
                config=config
                )
                
                # Converte o texto JSON retornado pela IA para dicionário Python
                dados_extraidos = json.loads(response.text)
                bairro_detectado = dados_extraidos.get("bairro")
                material_detectado = dados_extraidos.get("material")
                
                # 2. Lógica de consulta ao Banco com base no que a IA entendeu
                if bairro_detectado:
                    # Faz a consulta ao MariaDB na AWS
                    ecopontos = buscar_ecopontos_no_banco(bairro_detectado)
                    
                    if ecopontos:
                        resposta_final = f"Entendi que você quer descartar **{material_detectado or 'seus materiais'}** e está na região de **{bairro_detectado}**.\n\n"
                        resposta_final += "Aqui estão os pontos de coleta que encontrei para você:\n\n"
                        
                        for eco in ecopontos:
                            resposta_final += f"📍 **Ecoponto {eco['ecoponto']}** ({eco['zona']})\n"
                            resposta_final += f"🏠 Endereço: {eco['endereco']}\n"
                            resposta_final += f"🕒 Funcionamento: {eco['horario_seg_sab']}\n\n"
                    else:
                        resposta_final = f"Identifiquei que você está em **{bairro_detectado}**, mas não localizei nenhum ecoponto correspondente nessa região no banco de dados da AWS."
                else:
                    resposta_final = "Consegui entender o que você quer descartar, mas não peguei a informação de qual **bairro** você está. Pode me dizer o seu bairro ou subprefeitura para que eu consulte os dados?"
                
                # Exibe a resposta final na interface e salva no histórico
                st.write(resposta_final)
                st.session_state.messages.append({"role": "assistant", "content": resposta_final})
                
            except Exception as error_ia:
                st.error(f"Erro no processamento da Inteligência Artificial: {error_ia}")