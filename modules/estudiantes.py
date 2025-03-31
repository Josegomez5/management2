import streamlit as st
import pandas as pd
import io
from modules.auth import get_connection

def gestion_estudiantes():
    st.title("🧑‍🎓 Gestión de Estudiantes")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    seccion = st.radio("Selecciona una opción:", ["Registrar Estudiante", "Lista de Estudiantes"], horizontal=True)

    if seccion == "Registrar Estudiante":
        st.subheader("➕ Registrar nuevo estudiante")
        with st.form("form_estudiante"):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")
            tutor_nombre = st.text_input("Nombre del tutor")
            tutor_correo = st.text_input("Correo del tutor")
            tutor_telefono = st.text_input("Teléfono del tutor")
            parentesco = st.selectbox("Parentesco", ["Padre", "Madre", "Tío/a", "Otro"])
            submit = st.form_submit_button("Guardar")

            if submit:
                cursor.execute("""
                    INSERT INTO estudiantes (nombre, correo, telefono, tutor_nombre, tutor_correo, tutor_telefono, parentesco)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre, correo, telefono, tutor_nombre, tutor_correo, tutor_telefono, parentesco))
                conn.commit()
                st.success("Estudiante registrado exitosamente")

    elif seccion == "Lista de Estudiantes":
        st.subheader("📋 Lista de estudiantes")
        cursor.execute("SELECT * FROM estudiantes")
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
