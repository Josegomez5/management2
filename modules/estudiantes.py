import streamlit as st
import pandas as pd
import io
from modules.auth import get_connection

def gestion_estudiantes():
    st.title("🧑‍🎓 Gestión de Estudiantes")
    conn = get_connection()import streamlit as st
import pandas as pd
import io
from modules.auth import get_connection

def gestion_estudiantes():
    st.title("🧑‍🎓 Gestión de Estudiantes")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    seccion = st.radio("Selecciona una opción:", ["Registrar Estudiante", "Lista de Estudiantes", "Buscar Estudiante"], horizontal=True)

    if seccion == "Registrar Estudiante":
        st.subheader("➕ Registrar nuevo estudiante")

        # Obtener lista de cursos disponibles
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

    elif seccion == "Buscar Estudiante":
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
            busqueda = st.text_input("Escribe el nombre o correo del estudiante")
            filtrados = [e for e in estudiantes if busqueda.lower() in e['nombre'].lower() or busqueda.lower() in e['correo'].lower()]
            if filtrados:
                opciones = {f"{e['nombre']} ({e['correo']})": e['id'] for e in filtrados}
                seleccionado = st.selectbox("Selecciona un estudiante para ver su perfil:", list(opciones.keys()))
                estudiante_id = opciones[seleccionado]

                est = next(e for e in estudiantes if e['id'] == estudiante_id)
                st.subheader(f"📄 Perfil de {est['nombre']}")
                st.markdown(f"**Correo:** {est['correo']}")
                st.markdown(f"**Teléfono:** {est['telefono']}")
                st.markdown(f"**Curso(s):** {est['cursos']}")
                st.markdown("**👨‍👩‍👧 Tutor:**")
                st.markdown(f"- Nombre: {est['tutor_nombre']}")
                st.markdown(f"- Correo: {est['tutor_correo']}")
                st.markdown(f"- Teléfono: {est['tutor_telefono']}")
                st.markdown(f"- Parentesco: {est['parentesco']}")

                # Mostrar pagos
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
            elif busqueda:
                st.warning("No se encontraron estudiantes con ese término.")
        else:
            st.info("No hay estudiantes registrados aún.")
    cursor = conn.cursor(dictionary=True)

    seccion = st.radio("Selecciona una opción:", ["Registrar Estudiante", "Lista de Estudiantes", "Buscar Estudiante"], horizontal=True)

    if seccion == "Registrar Estudiante":
        st.subheader("➕ Registrar nuevo estudiante")

        # Obtener lista de cursos disponibles
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

    elif seccion in ["Lista de Estudiantes", "Buscar Estudiante"]:
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

            if seccion == "Lista de Estudiantes":
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

            st.subheader("🔍 Buscar estudiante")
            busqueda = st.text_input("Escribe el nombre o correo del estudiante")
            filtrados = [e for e in estudiantes if busqueda.lower() in e['nombre'].lower() or busqueda.lower() in e['correo'].lower()]
            if filtrados:
                opciones = {f"{e['nombre']} ({e['correo']})": e['id'] for e in filtrados}
                seleccionado = st.selectbox("Selecciona un estudiante para ver su perfil:", list(opciones.keys()))
                estudiante_id = opciones[seleccionado]

                est = next(e for e in estudiantes if e['id'] == estudiante_id)
                st.subheader(f"📄 Perfil de {est['nombre']}")
                st.markdown(f"**Correo:** {est['correo']}")
                st.markdown(f"**Teléfono:** {est['telefono']}")
                st.markdown(f"**Curso(s):** {est['cursos']}")
                st.markdown("**👨‍👩‍👧 Tutor:**")
                st.markdown(f"- Nombre: {est['tutor_nombre']}")
                st.markdown(f"- Correo: {est['tutor_correo']}")
                st.markdown(f"- Teléfono: {est['tutor_telefono']}")
                st.markdown(f"- Parentesco: {est['parentesco']}")

                # Mostrar pagos
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
            elif busqueda:
                st.warning("No se encontraron estudiantes con ese término.")
        else:
            st.info("No hay estudiantes registrados aún.")
