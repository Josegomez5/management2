import streamlit as st
from modules.auth import login

st.set_page_config(layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login()
else:
    st.title("🎓 Bienvenido al Sistema Académico")
    st.write(f"Has iniciado sesión como: **{st.session_state.rol}**")
    st.write("Aquí irán los módulos según el rol.")
