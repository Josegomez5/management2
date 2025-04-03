
import streamlit as st
import pandas as pd
import calendar
from datetime import date
from modules.auth import get_connection
import io

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
    first_weekday = (first_weekday + 1) % 7  # Ajustar lunes
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
        df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        render_html_calendar(df, anio, mes_num)

        st.markdown("### 📋 Lista de Clases del Mes")
        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Clases del mes")
        st.download_button(
            label="⬇️ Descargar Excel",
            data=output.getvalue(),
            file_name="clases_mes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay clases registradas este mes.")
