import streamlit as st
import pandas as pd
from modules.auth import get_connection
from datetime import date
import io

def gestion_pagos():
    st.title("💰 Gestión de Pagos")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Registro de nuevo pago
    st.subheader("➕ Registrar pago")
    cursor.execute("SELECT id, nombre FROM estudiantes ORDER BY nombre")
    estudiantes = cursor.fetchall()

    if estudiantes:
        opciones = {f"{e['nombre']} (ID {e['id']})": e['id'] for e in estudiantes}
        with st.form("form_pago"):
            estudiante_sel = st.selectbox("Selecciona estudiante", list(opciones.keys()))
            monto = st.number_input("Monto", min_value=0.0, step=0.5)
            fecha_pago = st.date_input("Fecha del pago", value=date.today())
            fecha_vencimiento = st.date_input("Fecha de vencimiento")
            registrar = st.form_submit_button("Guardar pago")
            if registrar:
                cursor.execute("INSERT INTO pagos (estudiante_id, monto, fecha, fecha_vencimiento) VALUES (%s, %s, %s, %s)",
                               (opciones[estudiante_sel], monto, fecha_pago, fecha_vencimiento))
                conn.commit()
                st.rerun()

    st.markdown("---")
    st.subheader("📋 Pagos registrados")
    cursor.execute("""
        SELECT p.id, e.nombre AS estudiante, p.monto, p.fecha, p.fecha_vencimiento
        FROM pagos p
        JOIN estudiantes e ON p.estudiante_id = e.id
        ORDER BY p.fecha DESC
    """)
    pagos = cursor.fetchall()
    if pagos:
        df = pd.DataFrame(pagos)
        st.dataframe(df)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        st.download_button("⬇️ Descargar Excel", data=output.getvalue(), file_name="pagos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No hay pagos registrados aún.")
