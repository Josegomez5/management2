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
                conn.commit()
                st.success("Estudiante registrado exitosamente")

    elif seccion == "Lista de Estudiantes":
        st.subheader("📋 Lista de estudiantes")
        cursor.execute("""
            SELECT e.id, e.nombre, e.correo, e.telefono, e.tutor_nombre, e.tutor_correo, e.tutor_telefono, e.parentesco,
                   GROUP_CONCAT(c.nombre SEPARATOR ', ') AS cursos
            FROM estudiantes e
            LEFT JOIN estudiante_curso ec ON e.id = ec.estudiante_id
            LEFT JOIN cursos c ON ec.curso_id = c.id
            GROUP BY e.id
        """)
        estudiantes = cursor.fetchall()

        if estudiantes:
            df = pd.DataFrame(estudiantes)
            st.dataframe(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=output.getvalue(),
                file_name="estudiantes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay estudiantes registrados aún.")

    elif seccion == "Estudiante":
        st.subheader("🔍 Buscar estudiante")
        cursor.execute("""
            SELECT e.id, e.nombre, e.correo, e.telefono, e.tutor_nombre, e.tutor_correo, e.tutor_telefono, e.parentesco,
                   GROUP_CONCAT(c.nombre SEPARATOR ', ') AS cursos
            FROM estudiantes e
            LEFT JOIN estudiante_curso ec ON e.id = ec.estudiante_id
            LEFT JOIN cursos c ON ec.curso_id = c.id
            GROUP BY e.id
        """)
        estudiantes = cursor.fetchall()

        if estudiantes:
            busqueda = st.text_input("Buscar por nombre o correo")
            opciones = {f"{e['nombre']} ({e['correo']})": e['id'] for e in estudiantes}

            if busqueda:
                opciones = {k: v for k, v in opciones.items() if busqueda.lower() in k.lower()}

            seleccionado = st.selectbox("Selecciona un estudiante:", ["-- Seleccionar --"] + list(opciones.keys()))

            if seleccionado != "-- Seleccionar --":
                estudiante_id = opciones[seleccionado]
                est = next(e for e in estudiantes if e['id'] == estudiante_id)

                st.subheader(f"📄 Perfil de {est['nombre']}")
                st.markdown(f"**Correo:** {est['correo']}")
                st.markdown(f"**Teléfono:** {est['telefono']}")
                st.markdown(f"**Curso(s):** {est['cursos']}")
                st.markdown("**👨‍👩‍👧 Tutor:**")
                st.markdown(f"- Nombre: {est['tutor_nombre']}")
                st.markdown(f"- Correo: {est['tutor_correo']}")
                st.markdown(f"- Teléfono: {est['tutor_telefono']}")
                st.markdown(f"- Parentesco: {est['parentesco']}")
