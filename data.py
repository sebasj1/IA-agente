# data.py

def get_fechas_materia(nombre_materia):
    fechas = {
        "Matemática I": ["15/06/2025", "01/07/2025"],
        "Física I": ["32/06/2025", "10/07/2025"],
        "Química": ["18/06/2025"]
    }
    return fechas.get(nombre_materia, ["Sin fechas disponibles."])

def get_correlativas(nombre_materia):
    correlativas = {
        "Física I": "Debe tener aprobada Matemática I",
        "Química": "Debe tener regularizada Física I y Matemática I",
        "Matemática I": "Sin correlativas"
    }
    return correlativas.get(nombre_materia, "No hay información de correlatividades.")
