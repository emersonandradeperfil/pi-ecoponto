import os
import re

import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente do processo.
# Precisa vir ANTES de qualquer os.getenv("MONGO_URI").
load_dotenv()


# ============================================================
# [BANCO DE DADOS] CONEXÃO COM MONGODB ATLAS
# ============================================================


@st.cache_resource
def obter_cliente_mongodb():
    """
    Cria e mantém uma conexão reutilizável com o MongoDB Atlas.
    O @st.cache_resource evita abrir uma nova conexão a cada
    interação do usuário no Streamlit.
    """

    # Primeiro tenta pegar dos Secrets do Streamlit
    try:
        MONGO_URI = st.secrets["MONGO_URI"]
    except Exception:
        # Fallback para variável de ambiente
        MONGO_URI = os.getenv("MONGO_URI")

    if not MONGO_URI:
        raise ValueError(
            "MONGO_URI não foi configurada. "
            "Configure a variável MONGO_URI nos Secrets do Streamlit "
            "ou no ambiente local."
        )

    cliente = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Testa a conexão
    cliente.admin.command("ping")

    return cliente


def obter_colecao():
    """
    Retorna a coleção de ecopontos.
    """

    cliente = obter_cliente_mongodb()

    banco = cliente["pi_ecoponto"]

    colecao = banco["ecopontos"]

    return colecao


# ============================================================
# [UTILITÁRIO] CONVERTE DOCUMENTO MONGODB PARA DICIONÁRIO
# ============================================================

def limpar_documento(documento):
    """
    Remove o campo _id do MongoDB para que os dados retornados
    tenham o mesmo formato que o código antigo esperava.
    """

    if documento:
        documento.pop("_id", None)

    return documento


# ============================================================
# [CONSULTAS] BAIRROS
# ============================================================

@st.cache_data(ttl=600)
def carregar_bairros_do_banco():

    try:
        colecao = obter_colecao()

        bairros = colecao.distinct(
            "bairro",
            {
                "ativo": True
            }
        )

        bairros = [
            bairro
            for bairro in bairros
            if bairro
        ]

        return sorted(bairros)

    except Exception as err:
        st.error(
            f"Erro ao consultar os bairros no MongoDB Atlas: {err}"
        )

        return []


# ============================================================
# [CONSULTAS] UNIDADES
# ============================================================

@st.cache_data(ttl=600)
def carregar_unidades_do_banco():

    try:
        colecao = obter_colecao()

        unidades = colecao.distinct(
            "ecoponto",
            {
                "ativo": True
            }
        )

        unidades = [
            unidade
            for unidade in unidades
            if unidade
        ]

        return sorted(unidades)

    except Exception as err:
        st.error(
            f"Erro ao consultar as unidades no MongoDB Atlas: {err}"
        )

        return []


# ============================================================
# [CONSULTA] BUSCA POR UNIDADE
# ============================================================

def buscar_por_unidade_direta(nome_unidade):

    try:
        colecao = obter_colecao()

        resultados = colecao.find(
            {
                "ecoponto": nome_unidade,
                "ativo": True
            },
            {
                "_id": 0,
                "ecoponto": 1,
                "endereco": 1,
                "horario": 1,
                "zona": 1,
                "bairro": 1,
                "materiais_aceitos": 1
            }
        )

        return list(resultados)

    except Exception as err:
        st.error(
            f"Erro ao buscar a unidade no MongoDB Atlas: {err}"
        )

        return []


# ============================================================
# [CONSULTA] BUSCA POR ZONA
# ============================================================

def buscar_ecopontos_por_zona(zona_filtro):

    try:
        colecao = obter_colecao()

        resultados = colecao.find(
            {
                "zona": zona_filtro,
                "ativo": True
            },
            {
                "_id": 0,
                "ecoponto": 1,
                "endereco": 1,
                "horario": 1,
                "zona": 1,
                "bairro": 1,
                "materiais_aceitos": 1
            }
        ).sort(
            "ecoponto",
            1
        )

        return list(resultados)

    except Exception as err:
        st.error(
            f"Erro ao buscar os ecopontos por região: {err}"
        )

        return []


# ============================================================
# [CONSULTA] BUSCA POR TEXTO LIVRE
# ============================================================

def buscar_por_texto_livre(termo_busca):
    """
    Usado pelo chatbot.

    Busca pelo nome do ecoponto OU pelo bairro,
    mantendo o mesmo comportamento do banco antigo.
    """

    try:
        colecao = obter_colecao()

        # Evita que caracteres especiais do usuário
        # sejam interpretados de forma indesejada pelo regex.
        termo_seguro = re.escape(termo_busca)

        resultados = colecao.find(
            {
                "ativo": True,
                "$or": [
                    {
                        "ecoponto": {
                            "$regex": termo_seguro,
                            "$options": "i"
                        }
                    },
                    {
                        "bairro": {
                            "$regex": termo_seguro,
                            "$options": "i"
                        }
                    }
                ]
            },
            {
                "_id": 0,
                "ecoponto": 1,
                "endereco": 1,
                "horario": 1,
                "zona": 1,
                "bairro": 1,
                "materiais_aceitos": 1
            }
        ).sort(
            "ecoponto",
            1
        )

        return list(resultados)

    except Exception as err:
        st.error(
            f"Erro na busca por texto no MongoDB Atlas: {err}"
        )

        return []