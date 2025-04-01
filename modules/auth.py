
import streamlit as st

# Simulación de conexión a base de datos
def get_connection():
    return None  # No usada en este ejemplo simple

# Login simulado
def login():
    st.sidebar.title("Iniciar sesión")
    usuario = st.sidebar.text_input("Usuario")
    contrasena = st.sidebar.text_input("Contraseña", type="password")
    if st.sidebar.button("Ingresar"):
        if usuario == "admin" and contrasena == "admin":
            st.session_state["logueado"] = True
        else:
            st.error("Credenciales incorrectas")
    return st.session_state.get("logueado", False)
