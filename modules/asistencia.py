import streamlit as st
import pandas as pd
from modules.auth import get_connection
from datetime import date

def gestion_asistencia():
    st.title("📋 Registro de Asistencia General")
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Selección de curso y fecha
    cursor.execute("SELECT id, nombre FROM cursos")
    cursos = cursor.fetchall()
    curso_dict = {curso['nombre']: curso['id'] for curso in cursos}
    curso_nombre = st.selectbox("Selecciona un curso", list(curso_dict.keys()))
    fecha = st.date_input("Fecha", value=date.today())
    curso_id = curso_dict[curso_nombre]

    # Obtener estudiantes del curso
    cursor.execute("""
        SELECT e.id, e.nombre FROM estudiantes e
        JOIN estudiante_curso ec ON e.id = ec.estudiante_id
        WHERE ec.curso_id = %s
    """, (curso_id,))
    estudiantes = cursor.fetchall()

    st.subheader("🧑‍🎓 Marcar asistencia")
    asistencia_dict = {}
    for est in estudiantes:
        asistencia_dict[est['id']] = st.checkbox(est['nombre'], value=True)

    if st.button("Guardar asistencia"):
        for est_id, presente in asistencia_dict.items():
            estado = 'presente' if presente else 'ausente'

            # Verificar si ya existe curso_id por seguridad
            cursor.execute("SELECT curso_id FROM estudiante_curso WHERE estudiante_id = %s LIMIT 1", (est_id,))
            curso_data = cursor.fetchone()
            curso_id_est = curso_data['curso_id'] if curso_data else None

            cursor.execute("""
                SELECT id FROM asistencia WHERE estudiante_id = %s AND fecha = %s
            """, (est_id, fecha))
            existe = cursor.fetchone()
            if existe:
                cursor.execute("UPDATE asistencia SET estado = %s WHERE id = %s", (estado, existe['id']))
            else:
                cursor.execute("INSERT INTO asistencia (estudiante_id, curso_id, fecha, estado) VALUES (%s, %s, %s, %s)",
                               (est_id, curso_id_est, fecha, estado))
        conn.commit()
        st.success("Asistencia guardada correctamente")
