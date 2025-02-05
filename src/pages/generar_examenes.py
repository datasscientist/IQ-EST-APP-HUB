import io
import zipfile
import streamlit as st
import pandas as pd
from src.utils.create_exams import generar_preguntas_por_bloques, responder_pregunta, procesar_respuesta, iniciar_cliente

def show():
    st.header("Generador de Exámenes con ChatGPT (o lógica propia)")

    with st.expander("¿Cómo usar esta herramienta?"):
        st.write("""
        1. Ingresa el tema general del examen (por ejemplo: Matemáticas).
        2. Indica cuántas preguntas quieres por cada subtema.
        3. Selecciona la dificultad.
        4. Sube un Excel con la columna llamada 'subtema' (una fila por cada subtema).
        5. Presiona "Generar Examen".
        6. Obtendrás un examen combinado con cada subtema.
        """)

    with st.form("form_examen"):
        st.subheader("Parámetros del Examen")
        col1, col2, col3 = st.columns(3)

        with col1:
            tema = st.text_input("Tema general del examen", value="Matemáticas")
            dificultad = st.selectbox("Dificultad", ["fácil", "medio", "difícil"])

        with col2:
            numero_preguntas = st.number_input(
                "Número de preguntas por subtema",
                min_value=1,
                max_value=100,
                value=5
            )
            api_key = st.text_input("Ingresa la API KEY de ChatGPT", value="Ingresa API KEY")

        with col3:
            subtemas_file = st.file_uploader(
                "Sube tu archivo Excel con la columna 'subtema'",
                type=["xlsx"]
            )

        generar = st.form_submit_button("Generar Examen")

    if generar:
        if subtemas_file is None:
            st.error("Por favor sube un archivo Excel con la columna 'subtema'.")
        else:
            with st.spinner("Generando el examen..."):
                df_subtemas = pd.read_excel(subtemas_file)
                
                if "subtema" not in df_subtemas.columns:
                    st.error("El archivo Excel no contiene una columna llamada 'subtema'.")
                else:
                    lista_subtemas = df_subtemas["subtema"].dropna().unique().tolist()
                    examenes_por_subtema = []
                    client = iniciar_cliente(api_key)

                    for subtema in lista_subtemas:
                        examen_del_subtema = pd.DataFrame()
                        preguntas_examen = generar_preguntas_por_bloques(
                            client, 
                            tema, 
                            subtema, 
                            numero_preguntas, 
                            preguntas_por_bloque=25
                        )

                        for pregunta in preguntas_examen:
                            pregunta_contestada = responder_pregunta(client, pregunta, tema, subtema)
                            pregunta_formato_df = procesar_respuesta(pregunta_contestada)
                            examen_del_subtema = pd.concat(
                                [examen_del_subtema, pregunta_formato_df],
                                ignore_index=True
                            )

                        examenes_por_subtema.append((subtema, examen_del_subtema))

            st.success("¡Examen generado con éxito!")

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for subtema, df_examen in examenes_por_subtema:
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                        df_examen.to_excel(writer, sheet_name="Sheet1", index=False)
                    excel_filename = f"Examen_Subtema_{subtema}.xlsx"
                    excel_filename = excel_filename.replace("/", "_").replace("\\", "_")
                    zf.writestr(excel_filename, excel_buffer.getvalue())

            zip_buffer.seek(0)
            st.download_button(
                label="Descargar Todos los Exámenes (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=f"Examenes_{tema}_{dificultad}.zip",
                mime="application/zip"
            )