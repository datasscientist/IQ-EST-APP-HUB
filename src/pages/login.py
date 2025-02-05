import streamlit as st
import pandas as pd

# ==========
# EJEMPLO DE LOGIN BÁSICO
# ==========

def login():
    """
    Muestra un formulario de inicio de sesión y valida un usuario/contraseña de ejemplo.
    """
    st.title("Inicio de Sesión")

    # Campos para usuario y contraseña
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    # Botón para iniciar sesión
    if st.button("Iniciar sesión"):
        # Validación de ejemplo (usuario y password "quemados" en el código)
        if username == "root" and password == "root":
            # Si coincide, marcamos en session_state que está logueado
            st.session_state["logged_in"] = True
            # streamlit experimental_rerun "recarga" la aplicación, para que aparezcan las pestañas
            st.rerun()
        else:
            st.error("Credenciales incorrectas. Intenta de nuevo.")