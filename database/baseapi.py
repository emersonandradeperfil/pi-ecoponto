import io
import pandas as pd
import requests
import urllib3

import streamlit as st  # ou use st se importar streamlit
from database.regiao import regiaodistrito

# ============================================================
# FUNÇÃO DE CARREGAMENTO DOS DADOS (usando API 156)
# ============================================================

@st.cache_data(ttl=1800) # 30 minutos dados salvo no cache
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