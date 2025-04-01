
import streamlit as st
import pandas as pd
from modules.auth import get_connection
import io

def gestion_profesores():
    st.title("👨‍🏫 Gestión de Profesores")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    seccion = st.radio("Selecciona una opción:", ["Registrar Profesor", "Lista de Profesores"], horizontal=True)

    if seccion == "Registrar Profesor":
        st.subheader("➕ Registrar nuevo profesor")
        with st.form("form_profesor"):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")
            especialidad = st.text_input("Especialidad")
            submit = st.form_submit_button("Guardar")

            if submit:
                cursor.execute("INSERT INTO profesores (nombre, correo, telefono, especialidad) VALUES (%s, %s, %s, %s)",
                               (nombre, correo, telefono, especialidad))
                conn.commit()
                st.success("Profesor registrado exitosamente")

    elif seccion == "Lista de Profesores":
        st.subheader("📋 Lista de profesores")
        cursor.execute("SELECT * FROM profesores")
        profesores = cursor.fetchall()

        if profesores:
            df = pd.DataFrame(profesores)
            st.dataframe(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=output.getvalue(),
                file_name="profesores.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay profesores registrados aún.")
# módulo profesores
