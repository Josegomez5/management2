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
        # Código ya existente para registrar clase
        # [omitir aquí por brevedad]
        pass

    elif opcion == "📄 Lista de Clases":
        # ... sin cambios ...
        pass

    elif opcion == "🛠️ Editar / Eliminar Clases":
        # ... sin cambios ...
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

                df_cal['start'] = pd.to_datetime(df_cal['fecha'].astype(str) + ' ' + df_cal['hora_inicio'].astype(str))
                df_cal['end'] = pd.to_datetime(df_cal['fecha'].astype(str) + ' ' + df_cal['hora_fin'].astype(str))
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
