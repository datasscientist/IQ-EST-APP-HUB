import streamlit as st
from src.utils.change_questions_format import formatear_preguntas

def show():
    st.header("Formato Quizes TutorLMS - IQ-Est Academy")
    st.markdown(
        """
        Sube un archivo Excel que contenga las siguientes columnas:  
        **Pregunta**, **Respuesta Correcta**, **Opcion 1**, **Opcion 2**, **Opcion 3**, **Explicacion**.  
        Cada fila representará una pregunta con 4 opciones y una explicación sobre la respuesta correcta. 
        
        Nota: Este excel se puede generar en la app de **Formato Quizes** que se encuentra dentro del HUB.
        """
    )

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