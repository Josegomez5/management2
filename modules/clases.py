
import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from modules.auth import get_connection

def vista_calendario():
    st.subheader("📅 Calendario de Clases")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    meses = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    mes = st.selectbox("Mes", meses, index=3)
    anio = st.number_input("Año", min_value=2020, max_value=2100, value=datetime.now().year)
    mes_num = meses.index(mes) + 1

    primer_dia = date(anio, mes_num, 1)
    ultimo_dia = date(anio, mes_num, calendar.monthrange(anio, mes_num)[1])

    cursor.execute("""
        SELECT cl.id, cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
        FROM clases cl
        JOIN cursos c ON cl.curso_id = c.id
        JOIN profesores p ON cl.profesor_id = p.id
        WHERE cl.fecha BETWEEN %s AND %s
        ORDER BY cl.fecha, cl.hora_inicio
    """, (primer_dia, ultimo_dia))
    clases = cursor.fetchall()

    df = pd.DataFrame(clases)
    if df.empty:
        st.info("No hay clases registradas para este mes.")
        return

    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    st.markdown("<style>.calendar-title { color: white; font-weight: bold; }</style>", unsafe_allow_html=True)

    st.markdown("### 🗓 Vista semanal")
    for semana in calendar.Calendar().monthdatescalendar(anio, mes_num):
        cols = st.columns(7)
        for i, dia in enumerate(semana):
            with cols[i]:
                if dia.month == mes_num:
                    st.markdown(f"<div class='calendar-title'>{dias_semana[i]}<br>{dia.day}</div>", unsafe_allow_html=True)
                    eventos = df[df["fecha"] == dia]
                    for _, row in eventos.iterrows():
                        hora = str(row["hora_inicio"])[:5]
                        st.markdown(f"🕘 {hora}<br>{row['curso']}<br><small>{row['profesor']}</small>", unsafe_allow_html=True)

    st.markdown("### 📋 Lista de todas las clases del mes")
    st.dataframe(df)
