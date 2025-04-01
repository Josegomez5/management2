import streamlit as st
import pandas as pd
from modules.auth import get_connection

def mostrar_dashboard():
    st.title("📊 Panel de Control")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Número total de estudiantes activos
    cursor.execute("SELECT COUNT(*) as total FROM estudiantes")
    total_estudiantes = cursor.fetchone()["total"]

    # Total pagado este mes
    cursor.execute("""
        SELECT SUM(monto) as total_pagado 
        FROM pagos 
        WHERE MONTH(fecha) = MONTH(CURRENT_DATE()) AND YEAR(fecha) = YEAR(CURRENT_DATE())
    """)
    total_pagado = cursor.fetchone()["total_pagado"] or 0

    # Próximos vencimientos
    cursor.execute("""
        SELECT e.nombre, p.fecha_vencimiento 
        FROM pagos p 
        JOIN estudiantes e ON e.id = p.estudiante_id 
        WHERE p.fecha_vencimiento >= CURDATE()
        ORDER BY p.fecha_vencimiento ASC
        LIMIT 5
    """)
    vencimientos = cursor.fetchall()

    # Alerta de clases restantes
    cursor.execute("SELECT id, nombre FROM estudiantes")
    estudiantes = cursor.fetchall()
    alertas = []

    for est in estudiantes:
        cursor.execute("SELECT SUM(clases_pagadas) as pagadas FROM pagos WHERE estudiante_id = %s", (est["id"],))
        pagadas = cursor.fetchone()["pagadas"] or 0

        cursor.execute("SELECT COUNT(*) as asistidas FROM asistencia WHERE estudiante_id = %s AND estado = 'presente'", (est["id"],))
        asistidas = cursor.fetchone()["asistidas"]

        restantes = pagadas - asistidas
        if restantes == 1:
            alertas.append({"nombre": est["nombre"], "estado": "⚠️ 1 clase restante"})
        elif restantes <= 0:
            alertas.append({"nombre": est["nombre"], "estado": "🚨 Sin clases disponibles"})

    # Mostrar tarjetas resumen
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎓 Estudiantes activos", total_estudiantes)
    with col2:
        st.metric("💰 Pagado este mes", f"${total_pagado:.2f}")

    st.markdown("---")
    st.subheader("📆 Próximos vencimientos de pago")
    if vencimientos:
        df_vencimientos = pd.DataFrame(vencimientos)
        st.table(df_vencimientos)
    else:
        st.info("No hay vencimientos próximos registrados")

    st.markdown("---")
    st.subheader("🔔 Alertas de clases")
    if alertas:
        df_alertas = pd.DataFrame(alertas)
        st.table(df_alertas)
    else:
        st.success("Todos los estudiantes tienen clases suficientes")
