import pandas as pd

def formatear_preguntas(input_file):
    """
    Esta función recibe un archivo de Excel con preguntas de opción múltiple
    y lo convierte en un DataFrame con el formato adecuado para TutorLMS.
    
    Parámetros:
    -----------
    input_file: archivo subido (tipo Excel) con las columnas:
                'PREGUNTA', 'DESCRIPCIÓN DE LA PREGUNTA', 'EXPLICACION', 
                'OPCION CORRECTA', 'OPCION INCORRECTA' (y variaciones .1, .2, etc.)
    
    Retorna:
    --------
    df_output: DataFrame de pandas con el formato deseado.
    """
    
    # 1. Leemos las preguntas desde el archivo de entrada
    preguntas = pd.read_excel(input_file)

    # 2. Creamos una lista para almacenar las filas formateadas
    formatted_data = []

    # 3. Añadimos la fila de encabezado fija para TutorLMS
    header = ["settings", "TÍTULO DE LA LECCIÓN", "RESUMEN DE LA LECCIÓN", 0, "minutes", "", 0, 80, 10, "", "", "rand", 200]
    formatted_data.append(header)

    # 4. Iteramos sobre cada pregunta en el DataFrame
    for idx, row in preguntas.iterrows():
        # Creamos la fila de la "pregunta"
        question_row = [
            "question",
            row['PREGUNTA'],
            "<p>" + (row['DESCRIPCIÓN DE LA PREGUNTA'] if isinstance(row['DESCRIPCIÓN DE LA PREGUNTA'], str) and row['DESCRIPCIÓN DE LA PREGUNTA'] else "") + "</p>",
            "single_choice",
            1,
            idx + 1,
            "",
            1,
            "",
            "<p>" + (row['EXPLICACION'] if isinstance(row['EXPLICACION'], str) and row['EXPLICACION'] else "") + "</p>"
        ]
        formatted_data.append(question_row)

        # Creamos las filas de respuestas (4 respuestas por pregunta)
        for j in range(4):
            # Nota: la columna 'OPCION INCORRECTA' podría estar en 'OPCION INCORRECTA', 'OPCION INCORRECTA.1', etc.
            # Ajustamos lógicamente el nombre de la columna dependiendo de j
            if j == 0:
                respuesta_texto = row['OPCION CORRECTA']
            else:
                # Para j=1 => 'OPCION INCORRECTA'
                # Para j=2 => 'OPCION INCORRECTA.1'
                # Para j=3 => 'OPCION INCORRECTA.2'
                col_incorrecta = 'OPCION INCORRECTA' + (f'.{j-1}' if j > 1 else '')
                respuesta_texto = row[col_incorrecta]

            answer_row = [
                "answer",
                respuesta_texto,
                "text",
                1 if j == 0 else "",  # Asumimos que la primera es la correcta
                0,
                "",
                j + 1,
                "",
                "",
                "",
                "",
                "",
                ""
            ]
            formatted_data.append(answer_row)

    # 5. Convertimos la lista a DataFrame
    df_output = pd.DataFrame(formatted_data)

    return df_output