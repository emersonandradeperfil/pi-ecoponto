import streamlit as st
import mysql.connector

from config.ambiente import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

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


@st.cache_data(ttl=600)
def carregar_bairros_do_banco():
    query = "SELECT DISTINCT bairro FROM vw_materiais_por_ecoponto WHERE bairro IS NOT NULL ORDER BY bairro;"
    dados = executar_query(query)
    return [linha['bairro'] for linha in dados]


@st.cache_data(ttl=600)
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


def buscar_por_texto_livre(termo_busca):
    """Usado pelo chat: busca por nome do ecoponto OU bairro (LIKE '%termo%')."""
    query = """
        SELECT ecoponto, endereco, horario, zona, bairro, materiais_aceitos
        FROM vw_materiais_por_ecoponto
        WHERE ecoponto LIKE %s OR bairro LIKE %s
    """
    return executar_query(query, (termo_busca, termo_busca))
