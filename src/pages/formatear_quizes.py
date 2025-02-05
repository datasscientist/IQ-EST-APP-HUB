import streamlit as st
from src.utils.change_questions_format import formatear_preguntas

def show():
    st.header("Formato Quizes TutorLMS - IQ-Est Academy")
    st.markdown("Descarga el archivo de referencia: [ENTRADA](https://docs.google.com/spreadsheets/d/14U-2J-OVjT3GeBxU3oPvLOWD5Rz-1NhX/edit?usp=sharing&ouid=108171399223130798643&rtpof=true&sd=true)")

    uploaded_file = st.file_uploader("Sube el archivo de preguntas en formato Excel", type=["xlsx"])

    if uploaded_file is not None:
        df_output = formatear_preguntas(uploaded_file)
        st.write("Archivo formateado:")
        st.dataframe(df_output)

        st.download_button(
            label="Descargar archivo formateado",
            data=df_output.to_csv(index=False, header=False).encode('utf-8'),
            file_name='tutor-quiz-formateado.csv',
            mime='text/csv'
        )