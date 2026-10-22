import streamlit as st
import streamlit.components.v1 as components

from components.layout import (
    renderizar_chat_flutuante,
    renderizar_rodape,
)

# ============================================================
# URLs DAS EMPRESAS
# (as marcadas com TODO ainda são a página inteira do site da empresa;
#  o ideal é trocar pela URL real do mapa, como foi feito com a Sustentare)
# ============================================================
SUSTENTARE = "https://sustentare.saclimpeza2.com.br/mapa/?servico=go&lat=-23.550342&lng=-46.634158&maptype=roadmap"
LOCAT      = "https://locatsp.saclimpeza2.com.br/mapa/index-50.php"
CORPUS     = "https://corpus.sdo2.tec.br/mapa/"
LURB       = "https://splurb.sdo2.tec.br/mapa/"
LIMPEBRAS  = "https://limpebrassp.sdo2.tec.br/mapa/"
SPURBANO   = "https://spurbano.sdo2.tec.br/mapa/"
CONSTROESTE = "https://constroeste.sdo2.tec.br/mapa/"
ECOSS      = "https://ecoss.sdo2.tec.br/mapa/"
VERTERE    = "https://busca-servicos.gestorurbano.com.br/vertere/"
CPLU       = "https://cplu.sdo2.tec.br/mapa/"

# ============================================================
# RELAÇÃO: região -> subprefeitura -> (empresa, url)
# ============================================================
REGIOES = {
    "Centro": {
        "Sé": ("Sustentare Saneamento", SUSTENTARE),
    },
    "Zona Leste": {
        "Aricanduva":         ("Consórcio LOCAT", LOCAT),
        "Cidade Tiradentes":  ("Corpus Saneamento e Obras", CORPUS),
        "Ermelino Matarazzo": ("Corpus Saneamento e Obras", CORPUS),
        "Guaianases":         ("Corpus Saneamento e Obras", CORPUS),
        "Itaim Paulista":     ("Corpus Saneamento e Obras", CORPUS),
        "Itaquera":           ("Corpus Saneamento e Obras", CORPUS),
        "Mooca":              ("SP – LURB AMBIENTAL", LURB),
        "Penha":              ("Corpus Saneamento e Obras", CORPUS),
        "São Mateus":         ("LOCAT SP", LOCAT),
        "São Miguel Paulista": ("Corpus Saneamento e Obras", CORPUS),
        "Sapopemba":          ("LOCAT SP", LOCAT),
        "Vila Prudente":      ("LOCAT SP", LOCAT),
    },
    "Zona Norte": {
        "Casa Verde":              ("LIMPEBRAS", LIMPEBRAS),
        "Freguesia/Brasilândia":   ("SP URBANO", SPURBANO),
        "Jaçanã/Tremembé":         ("LIMPEBRAS", LIMPEBRAS),
        "Perus":                   ("SP URBANO", SPURBANO),
        "Pirituba/Jaraguá":        ("SP URBANO", SPURBANO),
        "Santana/Tucuruvi":        ("LIMPEBRAS", LIMPEBRAS),
        "Vila Maria/Vila Guilherme": ("LIMPEBRAS", LIMPEBRAS),
    },
    "Zona Oeste": {
        "Butantã":   ("CONSTROESTE", CONSTROESTE),
        "Lapa":      ("ECOSS SERVIÇOS", ECOSS),
        "Pinheiros": ("ECOSS SERVIÇOS", ECOSS),
    },
    "Zona Sul": {
        "Campo Limpo":     ("CONSTROESTE", CONSTROESTE),
        "Capela do Socorro": ("Vertere", VERTERE),
        "Cidade Ademar":   ("Companhia Paulista de Limpeza Urbana", CPLU),
        "Ipiranga":        ("Companhia Paulista de Limpeza Urbana", CPLU),
        "Jabaquara":       ("Companhia Paulista de Limpeza Urbana", CPLU),
        "M'Boi Mirim":     ("Vertere", VERTERE),
        "Parelheiros":     ("Vertere", VERTERE),
        "Santo Amaro":     ("CONSTROESTE", CONSTROESTE),
        "Vila Mariana":    ("ECOSS SERVIÇOS", ECOSS),
    },
}


SEM_SELECAO = "Selecione..."

def renderizar_consulta_regiao():
    st.header("🚛Cata-Bagulho")
    st.write("Confira a programação do Cata-Bagulho na sua região.")
 
    # 1º filtro: região (começa em "Selecione...")
    regiao = st.selectbox(
        "Selecione uma região",
        [SEM_SELECAO] + list(REGIOES.keys()),
        key="cb_regiao",
    )
 
    regiao_escolhida = regiao != SEM_SELECAO
 
    # 2º filtro: subprefeitura (inativo até escolher a região)
    if regiao_escolhida:
        opcoes_sub = [SEM_SELECAO] + list(REGIOES[regiao].keys())
    else:
        opcoes_sub = [SEM_SELECAO]
 
    subprefeitura = st.selectbox(
        "Selecione um distrito",
        opcoes_sub,
        # a key muda com a região: ao trocar de região, volta para "Selecione..."
        key=f"cb_subprefeitura_{regiao}",
        disabled=not regiao_escolhida,
    )
 
    if not regiao_escolhida:
        pass
        return
 
    if subprefeitura == SEM_SELECAO:
        st.info("Escolha um distrito")
        return
 
    empresa, url = REGIOES[regiao][subprefeitura]
    st.caption(f"Operadora responsável por {subprefeitura}: **{empresa}**")
 
    st.divider()
 
    # o iframe é recarregado automaticamente quando a subprefeitura (e a URL) muda
    components.iframe(url, height=600, scrolling=True)
 
    # alternativa caso o site da empresa bloqueie ser exibido dentro de outro site
    st.link_button("Abrir em nova aba", url)
 
 
renderizar_consulta_regiao()

renderizar_chat_flutuante()
renderizar_rodape()