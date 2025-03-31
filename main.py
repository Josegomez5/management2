import streamlit as st
from modules.dashboard import mostrar_dashboard
from modules.estudiantes import gestion_estudiantes
from modules.profesores import gestion_profesores
from modules.cursos import gestion_cursos
from modules.clases import gestion_clases
from modules.pagos import gestion_pagos
from modules.calificaciones import gestion_calificaciones
from modules.asistencia import gestion_asistencia
from modules.auth import login

st.set_page_config(layout="wide")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login()
else:
    st.sidebar.title("Menú Principal")
    menu = [
        "Dashboard",
        "Estudiantes",
        "Profesores",
        "Cursos",
        "Clases",
        "Pagos",
        "Calificaciones",
        "Asistencia"
    ]
    opcion = st.sidebar.selectbox("Selecciona un módulo", menu)

    if opcion == "Dashboard":
        mostrar_dashboard()
    elif opcion == "Estudiantes":
        gestion_estudiantes()
    elif opcion == "Profesores":
        gestion_profesores()
    elif opcion == "Cursos":
        gestion_cursos()
    elif opcion == "Clases":
        gestion_clases()
    elif opcion == "Pagos":
        gestion_pagos()
    elif opcion == "Calificaciones":
        gestion_calificaciones()
    elif opcion == "Asistencia":
        gestion_asistencia()
