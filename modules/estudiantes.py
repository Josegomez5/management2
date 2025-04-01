import streamlit as st
import pandas as pd
import io
from modules.auth import get_connection
from datetime import date

def gestion_estudiantes():
    st.title("🧑‍🎓 Gestión de Estudiantes")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    seccion = st.radio("Selecciona una opción:", ["Registrar Estudiante", "Lista de Estudiantes", "Estudiante"], horizontal=True)

    if seccion == "Registrar Estudiante":
        st.subheader("➕ Registrar nuevo estudiante")
        cursor.execute("SELECT id, nombre FROM cursos")
        cursos = cursor.fetchall()
        cursos_dict = {curso['nombre']: curso['id'] for curso in cursos}

        with st.form("form_estudiante"):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")
            tutor_nombre = st.text_input("Nombre del tutor")
            tutor_correo = st.text_input("Correo del tutor")
            tutor_telefono = st.text_input("Teléfono del tutor")
            parentesco = st.selectbox("Parentesco", ["Padre", "Madre", "Tío/a", "Otro"])
            curso_seleccionado = st.selectbox("Curso", list(cursos_dict.keys()))
            submit = st.form_submit_button("Guardar")

            if submit:
                cursor.execute("""
                    INSERT INTO estudiantes (nombre, correo, telefono, tutor_nombre, tutor_correo, tutor_telefono, parentesco)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre, correo, telefono, tutor_nombre, tutor_correo, tutor_telefono, parentesco))
                estudiante_id = cursor.lastrowid
                curso_id = cursos_dict[curso_seleccionado]
                cursor.execute("INSERT INTO estudiante_curso (estudiante_id, curso_id) VALUES (%s, %s)", (estudiante_id, curso_id))
