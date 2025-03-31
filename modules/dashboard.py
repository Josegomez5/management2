import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from modules.auth import get_connection

def mostrar_dashboard():
    st.title("📊 Panel de Control - Dashboard")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM estudiantes")
    total_estudiantes = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM profesores")
    total_profesores = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS total FROM cursos")
    total_cursos = cursor.fetchone()['total']

    cursor.execute("""
        SELECT SUM(monto) AS total_pagado
        FROM pagos
        WHERE MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE())
    """)
    total_pagado_mes = cursor.fetchone()['total_pagado'] or 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Estudiantes", total_estudiantes)
    col2.metric("Profesores", total_profesores)
    col3.metric("Cursos", total_cursos)
    col4.metric("Pagos este mes", f"${total_pagado_mes:.2f}")

    st.subheader("📅 Pagos por día este mes")
    cursor.execute("""
        SELECT DAY(fecha) AS dia, SUM(monto) AS total
        FROM pagos
        WHERE MONTH(fecha) = MONTH(CURDATE()) AND YEAR(fecha) = YEAR(CURDATE())
        GROUP BY dia ORDER BY dia
    """)
    pagos_dia = cursor.fetchall()
    if pagos_dia:
        df_pagos = pd.DataFrame(pagos_dia)
        fig = px.bar(df_pagos, x='dia', y='total', labels={'dia': 'Día', 'total': 'Monto'}, title="Pagos diarios")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📘 Clases del día")
    hoy = date.today()
    cursor.execute("""
        SELECT c.nombre AS curso, p.nombre AS profesor, cl.hora_inicio, cl.hora_fin
        FROM clases cl
        JOIN cursos c ON cl.curso_id = c.id
        JOIN profesores p ON cl.profesor_id = p.id
        WHERE cl.fecha = %s
        ORDER BY cl.hora_inicio
    """, (hoy,))
    clases_hoy = cursor.fetchall()
    if clases_hoy:
        df_clases = pd.DataFrame(clases_hoy)
        st.dataframe(df_clases)
    else:
        st.info("No hay clases programadas para hoy.")
