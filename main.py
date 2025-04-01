import streamlit as st
from modules.auth import login
from modules.dashboard import mostrar_dashboard
from modules.estudiantes import gestion_estudiantes
from modules.profesores import gestion_profesores
from modules.cursos import gestion_cursos
from modules.asistencia import gestion_asistencia
#from modules.clases import gestion_clases
#from modules.calificaciones import gestion_calificaciones
from modules.pagos import gestion_pagos


st.set_page_config(layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login()
else:
    st.title("🎓 Bienvenido al Sistema Académico")
    st.write(f"Has iniciado sesión como: **{st.session_state.rol}**")

    if st.session_state.rol == "admin":
        menu = ["Dashboard", "Estudiantes", "Asistencia", "Pagos"]
        opcion = st.sidebar.radio("Menú", menu)

        if opcion == "Dashboard":
            mostrar_dashboard()
        elif opcion == "Estudiantes":
            gestion_estudiantes()
        elif opcion == "Asistencia":
            gestion_asistencia()
        elif opcion == "Pagos":
            gestion_pagos()
        elif opcion == "Profesores":
            gestion_profesores()
    else:
        st.info("Módulos aún no disponibles para este rol.")
