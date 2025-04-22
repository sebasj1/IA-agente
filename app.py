# app.py

from flask import Flask, render_template, request
from data import get_fechas_materia, get_correlativas
from openai import OpenAI
import os
import json

# Seteá tu API Key de OpenAI
# client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
client = OpenAI(
    base_url="http://pcwindows:1234/v1",  # tu servidor local
    api_key="not-needed"  # LM Studio no valida el token, pero lo requiere
)

app = Flask(__name__)

# Definición de las funciones como tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_fechas_materia",
            "description": "Devuelve las fechas de examen final para una materia",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_materia": {
                        "type": "string",
                        "description": "Nombre de la materia, como 'Física I'"
                    }
                },
                "required": ["nombre_materia"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_correlativas",
            "description": "Devuelve los requisitos y correlativas para una materia",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_materia": {
                        "type": "string",
                        "description": "Nombre de la materia, como 'Química'"
                    }
                },
                "required": ["nombre_materia"]
            }
        }
    }
]

# Mapeo real de las funciones
available_functions = {
    "get_fechas_materia": get_fechas_materia,
    "get_correlativas": get_correlativas
}

# Datos de ejemplo para materias aprobadas
materias_aprobadas = ["Matemática I"]
materias_regularizadas = ["Física I"]

@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""
    if request.method == "POST":
        pregunta = request.form["pregunta"]

        contexto_usuario = (
            f"El usuario aprobo: {materias_aprobadas}. "
            f"El usuario regularizo: {materias_regularizadas}."
        )

        messages = [
            {"role": "system", "content": "sos un chatbot asistente en una universidad, debes ayudar a los alumnos si quieren saber las fechas de examen y si cumplen las correlativas, tienes un trato gentil hacia el usuario"},
            {"role": "system", "content": contexto_usuario},
            {"role": "user", "content": pregunta}
        ]

        chat_response = client.chat.completions.create(
            # model="gpt-4-1106-preview",  # o gpt-3.5-turbo-1106
            model="meta-llama-3.1-8b-instruct",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
 
        response_msg = chat_response.choices[0].message

        # Si el modelo quiere llamar a una función...
        if response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_to_call = available_functions[function_name]
                function_response = function_to_call(**function_args)

                # Reenviamos la respuesta al modelo incluyendo lo que devolvió la función
                messages.append(response_msg)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(function_response)
                })

            # Nueva llamada ahora con el resultado de la función
            second_response = client.chat.completions.create(
                model="meta-llama-3.1-8b-instruct",
                messages=messages
            )
            respuesta = second_response.choices[0].message.content
        else:
            respuesta = response_msg.content

    return render_template("index.html", respuesta=respuesta)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

