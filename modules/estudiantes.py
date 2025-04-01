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

                st.markdown("---")
