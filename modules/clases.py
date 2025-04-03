
import streamlit as st
import pandas as pd
import calendar
import io
from datetime import date, datetime
from modules.auth import get_connection

def render_html_calendar(df, anio, mes):
    st.markdown("""
        <style>
        .calendar {
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
            font-family: Arial, sans-serif;
        }
        .day-header {
            font-weight: bold;
            text-align: center;
            padding: 5px;
            background: #444;
            color: white;
            border-radius: 5px;
        }
        .day-box {
            background: #1a1a1a;
            border: 1px solid #444;
            min-height: 100px;
            border-radius: 5px;
            padding: 5px;
            color: white;
        }
        .day-number {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .event {
            background: #2a9d8f;
            border-radius: 3px;
            padding: 2px 5px;
            margin-top: 4px;
            font-size: 0.85em;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🗓 Calendario Visual")
    headers = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    st.markdown('<div class="calendar">' + ''.join([f'<div class="day-header">{h}</div>' for h in headers]) + '</div>', unsafe_allow_html=True)

    first_weekday, days_in_month = calendar.monthrange(anio, mes)
    first_weekday = (first_weekday + 1) % 7
    calendar_cells = [""] * first_weekday + list(range(1, days_in_month + 1))
    rows = []

    for day in calendar_cells:
        if day == "":
            box = '<div class="day-box"></div>'
        else:
            current_date = date(anio, mes, day)
            clases = df[df['fecha'] == current_date]
            eventos = "".join([f"<div class='event'>⏰ {c['hora_inicio']} - {c['curso']}<br><small>{c['profesor']}</small></div>" for _, c in clases.iterrows()])
            box = f"<div class='day-box'><div class='day-number'>{day}</div>{eventos}</div>"
        rows.append(box)

    full_calendar_html = '<div class="calendar">' + ''.join(rows) + '</div>'
    st.markdown(full_calendar_html, unsafe_allow_html=True)

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
        hora_inicio = st.time_input("Hora inicio")
        hora_fin = st.time_input("Hora fin")

        if st.button("Guardar clase"):
            cursor.execute("INSERT INTO clases (curso_id, profesor_id, fecha, hora_inicio, hora_fin) VALUES (%s,%s,%s,%s,%s)",
                           (curso_id, profesor_id, fecha, hora_inicio, hora_fin))
            conn.commit()
            st.success("Clase registrada correctamente")

    elif opcion == "📄 Lista de Clases":
        cursor.execute("""
            SELECT cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            ORDER BY cl.fecha DESC
        """)
        clases = cursor.fetchall()
        if clases:
            df = pd.DataFrame(clases)
            st.dataframe(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button("⬇️ Descargar Excel", data=output.getvalue(), file_name="clases.xlsx")
        else:
            st.info("No hay clases registradas.")

    elif opcion == "🛠️ Editar / Eliminar Clases":
        cursor.execute("""
            SELECT cl.id, cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            ORDER BY cl.fecha DESC
        """)
        clases = cursor.fetchall()
        if clases:
            df = pd.DataFrame(clases)
            df["label"] = df.apply(lambda row: f"{row['fecha']} - {row['curso']} ({row['profesor']})", axis=1)
            seleccion = st.selectbox("Selecciona una clase para editar", df["label"])
            clase_id = int(df[df["label"] == seleccion]["id"].values[0])

            cursor.execute("SELECT * FROM clases WHERE id = %s", (clase_id,))
            clase = cursor.fetchone()

            cursor.execute("SELECT id, nombre FROM cursos")
            cursos = cursor.fetchall()
            cursos_dict = {c["nombre"]: c["id"] for c in cursos}
            curso_nombre = st.selectbox("Curso", list(cursos_dict.keys()), index=list(cursos_dict.values()).index(clase["curso_id"]))

            cursor.execute("SELECT id, nombre FROM profesores")
            profesores = cursor.fetchall()
            profesores_dict = {p["nombre"]: p["id"] for p in profesores}
            profesor_nombre = st.selectbox("Profesor", list(profesores_dict.keys()), index=list(profesores_dict.values()).index(clase["profesor_id"]))

            fecha = st.date_input("Fecha", value=clase["fecha"])
            hora_inicio = st.time_input("Hora inicio", value=clase["hora_inicio"])
            hora_fin = st.time_input("Hora fin", value=clase["hora_fin"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar"):
                    cursor.execute("UPDATE clases SET curso_id=%s, profesor_id=%s, fecha=%s, hora_inicio=%s, hora_fin=%s WHERE id=%s",
                                   (cursos_dict[curso_nombre], profesores_dict[profesor_nombre], fecha, hora_inicio, hora_fin, clase_id))
                    conn.commit()
                    st.success("Clase actualizada correctamente")
                    st.experimental_rerun()
            with col2:
                if st.button("🗑 Eliminar"):
                    cursor.execute("DELETE FROM clases WHERE id=%s", (clase_id,))
                    conn.commit()
                    st.warning("Clase eliminada correctamente")
                    st.experimental_rerun()
        else:
            st.info("No hay clases para editar.")

    elif opcion == "📅 Vista Calendario":
        mes_actual = date.today().month
        anio_actual = date.today().year
        mes = st.selectbox("Mes", list(calendar.month_name)[1:], index=mes_actual - 1)
        anio = st.number_input("Año", min_value=2020, max_value=2100, value=anio_actual)
        mes_num = list(calendar.month_name).index(mes)

        cursor.execute("""
            SELECT cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            WHERE cl.fecha BETWEEN %s AND %s
            ORDER BY cl.fecha, cl.hora_inicio
        """, (date(anio, mes_num, 1), date(anio, mes_num, calendar.monthrange(anio, mes_num)[1])))
        clases = cursor.fetchall()

        if clases:
            df = pd.DataFrame(clases)
            df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
            render_html_calendar(df, anio, mes_num)
            st.markdown("### 📋 Lista de clases del mes")
            st.dataframe(df)
        else:
            st.info("No hay clases registradas este mes.")
