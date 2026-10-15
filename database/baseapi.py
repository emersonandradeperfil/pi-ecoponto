import io
import pandas as pd
import requests
import urllib3

import streamlit as st  # ou use st se importar streamlit
from database.regiao import regiaodistrito

# ============================================================
# FUNÇÃO DE CARREGAMENTO DOS DADOS (usando API 156)
# ============================================================

@st.cache_data(ttl=86400) # 24hr dados salvo no cache
def carregar_dados_analise():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url = "https://dados.prefeitura.sp.gov.br/api/3/action/package_show?id=0aecfa2b-aa3a-40d4-8183-0d4351b7fd0a"
    
    # Adicionando User-Agent para evitar bloqueio da API na máquina local
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        if response.status_code != 200:
            return pd.DataFrame()
        
        dados_json = response.json()
        if not dados_json.get("success") or "result" not in dados_json:
            return pd.DataFrame()
            
        recursos = dados_json["result"].get("resources", [])
    except Exception as e:
        print(f"Erro ao acessar API: {e}")
        return pd.DataFrame()

    lista_dfs = []
    for rec in recursos:
        nome_rec = rec.get("name", "")
        if "Dados do SP156" in nome_rec and ("2026" in nome_rec or "-26" in nome_rec):
            if rec.get("format", "").upper() == "CSV" or rec.get("url", "").endswith(".csv"):
                try:
                    resp = requests.get(rec["url"], headers=headers, verify=False, timeout=30)
                    if resp.status_code == 200:
                        df_temp = None
                        for sep in [",", ";"]:
                            try:
                                df_temp = pd.read_csv(io.BytesIO(resp.content), sep=sep, encoding="latin1", low_memory=False)
                                if df_temp is not None and len(df_temp.columns) > 1: break
                            except: continue
                        
                        if df_temp is None or df_temp.empty: continue

                        df_temp.columns = df_temp.columns.str.strip()
                        df_temp = df_temp.rename(columns={
                            "Data de FinalizaÃ§Ã£o": "Data de Finalização", "Meio de ComunicaÃ§Ã£o": "Meio de Comunicação",
                            "ServiÃ§o": "Serviço", "Ã\x93rgÃ£o": "Órgão", "NÃºmero": "Número"
                        })
                        
                        if "Tema" in df_temp.columns:
                            df_temp = df_temp[df_temp["Tema"].str.contains("Lixo|Limpeza", case=False, na=False)].copy()
                        else: continue
                        
                        df_temp = df_temp.drop(columns=["Latitude", "Longitude"], errors="ignore")
                        
                        if "Órgão" in df_temp.columns:
                            df_temp["Empresa"] = df_temp["Órgão"].astype(str).apply(lambda x: x.split("-")[-1].strip())
                        
                        if "Distrito" in df_temp.columns:
                            df_temp = df_temp.dropna(subset=["Distrito"])
                            df_temp = df_temp[df_temp["Distrito"].str.strip() != ""]
                            df_temp = df_temp[df_temp["Distrito"] != "Prefeitura Regional nao encontrada"]
                            df_temp["Distrito"] = df_temp["Distrito"].str.upper()

                        df_temp["Data de Abertura"] = pd.to_datetime(df_temp["Data de Abertura"], errors="coerce")
                        df_temp["Data de Finalização"] = pd.to_datetime(df_temp["Data de Finalização"], errors="coerce")
                        
                        # Padronizações necessárias para os gráficos (Status_Normalizado e Regiao)
                        if "Status" in df_temp.columns:
                            df_temp["Status_Normalizado"] = df_temp["Status"]
                        
                        # Mapeamento provisório de região caso queira garantir
                        de_para_regiao = regiaodistrito()
                        if "Distrito" in df_temp.columns:
                            df_temp["Regiao"] = df_temp["Distrito"].map(de_para_regiao).fillna("OUTRAS")

                        lista_dfs.append(df_temp)
                except Exception as ex:
                    continue

    if lista_dfs:
        df = pd.concat(lista_dfs, ignore_index=True)
        df = df.loc[:, ~df.columns.duplicated()]
        return df

    return pd.DataFrame()

