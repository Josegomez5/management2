import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta, datetime, time
from modules.auth import get_connection
import calendar
import random


def gestion_clases():
    st.title("📅 Gestión de Clases")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if "dia_seleccionado" not in st.session_state:
        st.session_state.dia_seleccionado = None

    opcion = st.radio("Selecciona una opción:", [
        "📘 Registrar Clase",
        "📄 Lista de Clases",
        "🛠️ Editar / Eliminar Clases",
        "📅 Vista Calendario"
    ], horizontal=True)

    if opcion == "📘 Registrar Clase":
        st.subheader("Registrar nueva clase")
        cursor.execute("SELECT id, nombre FROM cursos")
        cursos = cursor.fetchall()
        cursos_dict = {c["nombre"]: c["id"] for c in cursos}
        curso_nombre = st.selectbox("Curso", list(cursos_dict.keys()))
        curso_id = cursos_dict[curso_nombre]

        cursor.execute("SELECT id, nombre FROM profesores")
        profesores = cursor.fetchall()
        profesores_dict = {p["nombre"]: p["id"] for p in profesores}
        profesor_nombre = st.selectbox("Profesor", list(profesores_dict.keys()))
        profesor_id = profesores_dict[profesor_nombre]

        fecha = st.date_input("Fecha")
        hora_inicio = st.time_input("Hora de inicio")
        hora_fin = st.time_input("Hora de fin")

        if st.button("Guardar clase"):
            cursor.execute(
                "INSERT INTO clases (curso_id, profesor_id, fecha, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s, %s)",
                (curso_id, profesor_id, fecha, hora_inicio, hora_fin)
            )
            conn.commit()
            st.success("Clase registrada exitosamente")

    elif opcion == "📄 Lista de Clases":
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

    elif opcion == "🛠️ Editar / Eliminar Clases":
        pass

    elif opcion == "📅 Vista Calendario":
        st.subheader("🗓️ Calendario Mensual de Clases")

        mes = st.selectbox("Mes", list(calendar.month_name)[1:])
        anio = st.number_input("Año", min_value=2020, max_value=2100, value=date.today().year)
        mes_num = list(calendar.month_name).index(mes)

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

            dias_mes = calendar.monthrange(anio, mes_num)[1]
            for day in range(1, dias_mes + 1):
                current_day = date(anio, mes_num, day)
                eventos = df[df["fecha"] == current_day]

                with st.expander(f"📅 {current_day.strftime('%A, %d %B %Y')}"):
                    for _, row in eventos.iterrows():
                        st.markdown(f"- 🕘 {row['hora_inicio']} - {row['curso']} ({row['profesor']})")

                    if st.button(f"➕ Añadir clase", key=f"add_{current_day}"):
                        st.session_state.dia_seleccionado = current_day

            if st.session_state.dia_seleccionado:
                st.markdown("---")
                st.subheader(f"Registrar clase el {st.session_state.dia_seleccionado.strftime('%A, %d %B %Y')}")

                cursor.execute("SELECT id, nombre FROM cursos")
                cursos = cursor.fetchall()
                cursos_dict = {c["nombre"]: c["id"] for c in cursos}
                curso_nombre = st.selectbox("Curso", list(cursos_dict.keys()), key="form_curso")
                curso_id = cursos_dict[curso_nombre]

                cursor.execute("SELECT id, nombre FROM profesores")
                profesores = cursor.fetchall()
                profesores_dict = {p["nombre"]: p["id"] for p in profesores}
                profesor_nombre = st.selectbox("Profesor", list(profesores_dict.keys()), key="form_prof")
                profesor_id = profesores_dict[profesor_nombre]

                hora_inicio = st.time_input("Hora de inicio", key="form_ini")
                hora_fin = st.time_input("Hora de fin", key="form_fin")

                if st.button("Guardar clase", key="form_submit"):
                    cursor.execute(
                        "INSERT INTO clases (curso_id, profesor_id, fecha, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s, %s)",
                        (curso_id, profesor_id, st.session_state.dia_seleccionado, hora_inicio, hora_fin)
                    )
                    conn.commit()
                    st.success("Clase registrada exitosamente")
                    st.session_state.dia_seleccionado = None
        else:
            st.info("No hay clases registradas para este mes.")
