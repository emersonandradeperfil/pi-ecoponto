import os
import re

import pandas as pd
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env para o ambiente do processo.
# Precisa vir ANTES de qualquer os.getenv("MONGO_URI").
load_dotenv()

# ============================================================
# FUNÇÃO DE CARREGAMENTO DOS DADOS (Movida para o topo)
# ============================================================

@st.cache_data
def carregar_dados_analise():
    """
    Carrega o arquivo CSV com suporte a encodings diferentes, trata as datas
    em português e calcula a quantidade de dias de atendimento por chamado.
    """
    # 1. Pega o diretório atual onde está o conexao.py (pasta 'database')
    diretorio_atual = os.path.dirname(__file__) 

    # 2. Sobe um nível com '..' para voltar à raiz, depois entra na pasta 'base'
    caminho_csv = os.path.join(diretorio_atual, "..", "base", "base_pi_1sem26.csv")

    colunas_base = [
        "Data_Abertura", "Data_Atendimento", "Canal", "Assunto", "Servico",
        "Especificacao", "Situacao", "Orgao", "Logradouro", "Numero", "CEP",
        "Subprefeitura", "Distrito", "Empresa", "Regiao", "Prazo_SLA"
    ]

    try:
        df = pd.read_csv(
            caminho_csv,
            names=colunas_base,
            header=0,
            on_bad_lines="skip",
            encoding="utf-8",
            engine="python"
        )
    except Exception:
        df = pd.read_csv(
            caminho_csv,
            names=colunas_base,
            header=0,
            sep=";",
            on_bad_lines="skip",
            encoding="latin1",
            engine="python"
        )

    # Dicionário para conversão dos meses abreviados do português
    meses_pt = {
        "jan.": "Jan", "fev.": "Feb", "mar.": "Mar", "abr.": "Apr",
        "mai.": "May", "jun.": "Jun", "jul.": "Jul", "ago.": "Aug",
        "set.": "Sep", "out.": "Oct", "nov.": "Nov", "dez.": "Dec"
    }

    for mes_pt, mes_en in meses_pt.items():
        df["Data_Abertura"] = df["Data_Abertura"].astype(str).str.replace(mes_pt, mes_en)
        df["Data_Atendimento"] = df["Data_Atendimento"].astype(str).str.replace(mes_pt, mes_en)

    df["dt_abertura"] = pd.to_datetime(df["Data_Abertura"], format="%d/%b/%y", errors="coerce")
    df["dt_atendimento"] = pd.to_datetime(df["Data_Atendimento"], format="%d/%b/%y", errors="coerce")

    # Dias de atendimento em relação à data atual (se aberto) ou data de encerramento
    dt_fim = df["dt_atendimento"].fillna(pd.Timestamp.now())
    df["Dias_Atendimento"] = (dt_fim - df["dt_abertura"]).dt.days

    df["Status_Normalizado"] = df["Situacao"].astype(str).str.strip()

    return df

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

def buscar_ecopontos_por_zona(zona_filtro, material=None):

    try:
        colecao = obter_colecao()

        filtro = {
            "zona": zona_filtro,
            "ativo": True
        }

        # Se um material foi informado, filtra também pelos
        # materiais aceitos (busca por substring, ignora maiúsc/minúsc).
        if material:
            filtro["materiais_aceitos"] = {
                "$regex": re.escape(material),
                "$options": "i"
            }

        resultados = colecao.find(
            filtro,
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

def buscar_por_texto_livre(termo_busca, material=None):
    """
    Usado pelo chatbot.

    Busca pelo nome do ecoponto OU pelo bairro,
    mantendo o mesmo comportamento do banco antigo.
    Se 'material' for informado, filtra também pelos
    materiais aceitos naquele ecoponto.
    """

    try:
        colecao = obter_colecao()

        # Evita que caracteres especiais do usuário
        # sejam interpretados de forma indesejada pelo regex.
        termo_seguro = re.escape(termo_busca)

        filtro = {
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
        }

        if material:
            filtro["materiais_aceitos"] = {
                "$regex": re.escape(material),
                "$options": "i"
            }

        resultados = colecao.find(
            filtro,
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