import streamlit as st
import pandas as pd
import io
from modules.auth import get_connection
from datetime import date

def gestion_estudiantes():
    st.title("🧑‍🎓 Gestión de Estudiantes")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    seccion = st.radio("Selecciona una opción:", ["Registrar Estudiante", "Lista de Estudiantes", "Estudiante"], horizontal=True)

    if seccion == "Registrar Estudiante":
        st.subheader("➕ Registrar nuevo estudiante")
        cursor.execute("SELECT id, nombre FROM cursos")
        cursos = cursor.fetchall()
        cursos_dict = {curso['nombre']: curso['id'] for curso in cursos}

        with st.form("form_estudiante"):
            nombre = st.text_input("Nombre completo")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")
            tutor_nombre = st.text_input("Nombre del tutor")
            tutor_correo = st.text_input("Correo del tutor")
            tutor_telefono = st.text_input("Teléfono del tutor")
            parentesco = st.selectbox("Parentesco", ["Padre", "Madre", "Tío/a", "Otro"])
            curso_seleccionado = st.selectbox("Curso", list(cursos_dict.keys()))
            submit = st.form_submit_button("Guardar")

            if submit:
                cursor.execute("""
                    INSERT INTO estudiantes (nombre, correo, telefono, tutor_nombre, tutor_correo, tutor_telefono, parentesco)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (nombre, correo, telefono, tutor_nombre, tutor_correo, tutor_telefono, parentesco))
                estudiante_id = cursor.lastrowid
                curso_id = cursos_dict[curso_seleccionado]
                cursor.execute("INSERT INTO estudiante_curso (estudiante_id, curso_id) VALUES (%s, %s)", (estudiante_id, cursos_dict[nuevo_curso]))) VALUES (%s, %s)", (estudiante_id, cursos_dict[nuevo_curso]))
                    conn.commit()
                    st.success("Datos actualizados correctamente")

                # Mostrar pagos y asistencia en columnas
                colp1, colp2 = st.columns(2)

                with colp1:
                    st.subheader("💳 Pagos")
                    cursor.execute("""
                        SELECT monto, fecha, fecha_vencimiento
                        FROM pagos
                        WHERE estudiante_id = %s
                        ORDER BY fecha DESC
                    """, (estudiante_id,))
                    pagos = cursor.fetchall()
                    if pagos:
                        df_pagos = pd.DataFrame(pagos)
                        st.dataframe(df_pagos)
                        prox = min(p['fecha_vencimiento'] for p in pagos if p['fecha_vencimiento'])
                        st.info(f"📆 Próximo vencimiento: {prox}")
                    else:
                        st.warning("Este estudiante no tiene pagos registrados.")

                with colp2:
                    st.subheader("📅 Asistencia")
                    cursor.execute("SELECT fecha, estado FROM asistencia WHERE estudiante_id = %s ORDER BY fecha DESC", (estudiante_id,))
                    asistencia = cursor.fetchall()
                    if asistencia:
                        df_asistencia = pd.DataFrame(asistencia)
                        st.dataframe(df_asistencia)
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df_asistencia.to_excel(writer, index=False)
                        st.download_button("⬇️ Descargar asistencia", data=output.getvalue(), file_name="asistencia_estudiante.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.info("No hay registros de asistencia para este estudiante.")

                colreg1, colreg2 = st.columns(2)
                with colreg1:
                    st.subheader("✏️ Registrar o actualizar asistencia")
                    cursor.execute("SELECT curso_id FROM estudiante_curso WHERE estudiante_id = %s LIMIT 1", (estudiante_id,))
                    curso_info = cursor.fetchone()
                    curso_id = curso_info['curso_id'] if curso_info else None
                    fecha_asistencia = st.date_input("Fecha de asistencia")
                    estado_asistencia = st.selectbox("Estado", ["presente", "ausente"])
                    if st.button("Guardar asistencia", key="guardar_asistencia"):
                        cursor.execute("SELECT * FROM asistencia WHERE estudiante_id = %s AND fecha = %s", (estudiante_id, fecha_asistencia))
                        existente = cursor.fetchone()
                        if existente:
                            cursor.execute("UPDATE asistencia SET estado = %s WHERE estudiante_id = %s AND fecha = %s",
                                           (estado_asistencia, estudiante_id, fecha_asistencia))
                        else:
                            cursor.execute("INSERT INTO asistencia (estudiante_id, curso_id, fecha, estado) VALUES (%s, %s, %s, %s)",
                                           (estudiante_id, curso_id, fecha_asistencia, estado_asistencia))
                        conn.commit()
                        st.rerun()

                with colreg2:
                    st.subheader("💳 Registrar pago individual")
                    monto = st.number_input("Monto", min_value=0.0, step=0.5, key="monto_pago")
                    fecha_pago = st.date_input("Fecha del pago", value=date.today(), key="fecha_pago")
                    fecha_ven = st.date_input("Fecha de vencimiento", key="fecha_ven")
                    if st.button("Guardar pago", key="guardar_pago"):
                        cursor.execute("INSERT INTO pagos (estudiante_id, monto, fecha, fecha_vencimiento) VALUES (%s, %s, %s, %s)",
                                       (estudiante_id, monto, fecha_pago, fecha_ven))
                        conn.commit()
                        st.rerun()
        else:
            st.info("No hay estudiantes registrados aún.")
