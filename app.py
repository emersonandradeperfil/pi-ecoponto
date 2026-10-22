import streamlit as st

st.set_page_config(page_title="Limpeza - SP", page_icon="♻", layout="wide")

# O app.py agora gerencia as páginas apontando para arquivos físicos em 'pages/'
pg = st.navigation([
    st.Page("pages/0_🏠_Home.py", title="Home", icon="🏠"),
    st.Page("pages/1_💬_Chat.py", title="Assistente IA", icon="💬"),
    st.Page("pages/2_♻_Ecoponto.py", title="Ecoponto", icon="♻"),
    st.Page("pages/3_🚛_Cata-Bagulho.py", title="Cata-Bagulho", icon="🚛"),
    st.Page("pages/4_📊_Analises.py", title="Análises SP156", icon="📊"),
])

pg.run()