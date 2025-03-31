...
                # Mostrar asistencia
                st.subheader("📅 Asistencia")
                cursor.execute("""
                    SELECT fecha, estado
                    FROM asistencia
                    WHERE estudiante_id = %s
                    ORDER BY fecha DESC
                """, (estudiante_id,))
                asistencia = cursor.fetchall()
                if asistencia:
                    df_asistencia = pd.DataFrame(asistencia)
                    st.dataframe(df_asistencia)
                else:
                    st.info("No hay registros de asistencia para este estudiante.")

                st.markdown("---")
                st.subheader("✏️ Registrar o actualizar asistencia")
                fecha_asistencia = st.date_input("Fecha de asistencia")
                estado_asistencia = st.selectbox("Estado", ["presente", "ausente"])
                if st.button("Guardar asistencia"):
                    # Verificar si ya existe asistencia en esa fecha
                    cursor.execute("SELECT * FROM asistencia WHERE estudiante_id = %s AND fecha = %s", (estudiante_id, fecha_asistencia))
                    existente = cursor.fetchone()
                    if existente:
                        cursor.execute("UPDATE asistencia SET estado = %s WHERE estudiante_id = %s AND fecha = %s",
                                       (estado_asistencia, estudiante_id, fecha_asistencia))
                        st.success("Asistencia actualizada correctamente")
                    else:
                        cursor.execute("INSERT INTO asistencia (estudiante_id, curso_id, fecha, estado) VALUES (%s, %s, %s, %s)",
                                       (estudiante_id, curso_id, fecha_asistencia, estado_asistencia))
                        st.success("Asistencia registrada correctamente")
                    conn.commit()
