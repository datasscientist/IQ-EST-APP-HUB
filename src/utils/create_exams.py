from openai import OpenAI
import pandas as pd
import math
import json

# Configura tu API key

def iniciar_cliente(api_key):

    client = OpenAI(api_key=api_key)

    return client

def generar_preguntas_por_bloques(client, tema_general: str, subtema: str, total_preguntas: int, preguntas_por_bloque: int = 25) -> list:
    """
    Genera `total_preguntas` en bloques utilizando un formato JSON estructurado.
    Cada bloque se solicita especificando un rango de números de pregunta.
    """
    todas_las_preguntas = []
    num_bloques = math.ceil(total_preguntas / preguntas_por_bloque)
    pregunta_inicial = 1

    for bloque in range(num_bloques):
        pregunta_final = min(pregunta_inicial + preguntas_por_bloque - 1, total_preguntas)

        prompt_bloque = f"""
Eres un profesor y experto en {tema_general}.
Estoy preparando un examen a manera de evaluación de mis alumnos. En particular, este examen abordará el subtema "{subtema}".
Genera las preguntas desde la #{pregunta_inicial} hasta la #{pregunta_final}.

Instrucciones:
1. Las preguntas deben enfocarse en el subtema "{subtema}".
2. No repitas preguntas de bloques anteriores.
3. Devuelve la respuesta únicamente en formato JSON, con una lista llamada "preguntas". 
   Cada elemento de la lista debe ser un objeto con las propiedades "numero" y "texto".

Ejemplo del formato de salida:
{{
  "preguntas": [
    {{ "numero": {pregunta_inicial}, "texto": "Primera pregunta..." }},
    {{ "numero": {pregunta_inicial+1}, "texto": "Segunda pregunta..." }},
    ...
    {{ "numero": {pregunta_final}, "texto": "Última pregunta." }}
  ]
}}
"""
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Sigue cuidadosamente las instrucciones dadas."},
                    {"role": "user", "content": prompt_bloque}
                ],
                max_completion_tokens=16384,
                temperature=0.7
            )
        except Exception as e:
            print(f"Error en la llamada a la API: {e}")
            break

        texto_bloque = response.choices[0].message.content.strip()

        try:
            data = json.loads(texto_bloque)
            preguntas_bloque = data.get("preguntas", [])
            todas_las_preguntas.extend(preguntas_bloque)
        except json.JSONDecodeError as e:
            print(f"Error al parsear JSON: {e}")
            # Opcional: aquí se podría reintentar o guardar el error para depuración
            continue

        pregunta_inicial = pregunta_final + 1

    return todas_las_preguntas

def responder_pregunta(client, pregunta, tema, subtema, max_iter=3):
    """
    Recibe una pregunta y genera:
      1. La respuesta correcta.
      2. Tres opciones incorrectas pero plausibles.
      3. Una explicación detallada.
    La respuesta se devuelve en formato JSON.
    """
    prompt = f"""
Tu tarea es recibir la siguiente pregunta y generar:
1. La respuesta correcta.
2. Tres opciones incorrectas pero plausibles.
3. Una explicación detallada de por qué la respuesta correcta es la adecuada.
4. Procura que las cuatro respuestas de cada pregunta tengan aproximadamente la misma extensión entre sí.

Devuelve la respuesta únicamente en formato JSON con el siguiente formato:
{{
  "pregunta": "{pregunta}",
  "respuesta_correcta": "...",
  "opciones_incorrectas": ["...", "...", "..."],
  "explicacion": "..."
}}

Aquí tienes la pregunta a procesar: {pregunta}
"""
    respuesta_completa = ""
    iteracion = 0

    while iteracion < max_iter:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Eres un generador de problemas de {tema} especializado en {subtema}."},
                    {"role": "user", "content": prompt if not respuesta_completa else "Continúa la respuesta:"}
                ],
                max_completion_tokens=16384,
                temperature=0.7
            )
        except Exception as e:
            return f"Error en la llamada a la API: {e}"

        nueva_respuesta = response.choices[0].message.content.strip()
        respuesta_completa += " " + nueva_respuesta

        try:
            resultado = json.loads(respuesta_completa)
            if all(key in resultado for key in ["pregunta", "respuesta_correcta", "opciones_incorrectas", "explicacion"]):
                return resultado
        except json.JSONDecodeError:
            # Si no se puede parsear aún, se continua el bucle
            pass

        iteracion += 1

    return f"Error al generar la respuesta completa después de {max_iter} intentos."

def procesar_respuesta(respuesta):
    """
    Procesa la respuesta en formato JSON y la convierte en un DataFrame con columnas definidas.
    """
    try:
        if isinstance(respuesta, str):
            respuesta = json.loads(respuesta)
        columnas = ["Pregunta", "Respuesta correcta", "Opcion 1", "Opcion 2", "Opcion 3", "Explicacion"]
        if all(key in respuesta for key in ["pregunta", "respuesta_correcta", "opciones_incorrectas", "explicacion"]):
            data = [
                respuesta["pregunta"],
                respuesta["respuesta_correcta"],
                respuesta["opciones_incorrectas"][0] if len(respuesta["opciones_incorrectas"]) > 0 else "",
                respuesta["opciones_incorrectas"][1] if len(respuesta["opciones_incorrectas"]) > 1 else "",
                respuesta["opciones_incorrectas"][2] if len(respuesta["opciones_incorrectas"]) > 2 else "",
                respuesta["explicacion"]
            ]
            df = pd.DataFrame([data], columns=columnas)
            return df
        else:
            return None
    except Exception as e:
        print(f"Error al procesar la respuesta: {e}")
        return None
