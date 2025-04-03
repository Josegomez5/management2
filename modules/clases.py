
import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from modules.auth import get_connection
import io

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
        curso_dict = {c["nombre"]: c["id"] for c in cursos}
        curso_nombre = st.selectbox("Curso", list(curso_dict.keys()))
        curso_id = curso_dict[curso_nombre]

        cursor.execute("SELECT id, nombre FROM profesores")
        profesores = cursor.fetchall()
        prof_dict = {p["nombre"]: p["id"] for p in profesores}
        prof_nombre = st.selectbox("Profesor", list(prof_dict.keys()))
        prof_id = prof_dict[prof_nombre]

        fecha = st.date_input("Fecha")
        hora_inicio = st.time_input("Hora inicio")
        hora_fin = st.time_input("Hora fin")

        if st.button("Guardar clase"):
            cursor.execute("INSERT INTO clases (curso_id, profesor_id, fecha, hora_inicio, hora_fin) VALUES (%s,%s,%s,%s,%s)",
                           (curso_id, prof_id, fecha, hora_inicio, hora_fin))
            conn.commit()
            st.success("Clase registrada")

    elif opcion == "📄 Lista de Clases":
        st.subheader("📋 Clases registradas")
        cursor.execute("""
            SELECT cl.id, cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            ORDER BY cl.fecha DESC
        """)
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            st.download_button("📥 Descargar Excel", data=output.getvalue(), file_name="clases.xlsx")
        else:
            st.info("No hay clases registradas aún.")

    elif opcion == "🛠️ Editar / Eliminar Clases":
        st.subheader("Editar / Eliminar clase")
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
            seleccion = st.selectbox("Selecciona una clase", df["label"])
            clase_id = int(df[df["label"] == seleccion]["id"].values[0])

            cursor.execute("SELECT * FROM clases WHERE id = %s", (clase_id,))
            clase = cursor.fetchone()

            cursor.execute("SELECT id, nombre FROM cursos")
            cursos = cursor.fetchall()
            curso_dict = {c["nombre"]: c["id"] for c in cursos}
            curso_nombre = st.selectbox("Curso", list(curso_dict.keys()), index=list(curso_dict.values()).index(clase["curso_id"]))

            cursor.execute("SELECT id, nombre FROM profesores")
            profesores = cursor.fetchall()
            prof_dict = {p["nombre"]: p["id"] for p in profesores}
            prof_nombre = st.selectbox("Profesor", list(prof_dict.keys()), index=list(prof_dict.values()).index(clase["profesor_id"]))

            fecha = st.date_input("Fecha", value=clase["fecha"])
            hora_inicio = st.time_input("Hora inicio", value=clase["hora_inicio"])
            hora_fin = st.time_input("Hora fin", value=clase["hora_fin"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar"):
                    cursor.execute("UPDATE clases SET curso_id=%s, profesor_id=%s, fecha=%s, hora_inicio=%s, hora_fin=%s WHERE id=%s",
                                   (curso_dict[curso_nombre], prof_dict[prof_nombre], fecha, hora_inicio, hora_fin, clase_id))
                    conn.commit()
                    st.success("Clase actualizada")
                    st.experimental_rerun()
            with col2:
                if st.button("🗑 Eliminar"):
                    cursor.execute("DELETE FROM clases WHERE id = %s", (clase_id,))
                    conn.commit()
                    st.warning("Clase eliminada")
                    st.experimental_rerun()
        else:
            st.info("No hay clases para editar.")

    elif opcion == "📅 Vista Calendario":
        vista_calendario()


def vista_calendario():
    st.subheader("📅 Calendario de Clases")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    mes = st.selectbox("Mes", list(calendar.month_name)[1:])
    anio = st.number_input("Año", min_value=2020, max_value=2100, value=datetime.now().year)
    mes_num = list(calendar.month_name).index(mes)

    primer_dia = date(anio, mes_num, 1)
    ultimo_dia = date(anio, mes_num, calendar.monthrange(anio, mes_num)[1])

    cursor.execute("""
        SELECT cl.id, cl.fecha, cl.hora_inicio, c.nombre as curso, p.nombre as profesor
        FROM clases cl
        JOIN cursos c ON cl.curso_id = c.id
        JOIN profesores p ON cl.profesor_id = p.id
        WHERE cl.fecha BETWEEN %s AND %s
        ORDER BY cl.fecha, cl.hora_inicio
    """, (primer_dia, ultimo_dia))
    clases = cursor.fetchall()

    df = pd.DataFrame(clases)
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

    dias_semana = list(calendar.day_abbr)
    st.markdown("<style>.calendar-title { color: white; font-weight: bold; }</style>", unsafe_allow_html=True)

    for semana in calendar.Calendar().monthdatescalendar(anio, mes_num):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia.month == mes_num:
                    st.markdown(f"<div class='calendar-title'>{dias_semana[i]}<br>{dia.day}</div>", unsafe_allow_html=True)
                    if not df.empty:
                        eventos = df[df["fecha"] == dia]
                        for _, row in eventos.iterrows():
                            hora_str = str(row["hora_inicio"])[:5]
                            st.info(f"🕘 {hora_str} - {row['curso']} ({row['profesor']})")
                    if st.button("➕ Añadir", key=f"add_{dia}"):
                        st.session_state.dia_seleccionado = dia
