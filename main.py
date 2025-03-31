import streamlit as st
from modules.auth import login
from modules.dashboard import mostrar_dashboard
from modules.estudiantes import gestion_estudiantes

st.set_page_config(layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login()
else:
    st.sidebar.title("Menú Principal")
    if st.session_state.rol == "admin":
        opcion = st.sidebar.radio("Ir a:", ["Dashboard", "Estudiantes"])

        if opcion == "Dashboard":
            mostrar_dashboard()
        elif opcion == "Estudiantes":
            gestion_estudiantes()
    else:
        st.title("🎓 Bienvenido al Sistema Académico")
        st.write(f"Has iniciado sesión como: **{st.session_state.rol}**")
        st.info("Módulos aún no disponibles para este rol.")
