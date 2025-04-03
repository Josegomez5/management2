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
            dias = sorted(df["fecha"].unique())

            colores = {}
            iconos = ["📘", "💡", "🧪", "🖌️", "📐", "🎵", "🌍", "🔬"]

            for curso in df["curso"].unique():
                colores[curso] = random.choice(["#FFDDC1", "#D1E8E4", "#F8E1F4", "#FFF6BF", "#E0BBE4"])

            for dia in dias:
                sub_df = df[df["fecha"] == dia][["hora_inicio", "hora_fin", "curso", "profesor"]]
                eventos = []
                for _, row in sub_df.iterrows():
                    color = colores.get(row["curso"], "#f0f0f0")
                    icon = random.choice(iconos)
                    eventos.append(f"<div style='background-color:{color}; padding:6px; border-radius:10px; margin-bottom:5px;'>"
                                   f"{icon} <b>{row['curso']}</b><br>🧑‍🏫 {row['profesor']}<br>🕘 {row['hora_inicio']} - {row['hora_fin']}"
                                   f"</div>")

                with st.expander(f"📅 {dia.strftime('%A, %d %B %Y')}"):
                    for evento in eventos:
                        st.markdown(evento, unsafe_allow_html=True)
        else:
            st.info("No hay clases registradas para este mes.")
