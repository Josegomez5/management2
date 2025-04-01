
import streamlit as st
import pandas as pd
import io
from modules.auth import get_connection

def gestion_cursos():
    st.title("📘 Gestión de Cursos")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    opcion = st.radio("Seleccione una opción:", ["Registrar Curso", "Lista de Cursos"], horizontal=True)

    if opcion == "Registrar Curso":
        st.subheader("➕ Nuevo Curso")
        with st.form("form_curso"):
            nombre = st.text_input("Nombre del curso")
            descripcion = st.text_area("Descripción")
            submit = st.form_submit_button("Guardar")

            if submit:
                cursor.execute("INSERT INTO cursos (nombre, descripcion) VALUES (%s, %s)", (nombre, descripcion))
                conn.commit()
                st.success("Curso registrado exitosamente")

    elif opcion == "Lista de Cursos":
        st.subheader("📋 Cursos Registrados")
        cursor.execute("SELECT * FROM cursos")
        cursos = cursor.fetchall()

        if cursos:
            df = pd.DataFrame(cursos)
            st.dataframe(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=output.getvalue(),
                file_name="cursos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay cursos registrados.")
# módulo cursos
