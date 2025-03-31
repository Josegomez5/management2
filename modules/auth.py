import streamlit as st
import mysql.connector
import hashlib

def get_connection():
    return mysql.connector.connect(
        host=st.secrets["db_host"],
        user=st.secrets["db_user"],
        password=st.secrets["db_password"],
        database=st.secrets["db_name"]
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    st.title("🔐 Iniciar Sesión")
    correo = st.text_input("Correo electrónico")
    password = st.text_input("Contraseña", type="password")
    rol = st.selectbox("Rol", ["admin", "profesor", "estudiante"])

    if st.button("Ingresar"):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT * FROM usuarios 
            WHERE correo = %s AND password = %s AND rol = %s
        """
        hashed = hash_password(password)
        cursor.execute(query, (correo, hashed, rol))
        user = cursor.fetchone()

        if user:
            st.session_state.autenticado = True
            st.session_state.user_id = user["id_usuario"]
            st.session_state.rol = user["rol"]
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
# módulo auth
