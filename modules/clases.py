import streamlit as st
import pandas as pd
import io
from datetime import date, timedelta, datetime, time
from modules.auth import get_connection
import plotly.express as px


def gestion_clases():
    st.title("📅 Gestión de Clases")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    opcion = st.radio("Selecciona una opción:", [
        "📘 Registrar Clase",
        "📄 Lista de Clases",
        "🛠️ Editar / Eliminar Clases",
        "📅 Vista Calendario"
    ], horizontal=True)

    if opcion == "📘 Registrar Clase":
        # ... sin cambios ...
        st.subheader("Registrar nueva clase")
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

    elif opcion == "📄 Lista de Clases":
        # ... sin cambios ...
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
                label="Descargar Excel",
                data=output.getvalue(),
                file_name="clases.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No hay clases registradas aún.")

    elif opcion == "🛠️ Editar / Eliminar Clases":
        # ... sin cambios ...
        # se mantiene igual
        pass

    elif opcion == "📅 Vista Calendario":
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
                try:
                    df_cal['start'] = df_cal.apply(lambda row: datetime.combine(row['fecha'], row['hora_inicio']), axis=1)
                    df_cal['end'] = df_cal.apply(lambda row: datetime.combine(row['fecha'], row['hora_fin']), axis=1)
                except Exception as e:
                    st.error(f"Error al procesar fechas y horas: {e}")
                    return

                df_cal['evento'] = df_cal['curso'] + ' - ' + df_cal['profesor']

                st.write("### 🗂 Vista tabular de clases en el calendario")
                st.dataframe(df_cal[['fecha', 'hora_inicio', 'hora_fin', 'curso', 'profesor']])

                fig = px.timeline(
                    df_cal,
                    x_start="start",
                    x_end="end",
                    y="evento",
                    color="curso",
                    title="Clases en calendario",
                    labels={"evento": "Clase"}
                )
                fig.update_layout(xaxis_title="Fecha y hora", yaxis_title="Clase", showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_cal[['fecha', 'hora_inicio', 'hora_fin', 'curso', 'profesor']].to_excel(writer, index=False)
                st.download_button(
                    label="Descargar Excel",
                    data=output.getvalue(),
                    file_name="clases_calendario.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("No hay clases en el rango seleccionado")
