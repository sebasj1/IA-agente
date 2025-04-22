# app.py

from flask import Flask, render_template, request

import csv
import unicodedata
import re

 

def buscar_materias(lista_materias):
    listado=""
    with open('./documents/programa.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)  # Saltamos la cabecera
        for row in csv_reader:
            if len(row) > 1: 
                if row[0] in lista_materias:
                    listado+=f"{row[1]}, "
    return listado

def evaluar_materia(pregunta,materias_alumno): 
    flag = ''
    pregunta = pregunta.strip().lower()
    
    with open('./documents/programa.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        next(csv_reader, None)  # Saltamos la cabecera
        for row in csv_reader:
            if len(row) > 1:  # Asegurarse de que la fila tiene al menos dos columnas
                materia = quitar_acentos(row[1].strip().lower())  # Materia en la segunda columna
                # Buscamos si la materia aparece como una palabra completa en el texto
                if re.search(pregunta,materia ) or re.search(materia,pregunta) and materia!="":
                    flag += f"Las fechas de {row[1]} son : {row[6] } "
                    if  set(row[5].split(',')).issubset(set(materias_alumno))  or row[5]=='':
                        flag+="Estás en condiciones para rendir "
                    else:
                        cod_materias_faltantes=list(set(row[5].split(','))-set(materias_alumno))
                        materias_faltantes=buscar_materias(cod_materias_faltantes)
                        flag+=f"NO estás en condiciones para rendir, te falta/n las siguientes materias {materias_faltantes}"
        return flag  
           
def evaluar_alumno(lu):
    flag=''
    with open('./documents/alumnos.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
       
        for row in csv_reader: 
            if len(row) > 1:  # Asegurarse de que la fila tiene al menos dos columnas
                alumno = row[0].strip().lower()  # Asumiendo que las materias están en la segunda columna
                if alumno == lu.strip().lower():
                    flag = row[2].split(',')#devuelve todas sus materias aprobadas
                      
    return flag

def quitar_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        #Convierte el texto a una forma "descompuesta", donde los caracteres acentuados son representados por dos caracteres: la letra base y el signo de acento.
        if unicodedata.category(c) != 'Mn'
        # Filtra los caracteres que son marcas de acento (como el acento agudo o la tilde) y los elimina.
    )

def buscar_fechas(pregunta,lu):
    #Considerando que es alumno y essa materia existe,evaluar correlativas
    respuesta="No se encontró al estudiante"
    materias_alumno=evaluar_alumno(lu)
    if materias_alumno: #si hay es porque está registrado
        fechas=evaluar_materia(pregunta,materias_alumno)
        if fechas:
            respuesta=fechas
        else:
            respuesta="No se encontro la materia, brinda más especificación"
    return respuesta

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""
    if request.method == "POST":
        pregunta = request.form["pregunta"]
        lu = request.form["lu"]
        pregunta=quitar_acentos(pregunta)#quito los acentos
        respuesta =buscar_fechas(pregunta,lu)
       
      
    return render_template("index.html", respuesta=respuesta)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

