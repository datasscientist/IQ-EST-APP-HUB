from openai import OpenAI
import pandas as pd
import math

# Configura tu API key

def iniciar_cliente(api_key):

    client = OpenAI(api_key=api_key)

    return client

def generar_preguntas_por_bloques(client, tema_general: str, subtema: str, total_preguntas: int, preguntas_por_bloque: int = 25) -> list:
    """
    Genera `total_preguntas` preguntas en varios bloques (chunks) de
    tamaño `preguntas_por_bloque`, para evitar exceder el límite de tokens.
    
    Retorna una lista de strings, donde cada elemento es una pregunta.
    """

    todas_las_preguntas = []
    
    # Cálculo de cuántas iteraciones (bloques) necesitamos
    num_bloques = math.ceil(total_preguntas / preguntas_por_bloque)
    
    # Iniciamos un contador de preguntas
    pregunta_inicial = 1
    
    for bloque in range(num_bloques):
        # Determinamos la pregunta final de este bloque
        pregunta_final = min(pregunta_inicial + preguntas_por_bloque - 1, total_preguntas)
        
        # Construimos el prompt para este bloque
        prompt_bloque = f"""
Eres un profesor y experto en {tema_general}.
Necesito que generes preguntas para el subtema "{subtema}".
Ya se han generado preguntas previas (o ninguna, si es la primera vez), ahora necesito específicamente
las preguntas desde la #{pregunta_inicial} hasta la #{pregunta_final}.

Instrucciones específicas:
1. Todas las preguntas deben estar enfocadas en el subtema "{subtema}".
2. No repitas preguntas anteriores.
3. Solo escribe las preguntas numeradas del {pregunta_inicial} al {pregunta_final}.
4. No incluyas introducciones, explicaciones adicionales o respuestas. Solo las preguntas.

Ejemplo de formato:
{pregunta_inicial}) Primera pregunta...
{pregunta_inicial+1}) Segunda pregunta...
...
{pregunta_final}) Última pregunta.

Tema general: {tema_general}
Subtema: {subtema}
Rango de preguntas: {pregunta_inicial} - {pregunta_final}
""".strip()
        
        # Llamada al modelo
        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content":"Sigue cuidadosamente las instrucciones dadas."},
                    {"role": "user", "content": prompt_bloque}
                ],
                max_tokens=2000,
                temperature=0.7
            )
        
        # Extraer el texto del modelo
        texto_bloque = response.choices[0].message.content.strip()
        
        # Podemos dividir el texto en líneas y filtrar solo las que parezcan preguntas
        # Esto depende de cómo regresa el modelo el output. 
        # Por ejemplo, si el modelo sigue el formato "1) ...", "2) ...", etc.
        
        lineas = texto_bloque.split("\n")
        
        # Filtramos las líneas vacías y las limpiamos
        lineas_limpias = [l.strip() for l in lineas if l.strip() != ""]
        
        # Agregamos todas esas preguntas a la lista global
        todas_las_preguntas.extend(lineas_limpias)
        
        # Actualizamos para la siguiente iteración
        pregunta_inicial = pregunta_final + 1
    
    return todas_las_preguntas

def responder_pregunta(client, pregunta, tema, subtema):
    prompt = f"""
    Tu tarea es recibir una pregunta de {subtema} y generar:
    1. La respuesta correcta.
    2. Tres opciones incorrectas pero plausibles.
    3. Una explicación detallada de por qué la respuesta correcta es la adecuada.

    Formato de salida (usa `|` como separador):
    Pregunta | Respuesta correcta | Opción 1 | Opción 2 | Opción 3 | Explicación

    Aquí tienes una pregunta para procesar: {pregunta}
    """


    try:
        respuesta_completa = ""
        continuar = True

        # Primera solicitud a la API
        while continuar:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Eres un generador de problemas de {tema} especializado en {subtema}."},
                    {"role": "user", "content": prompt if not respuesta_completa else "Continúa la respuesta:"}
                ],
                max_tokens=500,
                temperature=0.7
            )

            nueva_respuesta = response.choices[0].message.content.strip()
            respuesta_completa += nueva_respuesta
            continuar = nueva_respuesta.endswith("...")

        return respuesta_completa

    except Exception as e:
        return f"Error al generar la respuesta: {e}"

def procesar_respuesta(respuesta):
    try:
        elementos = [x.strip() for x in respuesta.split('|')]
        if len(elementos) != 6:
            return None
        columnas = ["Pregunta", "Respuesta correcta", "Opción 1", "Opción 2", "Opción 3", "Explicación"]
        df = pd.DataFrame([elementos], columns=columnas)
        return df
    except Exception as e:
        print(f"Error al procesar la respuesta: {e}")
        return None
