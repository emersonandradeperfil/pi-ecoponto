import streamlit as st

st.set_page_config(page_title="Limpeza - SP", page_icon="♻", layout="wide")

# O app.py agora gerencia as páginas apontando para arquivos físicos em 'pages/'
pg = st.navigation([
    st.Page("pages/home.py", title="Home", icon="🏠"),
    st.Page("pages/chat.py", title="Assistente IA", icon="💬"),
    st.Page("pages/ecoponto.py", title="Ecoponto", icon="♻"),
    st.Page("pages/cata_bagulho.py", title="Cata-Bagulho", icon="🚛"),
    st.Page("pages/analises.py", title="Análises SP156", icon="📊"),
])

pg.run()