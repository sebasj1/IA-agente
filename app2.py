# app.py

from flask import Flask, render_template, request, Response

import csv
import unicodedata
import re
import json

# Devuelve las fechas de examen y verifica correlativas del alumno
#segundo arbol de decision para correlativas
def buscar_fechas_registrado(materia_buscada,materias_alumno): 
    respuesta = ''
    with open('./documents/programa.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)  #Saltamos la cabecera
        for row in csv_reader:
            #Materia en la segunda columna
            materia = quitar_acentos(row[1].strip().lower())
            #Buscamos si la materia aparece como una palabra completa en el texto
            if re.search(materia_buscada,materia ) or re.search(materia,materia_buscada) and materia!="":
                respuesta += f"Las fechas de {row[1]} son : {row[6] } "
                if  set(row[5].split(',')).issubset(set(materias_alumno))  or row[5]=='':
                    respuesta+="Estás en condiciones para rendir "
                else:
                    #Separa las materias faltantes para rendir
                    cod_materias_faltantes=list(set(row[5].split(','))-set(materias_alumno))
                    materias_faltantes=buscar_materias(cod_materias_faltantes)
                    respuesta+=f"NO estás en condiciones para rendir, te faltan las siguientes materias {materias_faltantes}"
        return respuesta  
     
#buscar las materias que faltan para aprobar
def buscar_materias(lista_materias):
    listado=""
    with open('./documents/programa.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)  # Saltamos la cabecera
        for row in csv_reader:
            if row[0] in lista_materias:
                listado+=f"{row[1]}, "
    return listado

#Devuelve las fechas de examen sin validar correlativas (no hay LU)
def buscar_fechas_no_registrado(materia_buscada): 
    respuesta = ''
    with open('./documents/programa.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)  # Saltamos la cabecera
        for row in csv_reader:
            # Materia en la segunda columna
            materia = quitar_acentos(row[1].strip().lower())  
            # Buscamos si la materia aparece como una palabra completa en el texto
            if re.search(materia_buscada,materia ) or re.search(materia,materia_buscada) and materia!="":
                respuesta += f"Las fechas de {row[1]} son : {row[6] } "
        return respuesta  
           
#esta registrado o no,si Si devuelve materias,si NO devuelve vacio
def buscar_alumno(lu):
    respuesta=''   
    with open('./documents/alumnos.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader: 
            # Asumiendo que las l.u están en la 1ra columna
            alumno = row[0].strip().lower()
            #Valido que este registrado
            if alumno == lu:
                #devuelve todas sus materias aprobadas
                respuesta = row[2].split(',')
    return respuesta

def quitar_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        #Convierte el texto a una forma "descompuesta", donde los caracteres acentuados son representados por dos caracteres: la letra base y el signo de acento.
        if unicodedata.category(c) != 'Mn'
        # Filtra los caracteres que son marcas de acento (como el acento agudo o la tilde) y los elimina.
    )

#este sería el arbol de decision principal
def buscar_fechas(materia_buscada,lu):
    respuesta=""
    if lu!="": #que tenga LU
        materias_alumno=buscar_alumno(lu) #busca al alumno y materias
        if materias_alumno: #si hay es porque está registrado
            fechas=buscar_fechas_registrado(materia_buscada,materias_alumno)
            if fechas: #busca coincidencias de materia
                respuesta=fechas
            else:
                respuesta="No se encontro la materia, brinda más especificación"
        else:
            fechas=buscar_fechas_no_registrado(materia_buscada)
            if fechas:
                respuesta=fechas + "puedes brindar tu Libreta universitaria para más información"
            else:
                respuesta="No se encontro la materia, brinda más especificación"
    else:
        fechas=buscar_fechas_no_registrado(materia_buscada)
        if fechas:
            respuesta=fechas
        else:
            respuesta="No se encontro la materia, brinda más especificación"
    return respuesta

app = Flask(__name__)   

@app.route("/api", methods=["GET", "POST"])

def index():
    respuesta = ""
    if request.method == "GET":
        materia_buscada = request.args.get("pregunta")
        lu = request.args.get("lu")
        #limpio las palabras
        materia_buscada = quitar_acentos(materia_buscada.strip().lower())
        lu= lu.strip().lower()
        respuesta =buscar_fechas(materia_buscada,lu)
       
    data_json = json.dumps({"respuesta": respuesta}, ensure_ascii=False)
    return Response(data_json, content_type="application/json; charset=utf-8")
    # return render_template("index.html", respuesta=respuesta)

@app.route("/chat", methods=["GET"])
def chat():
    # Solo devuelve el HTML para la interfaz de chat
    return render_template("chat.html")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

