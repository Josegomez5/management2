
import streamlit as st
from modules.auth import login
from modules.dashboard import mostrar_dashboard
from modules.estudiantes import gestion_estudiantes
from modules.profesores import gestion_profesores
#from modules.cursos import gestion_cursos
from modules.pagos import gestion_pagos
from modules.asistencia import gestion_asistencia

st.set_page_config(page_title="Academia", layout="wide")

def main():
    if login():
        st.sidebar.title("Menú principal")
        opciones = [
            "Dashboard",
            "Estudiantes",
            "Profesores",
            "Cursos",
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
        elif eleccion == "Pagos":
            gestion_pagos()
        elif eleccion == "Asistencia":
            gestion_asistencia()

if __name__ == "__main__":
    main()