# ============================================================
# FUNÇÃO DE CARREGAMENTO DOS DADOS (usando CSV local já tratado)
# ============================================================
# @st.cache_data
# def carregar_dados_analise():
    # caminho_arquivo = "base/dados_locais.csv"
    # df = pd.read_csv(caminho_arquivo, encoding="utf-8")
    
    # # Converte as colunas de data para o formato datetime do Pandas
    # if "Data de Abertura" in df.columns:
    #     df["Data de Abertura"] = pd.to_datetime(df["Data de Abertura"], errors="coerce")
    # if "Data de Finalização" in df.columns:
    #     df["Data de Finalização"] = pd.to_datetime(df["Data de Finalização"], errors="coerce")
        
    # return df

# ============================================================
# FUNÇÃO DE CARREGAMENTO DOS DADOS (usando csv local e tratando)
# ============================================================
# @st.cache_data
# def carregar_dados_analise():
    # """
    # Carrega o arquivo CSV com suporte a encodings diferentes, trata as datas
    # em português e calcula a quantidade de dias de atendimento por chamado.
    # """
    # # 1. Pega o diretório atual onde está o conexao.py (pasta 'database')
    # diretorio_atual = os.path.dirname(__file__) 

    # # 2. Sobe um nível com '..' para voltar à raiz, depois entra na pasta 'base'
    # caminho_csv = os.path.join(diretorio_atual, "..", "base", "base_pi_1sem26.csv")

    # colunas_base = [
    #     "Data_Abertura", "Data_Atendimento", "Canal", "Assunto", "Servico",
    #     "Especificacao", "Situacao", "Orgao", "Logradouro", "Numero", "CEP",
    #     "Subprefeitura", "Distrito", "Empresa", "Regiao", "Prazo_SLA"
    # ]

    # try:
    #     df = pd.read_csv(
    #         caminho_csv,
    #         names=colunas_base,
    #         header=0,
    #         on_bad_lines="skip",
    #         encoding="utf-8",
    #         engine="python"
    #     )
    # except Exception:
    #     df = pd.read_csv(
    #         caminho_csv,
    #         names=colunas_base,
    #         header=0,
    #         sep=";",
    #         on_bad_lines="skip",
    #         encoding="latin1",
    #         engine="python"
    #     )

    # # Dicionário para conversão dos meses abreviados do português
    # meses_pt = {
    #     "jan.": "Jan", "fev.": "Feb", "mar.": "Mar", "abr.": "Apr",
    #     "mai.": "May", "jun.": "Jun", "jul.": "Jul", "ago.": "Aug",
    #     "set.": "Sep", "out.": "Oct", "nov.": "Nov", "dez.": "Dec"
    # }

    # for mes_pt, mes_en in meses_pt.items():
    #     df["Data_Abertura"] = df["Data_Abertura"].astype(str).str.replace(mes_pt, mes_en)
    #     df["Data_Atendimento"] = df["Data_Atendimento"].astype(str).str.replace(mes_pt, mes_en)

    # df["dt_abertura"] = pd.to_datetime(df["Data_Abertura"], format="%d/%b/%y", errors="coerce")
    # df["dt_atendimento"] = pd.to_datetime(df["Data_Atendimento"], format="%d/%b/%y", errors="coerce")

    # # Dias de atendimento em relação à data atual (se aberto) ou data de encerramento
    # dt_fim = df["dt_atendimento"].fillna(pd.Timestamp.now())
    # df["Dias_Atendimento"] = (dt_fim - df["dt_abertura"]).dt.days

    # df["Status_Normalizado"] = df["Situacao"].astype(str).str.strip()

    # return df
