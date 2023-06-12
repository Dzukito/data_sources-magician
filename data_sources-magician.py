import requests
from bs4 import BeautifulSoup
import csv
import openpyxl
from openpyxl import load_workbook


lista_grupos = []
dic_grupo_tec = {}
i = 0
dic_id_grupo = {}
dic_tecnicas_nombre = {}
dic_tecnicas_tacticas = {}
dic_tecnicas_description = {}
dic_tecnicas_plataforma = {}
dic_tecnicas_data={}


# Obtener actores seleccionados del Excel
# Ruta del archivo de Excel
archivo_excel = "PrehuntVacio.xlsx"

# Cargar el archivo de Excel
libro = openpyxl.load_workbook(archivo_excel)

# Seleccionar la hoja de cálculo (sheet) específica
hoja = libro["Actores seleccionados"]

# Leer el valor de una celda específica
actores= []
actores.append(str(hoja["B8"].value))
actores.append(hoja["B9"].value)
actores.append(hoja["B10"].value)
actores.append(hoja["B11"].value)

# ---------------------- RECORRER MITRE ----------------------------------------


url = 'https://attack.mitre.org/techniques/enterprise/'

# Realizar la solicitud HTTP GET a la página
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Crear un objeto BeautifulSoup con el contenido HTML de la página
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar la tabla que contiene los grupos
    table_tecnicas = soup.find('table')

#----------------------------- Lista de todas las TTPs ---------------------------------
    lista_id = []
    try:
        tec_id_aux=""
        for row_tec in table_tecnicas.find_all('tr'):
            # Encontrar todas las celdas de la fila
            cells = row_tec.find_all('td')
            if len(cells) >= 0:  # Verificar si hay al menos dos celdas
                tec_id = cells[0].text.strip()
                if tec_id.startswith('T'):  # Filtrar solo los IDs que comienzan con 'T'
                    tec_id_aux=tec_id
                    subtec_id = cells[1].text.strip()  # Obtener el ID de la subtecnología si existe
                    if subtec_id.startswith('.'):
                        tec_id += subtec_id  # Concatenar el ID de la subtecnología a la tecnología principal
                    lista_id.append(tec_id) 
                else:
                    subtec_id = cells[1].text.strip()  # Obtener el ID de la subtecnología si existe
                    if subtec_id.startswith('.'):
                        lista_id.append(tec_id_aux + subtec_id) # Concatenar el ID de la subtecnología a la tecnología principal
                    
    except:
       print("Algo fallo")

#----------------------------- Scraping de c/tecnica ---------------------------------

    url_id = 'https://attack.mitre.org/techniques/'
    for tecnica in lista_id:
        if '.' in tecnica:
          subtecnica_id = tecnica.split('.')
          url_id += subtecnica_id[0]+'/'+subtecnica_id[1]
        else:
            url_id += tecnica

        # Realizar la solicitud HTTP GET a la página
        response_id = requests.get(url_id)
        print(url_id)
        
        if response_id.status_code == 200:
                
                # Crear un objeto BeautifulSoup con el contenido HTML de la página
                soup_id = BeautifulSoup(response_id.content, 'html.parser')

                # Data Sources
                lista_data = []
                try:
                    data_source_aux=""
                    table_data = soup_id.find('table', class_='table datasources-table table-bordered')
                    # Encuentra todas las filas de datos en el cuerpo de la tabla
                    rows = table_data.find_all('tr')

                    # Itera sobre cada fila (omitimos la primera fila de encabezados)
                    for row in rows[1:]:
                        # Encuentra los elementos td de la fila
                        tds = row.find_all('td')
                        
                        # Extrae los valores de las columnas "Data Source" y "Data Component"
                        data_source = tds[1].text.strip()
                        if data_source !='':
                            data_source_aux=data_source
                            data_component = tds[2].text.strip()
                            lista_data.append(f"{data_source} : {data_component}")
                        else:
                            data_component = tds[2].text.strip()
                            lista_data.append(f"{data_source_aux} : {data_component}")

                    if(tecnica not in dic_tecnicas_data):
                        dic_tecnicas_data[tecnica]=lista_data
                    
                except:    
                   pass
                
       #{T123: [Data1, Data2...],T323: [Data1...]}
    dic_data_count={}
    for tecnica, data_sources in dic_tecnicas_data.items():
       for data in data_sources:
          dic_data_count[data]=0
    
    for tecnica, data_sources in dic_tecnicas_data.items():
        for data in data_sources:
            dic_data_count[data]+=1
        
    print(dic_data_count)

    with open('output.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Data source', 'Count'])

        # Escribir los datos en el archivo CSV
        for data, cantidad in dic_data_count.items():
            writer.writerow([data, cantidad])

else:
    print('No se pudo acceder a la página:', response.status_code)
