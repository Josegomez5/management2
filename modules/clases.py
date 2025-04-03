import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta, datetime, time
from modules.auth import get_connection
import calendar
import random
import streamlit.components.v1 as components


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

            dias_mes = calendar.monthrange(anio, mes_num)[1]
            calendario_html = "<table style='width:100%; border-collapse: collapse;'>"
            calendario_html += "<tr>" + "".join(f"<th style='border:1px solid #ccc; padding:5px'>{day}</th>" for day in ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]) + "</tr>"

            day_pointer = date(anio, mes_num, 1)
            weekday = (day_pointer.weekday() + 1) % 7

            calendario_html += "<tr>" + "<td></td>" * weekday
            for day in range(1, dias_mes + 1):
                current_day = date(anio, mes_num, day)
                eventos = df[df["fecha"] == current_day]
                content = f"<strong>{day}</strong><br>"
                for _, row in eventos.iterrows():
                    content += f"<div style='background:#e3f2fd; padding:2px; margin:2px; border-radius:4px;'>🕘 {row['hora_inicio']} - {row['curso']}<br><small>{row['profesor']}</small></div>"
                content += f"<br><a href='?form_dia={current_day}' style='font-size:0.85em'>➕ Añadir</a>"
                calendario_html += f"<td style='vertical-align:top; border:1px solid #ccc; padding:5px'>{content}</td>"
                weekday += 1
                if weekday == 7:
                    calendario_html += "</tr><tr>"
                    weekday = 0
            if weekday != 0:
                calendario_html += "<td></td>" * (7 - weekday) + "</tr>"
            calendario_html += "</table>"

            components.html(f"<div style='overflow-x:auto'>{calendario_html}</div>", height=600, scrolling=True)

            form_dia = st.query_params.get("form_dia")
            if form_dia:
                st.markdown("---")
                st.subheader(f"Registrar clase el {form_dia}")
                cursor.execute("SELECT id, nombre FROM cursos")
                cursos = cursor.fetchall()
                cursos_dict = {c["nombre"]: c["id"] for c in cursos}
                curso_nombre = st.selectbox("Curso", list(cursos_dict.keys()), key="f1")
                curso_id = cursos_dict[curso_nombre]

                cursor.execute("SELECT id, nombre FROM profesores")
                profesores = cursor.fetchall()
                profesores_dict = {p["nombre"]: p["id"] for p in profesores}
                profesor_nombre = st.selectbox("Profesor", list(profesores_dict.keys()), key="f2")
                profesor_id = profesores_dict[profesor_nombre]

                hora_inicio = st.time_input("Hora de inicio", key="f3")
                hora_fin = st.time_input("Hora de fin", key="f4")

                if st.button("Guardar clase", key="f5"):
                    cursor.execute(
                        "INSERT INTO clases (curso_id, profesor_id, fecha, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s, %s)",
                        (curso_id, profesor_id, form_dia, hora_inicio, hora_fin)
                    )
                    conn.commit()
                    st.success("Clase registrada exitosamente")
        else:
            st.info("No hay clases registradas para este mes.")
