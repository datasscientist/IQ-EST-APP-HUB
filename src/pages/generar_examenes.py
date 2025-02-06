import io 
import streamlit as st
import pandas as pd
from src.utils.create_exams import iniciar_cliente, generar_preguntas_por_bloques, responder_pregunta

def show():
    st.header("Generador de Exámenes Completos con IA")
    st.markdown(
        """
        Sube un archivo Excel que contenga las siguientes columnas:  
        **Tema General**, **Sub Tema**, **Preguntas por Subtema**.  
        Cada fila representará un subtema para el cual se generarán preguntas, respuestas y explicaciones.
        """
    )
    
    # Entrada: archivo Excel y API Key
    uploaded_file = st.file_uploader("Sube el archivo Excel", type=["xlsx"])
    api_key = st.text_input("API Key de OpenAI", type="password")
    
    if uploaded_file and api_key:
        # Leer el archivo Excel
        try:
            df_input = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return
        
        # Validar que se encuentren las columnas requeridas
        required_columns = ["Tema General", "Sub Tema", "Preguntas por Subtema"]
        if not all(col in df_input.columns for col in required_columns):
            st.error(f"El archivo debe contener las columnas: {', '.join(required_columns)}")
            return
        
        # Inicializar el cliente de OpenAI
        try:
            client = iniciar_cliente(api_key)
        except Exception as e:
            st.error(f"Error al iniciar el cliente de OpenAI: {e}")
            return
        
        # Lista para almacenar los resultados finales
        resultados = []
        
        total_rows = len(df_input)
        progress_bar = st.progress(0)
        
        # Placeholders para mensajes de estado
        message_placeholder = st.empty()
        message_placeholder2 = st.empty()

        # Recorrer cada fila del Excel
        for idx, row in df_input.iterrows():
            tema_general = row["Tema General"]
            subtema = row["Sub Tema"]
            try:
                total_preguntas = int(row["Preguntas por Subtema"])
            except Exception as e:
                st.error(f"Error en la conversión de 'Preguntas por Subtema' en la fila {idx+1}: {e}")
                continue

            message_placeholder.write(
                f"**Generando preguntas para:** *{subtema}* (Tema: {tema_general}) con {total_preguntas} preguntas."
            )
            
            # Generar las preguntas para este subtema
            try:
                preguntas = generar_preguntas_por_bloques(
                    client, tema_general, subtema, total_preguntas, preguntas_por_bloque=total_preguntas
                )
            except Exception as e:
                st.error(f"Error generando preguntas para el subtema {subtema}: {e}")
                continue

            if not preguntas:
                st.error(f"No se generaron preguntas para el subtema: {subtema}")
                continue
            
            # Procesar cada pregunta generada
            for pregunta_dict in preguntas:
                numero = pregunta_dict.get("numero", "")
                pregunta_texto = pregunta_dict.get("texto", "")
                message_placeholder2.write(f"Procesando pregunta #{numero}: {pregunta_texto}")
                
                try:
                    respuesta_resultado = responder_pregunta(client, pregunta_texto, tema_general, subtema)
                except Exception as e:
                    respuesta_resultado = f"Error en la respuesta: {e}"
                
                # Verificar que la respuesta sea un diccionario con la estructura esperada
                if isinstance(respuesta_resultado, dict):
                    respuesta_correcta = respuesta_resultado.get("respuesta_correcta", "")
                    opciones_incorrectas = respuesta_resultado.get("opciones_incorrectas", [])
                    opcion1 = opciones_incorrectas[0] if len(opciones_incorrectas) > 0 else ""
                    opcion2 = opciones_incorrectas[1] if len(opciones_incorrectas) > 1 else ""
                    opcion3 = opciones_incorrectas[2] if len(opciones_incorrectas) > 2 else ""
                    explicacion = respuesta_resultado.get("explicacion", "")
                else:
                    respuesta_correcta = "Error"
                    opcion1 = ""
                    opcion2 = ""
                    opcion3 = ""
                    explicacion = str(respuesta_resultado)
                
                # Almacenar la información obtenida
                resultados.append({
                    "Tema General": tema_general,
                    "Sub Tema": subtema,
                    "Numero": numero,
                    "Pregunta": pregunta_texto,
                    "Respuesta Correcta": respuesta_correcta,
                    "Opcion 1": opcion1,
                    "Opcion 2": opcion2,
                    "Opcion 3": opcion3,
                    "Explicacion": explicacion
                })
            
            # Actualizar el progreso de acuerdo a la fila procesada
            progress_bar.progress((idx + 1) / total_rows)
        
        # Convertir los resultados en DataFrame y mostrarlos
        if resultados:
            df_resultados = pd.DataFrame(resultados)
            st.success("Exámenes generados exitosamente.")
            st.dataframe(df_resultados)
            
            # Crear un buffer en memoria para el archivo Excel
            output = io.BytesIO()
            # Guardar el DataFrame en el buffer usando to_excel. Se puede especificar engine si es necesario (por ejemplo, 'openpyxl')
            df_resultados.to_excel(output, index=False, engine='openpyxl')
            # Es importante volver al inicio del buffer
            output.seek(0)
            
            st.download_button(
                label="Descargar exámenes completos",
                data=output,
                file_name="examenes_completos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No se generaron exámenes.")
