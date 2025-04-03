
import streamlit as st
import pandas as pd
import io
from datetime import date
from modules.auth import get_connection
import calendar

def gestion_clases():
    st.title("📅 Gestión de Clases")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    opcion = st.radio("Selecciona una opción:", [
        "📄 Lista de Clases",
        "📅 Vista Calendario"
    ], horizontal=True)

    if opcion == "📄 Lista de Clases":
        st.subheader("📋 Clases Programadas")
        cursor.execute("""
            SELECT c.nombre as curso, p.nombre as profesor, cl.fecha, cl.hora_inicio, cl.hora_fin
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            ORDER BY cl.fecha DESC, cl.hora_inicio
        """)
        clases = cursor.fetchall()

        if clases:
            df = pd.DataFrame(clases)
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="Descargar Excel",
                data=output.getvalue(),
                file_name="clases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay clases registradas aún.")

    elif opcion == "📅 Vista Calendario":
        st.subheader("📅 Vista mensual")

        meses = list(calendar.month_name)[1:]
        mes_actual = date.today().month
        anio_actual = date.today().year

        mes = st.selectbox("Mes", meses, index=mes_actual - 1)
        anio = st.number_input("Año", min_value=2020, max_value=2100, value=anio_actual)

        mes_num = meses.index(mes) + 1
        primer_dia = date(anio, mes_num, 1)
        ultimo_dia = date(anio, mes_num, calendar.monthrange(anio, mes_num)[1])

        cursor.execute("""
            SELECT cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            WHERE cl.fecha BETWEEN %s AND %s
            ORDER BY cl.fecha, cl.hora_inicio
        """, (primer_dia, ultimo_dia))
        clases = cursor.fetchall()

        if clases:
            df = pd.DataFrame(clases)
            df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
            st.subheader("📋 Lista de todas las clases del mes")
            st.dataframe(df)
        else:
            st.info("No hay clases registradas para este mes.")
