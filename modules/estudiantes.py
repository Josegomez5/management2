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
                cursor.execute("INSERT INTO estudiante_curso (estudiante_id, curso_id) VALUES (%s, %s)", (estudiante_id, curso_id))
                conn.commit()
                st.success("Estudiante registrado exitosamente")

    elif seccion == "Lista de Estudiantes":
        st.subheader("📋 Lista de estudiantes")
        cursor.execute("""
            SELECT e.id, e.nombre, e.correo, e.telefono, e.tutor_nombre, e.tutor_correo, e.tutor_telefono, e.parentesco,
                   GROUP_CONCAT(c.nombre SEPARATOR ', ') AS cursos
            FROM estudiantes e
            LEFT JOIN estudiante_curso ec ON e.id = ec.estudiante_id
            LEFT JOIN cursos c ON ec.curso_id = c.id
            GROUP BY e.id
        """)
        estudiantes = cursor.fetchall()

        if estudiantes:
            df = pd.DataFrame(estudiantes)
            st.dataframe(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=output.getvalue(),
                file_name="estudiantes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
        st.info("No hay estudiantes registrados aún.")

    # Registro general de pagos
    st.markdown("---")
    st.subheader("💸 Registrar pago de cualquier estudiante")
    cursor.execute("SELECT id, nombre FROM estudiantes ORDER BY nombre")
    est_pagables = cursor.fetchall()
    if est_pagables:
        est_nombres = {f"{e['nombre']} (ID {e['id']})": e['id'] for e in est_pagables}
        with st.form("form_pago_general"):
            estudiante_sel = st.selectbox("Selecciona estudiante", list(est_nombres.keys()))
            monto_pago = st.number_input("Monto del pago", min_value=0.0, step=0.5)
            fecha_pago = st.date_input("Fecha del pago", value=date.today())
            fecha_ven = st.date_input("Fecha de vencimiento")
            enviar_pago = st.form_submit_button("Registrar pago")
            if enviar_pago:
                cursor.execute("INSERT INTO pagos (estudiante_id, monto, fecha, fecha_vencimiento) VALUES (%s, %s, %s, %s)",
                               (est_nombres[estudiante_sel], monto_pago, fecha_pago, fecha_ven))
                conn.commit()
                st.rerun()

    elif seccion == "Estudiante":
        st.subheader("🔍 Buscar estudiante")
        cursor.execute("""
            SELECT e.id, e.nombre, e.correo, e.telefono, e.tutor_nombre, e.tutor_correo, e.tutor_telefono, e.parentesco,
                   GROUP_CONCAT(c.nombre SEPARATOR ', ') AS cursos
            FROM estudiantes e
            LEFT JOIN estudiante_curso ec ON e.id = ec.estudiante_id
            LEFT JOIN cursos c ON ec.curso_id = c.id
            GROUP BY e.id
        """)
        estudiantes = cursor.fetchall()

        if estudiantes:
            busqueda = st.text_input("Buscar por nombre o correo")
            opciones = {f"{e['nombre']} ({e['correo']})": e['id'] for e in estudiantes}

            if busqueda:
                opciones = {k: v for k, v in opciones.items() if busqueda.lower() in k.lower()}

            seleccionado = st.selectbox("Selecciona un estudiante:", ["-- Seleccionar --"] + list(opciones.keys()))

            if seleccionado != "-- Seleccionar --":
                estudiante_id = opciones[seleccionado]
                est = next(e for e in estudiantes if e['id'] == estudiante_id)

                st.subheader(f"📄 Perfil de {est['nombre']}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"**Correo:** {est['correo']}")
                    st.markdown(f"**Teléfono:** {est['telefono']}")
                    st.markdown(f"**Curso(s):** {est['cursos']}")
                    st.markdown("**👨‍👩‍👧 Tutor:**")
                    st.markdown(f"- Nombre: {est['tutor_nombre']}")
                    st.markdown(f"- Correo: {est['tutor_correo']}")
                    st.markdown(f"- Teléfono: {est['tutor_telefono']}")
                    st.markdown(f"- Parentesco: {est['parentesco']}")

                with col2:
                    st.markdown("### ✏️ Editar datos")

                with col2.form("editar_estudiante"):
                    nuevo_nombre = st.text_input("Nombre completo", value=est['nombre'])
                    nuevo_correo = st.text_input("Correo electrónico", value=est['correo'])
                    nuevo_telefono = st.text_input("Teléfono", value=est['telefono'])
                    nuevo_tutor = st.text_input("Nombre del tutor", value=est['tutor_nombre'])
                    nuevo_tutor_correo = st.text_input("Correo del tutor", value=est['tutor_correo'])
                    nuevo_tutor_tel = st.text_input("Teléfono del tutor", value=est['tutor_telefono'])
                    nuevo_parentesco = st.selectbox("Parentesco", ["Padre", "Madre", "Tío/a", "Otro"], index=["Padre", "Madre", "Tío/a", "Otro"].index(est['parentesco']))

                    cursor.execute("SELECT id, nombre FROM cursos")
                    cursos_all = cursor.fetchall()
                    cursos_dict = {c['nombre']: c['id'] for c in cursos_all}
                    cursor.execute("SELECT curso_id FROM estudiante_curso WHERE estudiante_id = %s LIMIT 1", (estudiante_id,))
                    actual_curso_id = cursor.fetchone()
                    actual_curso_nombre = next((k for k, v in cursos_dict.items() if v == actual_curso_id['curso_id']), None)
                    nuevo_curso = st.selectbox("Curso", list(cursos_dict.keys()), index=list(cursos_dict.keys()).index(actual_curso_nombre) if actual_curso_nombre else 0)

                    if st.form_submit_button("Actualizar datos"):
                        cursor.execute("""
                            UPDATE estudiantes SET nombre=%s, correo=%s, telefono=%s,
                            tutor_nombre=%s, tutor_correo=%s, tutor_telefono=%s, parentesco=%s
                            WHERE id=%s
                        """, (nuevo_nombre, nuevo_correo, nuevo_telefono, nuevo_tutor, nuevo_tutor_correo, nuevo_tutor_tel, nuevo_parentesco, estudiante_id))
                        cursor.execute("DELETE FROM estudiante_curso WHERE estudiante_id = %s", (estudiante_id,))
                        cursor.execute("INSERT INTO estudiante_curso (estudiante_id, curso_id) VALUES (%s, %s)", (estudiante_id, cursos_dict[nuevo_curso]))
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

                        st.download_button(
                            label="⬇️ Descargar asistencia",
                            data=output.getvalue(),
                            file_name="asistencia_estudiante.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.info("No hay registros de asistencia para este estudiante.")

                st.markdown("---")
                colreg1, colreg2 = st.columns(2)
                with colreg1:
                    st.subheader("✏️ Registrar o actualizar asistencia")
                fecha_asistencia = st.date_input("Fecha de asistencia")
                estado_asistencia = st.selectbox("Estado", ["presente", "ausente"])

                # Obtener curso_id para el estudiante
                cursor.execute("SELECT curso_id FROM estudiante_curso WHERE estudiante_id = %s LIMIT 1", (estudiante_id,))
                curso_info = cursor.fetchone()
                curso_id = curso_info['curso_id'] if curso_info else None

                                                if st.button("Guardar asistencia", key="asistencia_btn"):
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
        else:
            st.info("No hay estudiantes registrados aún.")
