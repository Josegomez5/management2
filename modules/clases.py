import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta, datetime
from modules.auth import get_connection

def gestion_clases():
    st.title("📅 Gestión de Clases")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    opcion = st.radio("Selecciona una opción:", [
        "Registrar Clase",
        "Lista de Clases",
        "🛠 Editar / Eliminar Clases",
        "📆 Vista Calendario"
    ], horizontal=True)

    if opcion == "Registrar Clase":
        st.subheader("➕ Nueva Clase")
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
        hora_inicio = st.time_input("Hora de inicio")
        hora_fin = st.time_input("Hora de fin")

        if st.button("Guardar clase"):
            cursor.execute(
                "INSERT INTO clases (curso_id, profesor_id, fecha, hora_inicio, hora_fin) VALUES (%s, %s, %s, %s, %s)",
                (curso_id, profesor_id, fecha, hora_inicio, hora_fin)
            )
            conn.commit()
            st.success("Clase registrada exitosamente")

    elif opcion == "Lista de Clases":
        st.subheader("📋 Clases Programadas")
        cursor.execute("""
            SELECT c.nombre as curso, p.nombre as profesor, cl.fecha, cl.hora_inicio, cl.hora_fin
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            ORDER BY cl.fecha DESC, cl.hora_inicio
        """)
        clases = cursor.fetchall()

        if clases:
            df = pd.DataFrame(clases)
            st.dataframe(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="⬇️ Descargar Excel",
                data=output.getvalue(),
                file_name="clases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay clases registradas aún.")

    elif opcion == "🛠 Editar / Eliminar Clases":
        st.subheader("🛠 Editar o Eliminar Clase")
        cursor.execute("""
            SELECT cl.id, c.nombre as curso, p.nombre as profesor, cl.fecha, cl.hora_inicio, cl.hora_fin
            FROM clases cl
            JOIN cursos c ON cl.curso_id = c.id
            JOIN profesores p ON cl.profesor_id = p.id
            ORDER BY cl.fecha DESC
        """)
        clases = cursor.fetchall()

        if clases:
            df = pd.DataFrame(clases)
            df["label"] = df.apply(lambda row: f"{row['fecha']} - {row['curso']} ({row['profesor']})", axis=1)
            selected = st.selectbox("Selecciona una clase para editar/eliminar", df["label"])
            clase_id = int(df[df["label"] == selected]["id"].values[0])

            cursor.execute("SELECT * FROM clases WHERE id = %s", (clase_id,))
            clase = cursor.fetchone()

            cursor.execute("SELECT id, nombre FROM cursos")
            cursos = cursor.fetchall()
            cursos_dict = {c["nombre"]: c["id"] for c in cursos}
            curso_edit = st.selectbox("Curso", list(cursos_dict.keys()), index=list(cursos_dict.values()).index(clase["curso_id"]))

            cursor.execute("SELECT id, nombre FROM profesores")
            profesores = cursor.fetchall()
            profesores_dict = {p["nombre"]: p["id"] for p in profesores}
            profesor_edit = st.selectbox("Profesor", list(profesores_dict.keys()), index=list(profesores_dict.values()).index(clase["profesor_id"]))

            fecha_edit = st.date_input("Fecha", value=clase["fecha"])
            hora_inicio_edit = st.time_input("Hora inicio", value=datetime.strptime(str(clase["hora_inicio"]), "%H:%M:%S").time())
            hora_fin_edit = st.time_input("Hora fin", value=datetime.strptime(str(clase["hora_fin"]), "%H:%M:%S").time())

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Actualizar clase"):
                    cursor.execute("""
                        UPDATE clases SET curso_id=%s, profesor_id=%s, fecha=%s, hora_inicio=%s, hora_fin=%s WHERE id=%s
                    """, (cursos_dict[curso_edit], profesores_dict[profesor_edit], fecha_edit, hora_inicio_edit, hora_fin_edit, clase_id))
                    conn.commit()
                    st.success("Clase actualizada")
                    st.experimental_rerun()
            with col2:
                if st.button("🗑 Eliminar clase"):
                    cursor.execute("DELETE FROM clases WHERE id = %s", (clase_id,))
                    conn.commit()
                    st.warning("Clase eliminada")
                    st.experimental_rerun()
        else:
            st.info("No hay clases disponibles para editar o eliminar.")

    elif opcion == "📆 Vista Calendario":
        st.subheader("📅 Clases por Calendario")
        fecha_inicio = st.date_input("Desde", date.today())
        fecha_fin = st.date_input("Hasta", date.today() + timedelta(days=7))

        if fecha_inicio > fecha_fin:
            st.warning("La fecha de inicio no puede ser posterior a la fecha de fin")
        else:
            cursor.execute("""
                SELECT cl.fecha, cl.hora_inicio, cl.hora_fin, c.nombre as curso, p.nombre as profesor
                FROM clases cl
                JOIN cursos c ON cl.curso_id = c.id
                JOIN profesores p ON cl.profesor_id = p.id
                WHERE cl.fecha BETWEEN %s AND %s
                ORDER BY cl.fecha, cl.hora_inicio
            """, (fecha_inicio, fecha_fin))
            clases_rango = cursor.fetchall()

            if clases_rango:
                df_cal = pd.DataFrame(clases_rango)
                st.write("📋 Tipos de datos:")
                st.write(df_cal.dtypes)
                st.write(df_cal.head())
                st.dataframe(df_cal)

                # Visualización avanzada tipo calendario
                import plotly.express as px
                df_cal['start'] = df_cal.apply(lambda row: datetime.combine(pd.to_datetime(row['fecha']).date(), row['hora_inicio'] if isinstance(row['hora_inicio'], datetime.time) else pd.to_datetime(row['hora_inicio']).time()), axis=1)
                df_cal['end'] = df_cal.apply(lambda row: datetime.combine(pd.to_datetime(row['fecha']).date(), row['hora_fin'] if isinstance(row['hora_fin'], datetime.time) else pd.to_datetime(row['hora_fin']).time()), axis=1)
                df_cal['titulo'] = df_cal['curso'] + ' - ' + df_cal['profesor']

                fig = px.timeline(df_cal, x_start='start', x_end='end', y='titulo', color='curso')
                fig.update_layout(title="🗓 Clases por calendario (timeline)", xaxis_title="Hora", yaxis_title="Clase", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay clases en el rango seleccionado")
