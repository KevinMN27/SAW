import ctypes
from ctypes import c_double, c_char_p, c_int, POINTER
import os
from fastapi import FastAPI, UploadFile, File as FastAPIFile
from pydantic import BaseModel
from typing import List
import csv
from io import StringIO

# Obtener la ruta completa del archivo DLL
#os.add_dll_directory(r'C:\msys64\ucrt64\bin')
os.add_dll_directory(r'C:\Programacion\compilador\mingw64\bin')
dll_path = os.path.join(os.path.dirname(__file__), "saw.dll")

# Cargar la biblioteca compartida generada
saw_lib = ctypes.CDLL(dll_path)

# Definir las firmas de las funciones C++
saw_lib.add_criterion.argtypes = [c_char_p, c_double, c_char_p]
saw_lib.add_criterion.restype = None

saw_lib.add_alternative.argtypes = [c_char_p, POINTER(c_double), c_int]
saw_lib.add_alternative.restype = None

saw_lib.calculate_best_alternative.restype = c_int

# Agregar los criterios desde Python


# Iniciar la aplicación FastAPI
app = FastAPI()

#Modelo para criterios
class Criterio(BaseModel):
    nombre: str
    peso: float
    tipo: str

#Modelo para alternativas
class Alternativa(BaseModel):
    nombre: str
    valores: List[float] #Lista de valores para las alternativas 

# Agregar alternativas y sus valores

'''

saw_lib.add_criterion(b"Logros", 5.0, b"cost")
saw_lib.add_criterion(b"Ambiente", 4.0, b"benefit")
saw_lib.add_criterion(b"Acreditacion", 3.0, b"cost")
saw_lib.add_criterion(b"Curriculum", 2.0, b"benefit")
saw_lib.add_criterion(b"ExtraAct", 1.0, b"benefit") 
alt1 = (c_double * 5)(4, 2, 4, 2, 2)
alt2 = (c_double * 5)(2, 3, 3, 2, 1)
alt3 = (c_double * 5)(2, 3, 3, 1, 2)
alt4 = (c_double * 5)(4, 1, 3, 1, 1)

saw_lib.add_alternative(b"Alternativa 1", alt1, 5)
saw_lib.add_alternative(b"Alternativa 2", alt2, 5)
saw_lib.add_alternative(b"Alternativa 3", alt3, 5)
saw_lib.add_alternative(b"Alternativa 4", alt4, 5)

# Calcular la mejor alternativa
best_alt_index = saw_lib.calculate_best_alternative()
print(f"La mejor alternativa es: Alternativa {best_alt_index + 1}")
'''

# Crear estructuras para almacenar criterios y alternativas
criterios = []
alternativas = []


# Endpoint para agregar criterios
@app.post("/criterios/")
async def agregar_criterio(criterio: Criterio):
    saw_lib.add_criterion(criterio.nombre.encode(), c_double(criterio.peso), criterio.tipo.encode())
    return {"mensaje": f"Criterio '{criterio.nombre}' agregado exitosamente."}

# Endpoint para agregar alternativas
@app.post("/alternativas/")
async def agregar_alternativa(alternativa: Alternativa):
    if len(alternativa.valores) < 2:
        return {"error": "No funciona."}
    
    alt_valores = (c_double * len(alternativa.valores))(*alternativa.valores)
    saw_lib.add_alternative(alternativa.nombre.encode(), alt_valores, len(alternativa.valores))
    return {"mensaje": f"Alternativa '{alternativa.nombre}' agregada exitosamente."}

# Endpoint para calcular la mejor alternativa
@app.get("/mejor_alternativa/")
async def calcular_mejor_alternativa():
    best_alt_index = saw_lib.calculate_best_alternative()
    return {"mensaje": f"La mejor alternativa es: Alternativa {best_alt_index + 1}"}

# Endpoint para procesar un archivo .txt con los criterios
@app.post("/archivo_criterios/")
async def procesar_archivo_criterios(file: UploadFile = FastAPIFile(...)):

    if not file.filename.endswith(".txt"):
        return {"error": "El archivo debe ser un archivo .txt"}
    
    content = await file.read()  # Leer el contenido del archivo
    decoded_content = content.decode("utf-8").strip()  # Decodificar el archivo y eliminar espacios en blanco
    
    # Leer el contenido como líneas separadas por comas
    csv_reader = csv.reader(StringIO(decoded_content))
    
    criterios = []
    
    for row in csv_reader:
        # Validar que la fila no esté vacía y contenga exactamente 3 elementos
        if len(row) != 3:
            if not row:  # Si la fila está vacía, la ignoramos
                continue
            return {"error": f"Fila inválida: {row}. Cada fila debe contener nombre, valor y tipo."}
        
        try:
            nombre = row[0].strip()  # Eliminar espacios en blanco alrededor
            peso = float(row[1].strip())  # Convertir el valor a float
            tipo = row[2].strip()  # Eliminar espacios en blanco alrededor
            
            # Validar que el tipo sea "cost" o "benefit"
            if tipo not in ["cost", "benefit"]:
                return {"error": f"Tipo inválido en la fila {row}. El tipo debe ser 'cost' o 'benefit'."}
            
            # Agregar el criterio a la biblioteca C++
            saw_lib.add_criterion(nombre.encode(), c_double(peso), tipo.encode())
            criterios.append({"nombre": nombre, "peso": peso, "tipo": tipo})
        
        except ValueError:
            return {"error": f"Error en la conversión de datos en la fila: {row}. El peso debe ser un número válido."}
    
    return {
        "mensaje": "Archivo .txt procesado y criterios agregados correctamente.",
        "criterios": criterios
    }

# Endpoint para procesar un archivo .txt con las alternativas
@app.post("/archivo_alternativas/")
async def procesar_archivo_alternativas(file: UploadFile = FastAPIFile(...)):
    if not file.filename.endswith(".txt"):
        return {"error": "El archivo debe ser un archivo .txt"}
    
    content = await file.read()  # Leer el contenido del archivo
    decoded_content = content.decode("utf-8")  # Decodificar el archivo en texto
    
    # Leer el contenido como líneas separadas por comas
    csv_reader = csv.reader(StringIO(decoded_content))
    
    alternativas = []
    for row in csv_reader:
        # Validar que la fila contenga al menos 6 elementos (nombre + 5 valores)
        if len(row) < 2:
            return {"error": f"Fila inválida: {row}."}
        
        nombre = row[0]
        valores = [float(x) for x in row[1:]]  # Convertir los valores a float
        
        # Convertir los valores de la alternativa a c_double y agregar a la biblioteca C++
        alt_valores = (c_double * len(valores))(*valores)
        saw_lib.add_alternative(nombre.encode(), alt_valores, len(valores))
        alternativas.append({"nombre": nombre, "valores": valores})
    
    return {
        "mensaje": "Archivo .txt procesado y alternativas agregadas correctamente.",
        "alternativas": alternativas
    }