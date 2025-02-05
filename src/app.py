import streamlit as st
from src.pages.login import login
from src.pages.formatear_quizes import show as show_formatear_quizes
from src.pages.generar_examenes import show as show_generar_examenes

def main():
    st.title("IQ-EST ACADEMY - APP HUB")
    tab1, tab2 = st.tabs(["Formato Quizes", "Generador de Exámenes"])

    with tab1:
        show_formatear_quizes()

    with tab2:
        show_generar_examenes()

def validacionUsuario():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        login()
    else:
        main()

if __name__ == "__main__":
    validacionUsuario()