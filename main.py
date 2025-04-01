
import streamlit as st
from modules.auth import login
from modules.dashboard import mostrar_dashboard
from modules.estudiantes import gestion_estudiantes
from modules.profesores import gestion_profesores
from modules.cursos import gestion_cursos
from modules.clases import gestion_clases
from modules.pagos import gestion_pagos
from modules.asistencia import gestion_asistencia

st.set_page_config(page_title="Academia", layout="wide")

def main():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if st.session_state["autenticado"]:
        st.sidebar.title("Menú principal")
        opciones = [
            "Dashboard",
            "Estudiantes",
            "Profesores",
            "Cursos",
            "Clases",
            "Pagos",
            "Asistencia"
        ]
        eleccion = st.sidebar.radio("Ir a", opciones)

        if eleccion == "Dashboard":
            mostrar_dashboard()
        elif eleccion == "Estudiantes":
            gestion_estudiantes()
        elif eleccion == "Profesores":
            gestion_profesores()
        elif eleccion == "Cursos":
            gestion_cursos()
        elif eleccion == "Clases":
            gestion_clases()
        elif eleccion == "Pagos":
            gestion_pagos()
        elif eleccion == "Asistencia":
            gestion_asistencia()
    else:
        login()

if __name__ == "__main__":
    main()
