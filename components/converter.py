import pandas as pd

# ============================================================
# 1. Localizar a linha real do cabeçalho, de forma automática
# ============================================================
# Em vez de assumir que o cabeçalho está sempre na primeira linha
# (header=0), procuramos a linha que contém "Nome do Ecoponto".
# Isso evita quebrar quando existe um título mesclado acima da
# tabela (comum em planilhas exportadas/formatadas manualmente).

caminho_arquivo = "mongoDB.xlsx"

COLUNA_ANCORA = "Nome do Ecoponto"

try:
    xls = pd.ExcelFile(caminho_arquivo)
    print(f"Abas disponíveis no Excel: {xls.sheet_names}")

    aba_alvo = xls.sheet_names[0]

    # Lê a aba SEM cabeçalho, só pra "espiar" as primeiras linhas
    # e achar em qual linha está o texto "Nome do Ecoponto".
    df_bruto = pd.read_excel(caminho_arquivo, sheet_name=aba_alvo, header=None)

    linha_cabecalho = None
    for indice_linha in range(min(10, len(df_bruto))):
        valores_linha = df_bruto.iloc[indice_linha].astype(str).str.strip()
        if valores_linha.eq(COLUNA_ANCORA).any():
            linha_cabecalho = indice_linha
            break

    if linha_cabecalho is None:
        raise ValueError(
            f'Não encontrei a coluna "{COLUNA_ANCORA}" nas primeiras '
            f'10 linhas da aba "{aba_alvo}". Verifique se o nome da '
            f'coluna no Excel está exatamente assim (confira acentos '
            f'e espaços extras).'
        )

    print(f'Cabeçalho encontrado na linha {linha_cabecalho + 1} do Excel.')

    # Agora lê de verdade, usando a linha certa como cabeçalho
    df = pd.read_excel(caminho_arquivo, sheet_name=aba_alvo, header=linha_cabecalho)

    # Remove espaços em branco escondidos nos nomes das colunas
    df.columns = df.columns.astype(str).str.strip()

    print(f"Colunas encontradas: {df.columns.tolist()}")

except Exception as e:
    print(f"Erro ao carregar o arquivo Excel: {e}")
    df = pd.DataFrame()

if not df.empty:

    # ============================================================
    # 2. Remove linhas que não são ecopontos de verdade
    # ============================================================
    # A planilha tem linhas divisórias tipo "◆ ZONA LESTE" que viram
    # linhas vazias (NaN) na coluna "Nome do Ecoponto" depois de lida.
    # Também removemos linhas totalmente em branco.

    df = df.dropna(subset=["Nome do Ecoponto"])
    df = df[df["Nome do Ecoponto"].astype(str).str.strip() != ""]
    df = df.reset_index(drop=True)

    print(f"Linhas válidas após limpeza: {len(df)}")

    # ============================================================
    # 3. Montar a estrutura final idêntica ao modelo do MongoDB
    # ============================================================
    # Horário é o mesmo para todos os ecopontos, então fica fixo,
    # sem precisar ler colunas de horário do Excel.
    HORARIO_PADRAO = "Seg a Sáb: 24h - Dom e Fer: 24h"

    # Materiais aceitos também fixo, já que a planilha simplificada
    # não distingue mais por ecoponto (sem coluna de Gesso/Entulho/etc.)
    MATERIAIS_PADRAO = "Apenas tecido"

    df_final = pd.DataFrame({
        "ecoponto": "Ecoponto " + df["Nome do Ecoponto"].astype(str),
        "endereco": df["Endereço"].astype(str) + ", " + df["Bairro"].astype(str) + ", São Paulo - SP",
        "bairro": df["Bairro"],
        "zona": df["Zona"],
        "horario": HORARIO_PADRAO,
        "materiais_aceitos": MATERIAIS_PADRAO,
        "ativo": True
    })

    # ============================================================
    # 4. Salvar o resultado em formato CSV para importação manual
    # ============================================================
    nome_saida = "ecopontos_processado.csv"
    df_final.to_csv(nome_saida, index=False, encoding="utf-8")

    print(f"\nSucesso! Arquivo '{nome_saida}' gerado com {len(df_final)} registros prontos para o MongoDB.")