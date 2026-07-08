import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from groq import Groq

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
    GROQ_API_KEY = get_secret("GROQ_API_KEY")
    DB_HOST = get_secret("DB_HOST")
    DB_USER = get_secret("DB_USER")
    DB_PASSWORD = get_secret("DB_PASSWORD")
    DB_NAME = get_secret("DB_NAME")
except KeyError as e:
    st.error(f"Erro de configuração: A chave {e} não foi encontrada.")
    st.stop()


@st.cache_resource
def obter_client_gemini():
    """Inicializa (uma única vez, graças ao cache) o cliente do Gemini."""
    return genai.Client(api_key=GEMINI_API_KEY)


@st.cache_resource
def obter_client_groq():
    """Inicializa (uma única vez, graças ao cache) o cliente do Groq (fallback)."""
    return Groq(api_key=GROQ_API_KEY)
