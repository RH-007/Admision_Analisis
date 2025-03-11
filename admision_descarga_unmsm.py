
## Decarga data Admision

## LIBRERIAS
## ==================:

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import re
import warnings
warnings.filterwarnings("ignore")

## INICIO DE PROCESO
## ==================:

# Solicitar año y admisión al usuario en un bucle
while True:
    try:
        anio = int(input("Año a extraer información: "))
        admision = int(input("Admisión 1 o 2: "))

        if anio > 2023 and admision in [1, 2]:
            print("Año Cargado")
            break
        else:
            print("Pruebe con otro año más actual y asegúrese de que la admisión sea 1 o 2.")
    except ValueError:
        print("Ingrese valores numéricos válidos.")


# URL base y página de admisión
# base_url = f"https://admision.unmsm.edu.pe/Website{anio}{admision}/"
# base_url = f"https://admision.unmsm.edu.pe/Website{anio}{admision}General/"
base_url = f"https://admision.unmsm.edu.pe/Website{anio}{admision}GeneralA/"

url = base_url + "A.html" ## relacion de todas las carreras

print(f"Se extraera informacion del examen de Admision del año {anio} - {admision}")
print("\nValidando informacion:")

# Hacer la solicitud HTTP
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers, verify=False)

print("Enlace a Consultar:", url)

if response.status_code == 200:
    print("\nExiste informacion! 😎👌")
else:
    print("\nNo existe información 😣")

print("\nINICIO OBTENCION DE ENLACES")    

## Extraccion de Enlaces de Carreras    
soup = BeautifulSoup(response.content, "html.parser")
a_tags = soup.find_all('a')

enlaces_carreras = []
nombre_carreras = []
codigo_carreras = []

for tag in a_tags:
    if tag["href"].startswith("./A/"):
        
        enlace = base_url + tag["href"][2:]
        carrera = tag.get_text()
        
        # Extraer el código de la escuela con expresiones regulares
        patron = r"/(\d+)/0\.html"
        resultado = re.search(patron, enlace)
        
        # Verificar si encontró el código
        codigos = resultado.group(1) if resultado else "No encontrado"

        enlaces_carreras.append(enlace)
        nombre_carreras.append(carrera)
        codigo_carreras.append(codigos)
        
print("-"*50)
print("\nTotal de enlaces de carreras :", len(enlaces_carreras))
print("\nTotal de carreras :", len(nombre_carreras))
print("\nTotal de codigo de carrera :", len(codigo_carreras))
print("Enlaces Validados!")

escuela_data = list(zip(nombre_carreras, codigo_carreras))
escuela_data_df = pd.DataFrame(escuela_data, columns=["ESCUELA", "CODIGO"])


## Descarga Data

informacion_carrera = list(zip(nombre_carreras, codigo_carreras, enlaces_carreras))

## Funcion Extraccion de Data por carrera!
def data_admision_unmsm(informacion_carrera):
    url = informacion_carrera[2]
    cod_escuela = informacion_carrera[1]
    
    # Obtener la respuesta de la solicitud
    response = requests.get(url) 
    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    # Encontrar la tabla con el id "tablaPostulantes"
    tabla = soup.find("table", {"id": "tablaPostulantes"})
    
    # Extraer los encabezados de la tabla
    th_tags = tabla.find_all('th')
    encabezados = []
    for th in th_tags:
        encabezado = th.get_text()
        encabezados.append(encabezado)
        
    ## extraer datos fila por fila
    data = []
    # Omitimos la primera fila (encabezados)
    filas = tabla.find_all("tr")[1:]
    for fila in filas:
        celdas = fila.find_all("td") # Obtener el texto de cada celda y eliminar espacios en blanco
        columnas = []
        for celda in celdas:
            texto = celda.text.strip()
            columnas.append(texto)
        # Verificar que la fila tenga contenido
        if columnas:
            data.append(columnas)
    
    ## DataFrame
    df = pd.DataFrame(data, columns=encabezados)
    
    df.insert(0, 'CODIGO_ESCUELA', cod_escuela)
    
    return df    

print("\nINICIO DESCARGA DE DATA ADMISION")

data_postulacion = []
for enlace_i in informacion_carrera:

    data = data_admision_unmsm(enlace_i)
    nombre_carrera = pd.unique(data.iloc[:,3])[0]
    
    print("descargando data de la carrera:", nombre_carrera)
    
    data_carrera = data.iloc[:,0:7] ## conisderamos solo las primeros 6 columnas
    data_carrera.columns = ["CODIGO_ESCUELA", "CODIGO", "APELLIDOS_NOMBRES", "ESCUELA_PROFESIONAL", "PUNTAJE", "MERITO", "OBS"]
    data_postulacion.append(data_carrera)


print("fin descarga!")


print("\nGUARDANDO INFORMACIÓN 😎")
## Guardado de Informacion 
data_postulacion_final = pd.concat(data_postulacion, axis=0)
print("TOTAL POSTULANTES:", len(data_postulacion_final))

## Crea la columna ANIO (año) de prueba de admision
data_postulacion_final["ANIO"] = anio
data_postulacion_final["TIPO"] = admision

## Guarda la data en CSV
directorio = "datos_admision"
os.makedirs(directorio, exist_ok=True)  # Crea la carpeta si no existe
nombre_archivo = os.path.join(directorio, f"data_admision_{anio}{admision}.csv")

data_postulacion_final.to_csv(nombre_archivo, sep="|", index=False, encoding='utf-8')

os.makedirs(directorio, exist_ok=True)  # Crea la carpeta si no existe
nombre_archivo_escuela = os.path.join(directorio, f"escuela_admision_{anio}{admision}.csv")

escuela_data_df.to_csv(nombre_archivo_escuela, sep="|", index=False, encoding="utf-8")

print("Descarga hecha ✌️")
