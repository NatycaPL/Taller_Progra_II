import requests
import json

#consumir el recurso
URL = "https://jsonplaceholder.typicode.com/users"


# Realizar la solicitud GET a la API con autenticación 
respuesta = requests.get(URL)

# Validar el estado de la solicitud
if respuesta.status_code == 200:
    print('Solicitud Exitosa')
    print('Datos Extraidos: ', respuesta.json())
else:
    print("Error en la solicitud del recurso. Detalles: \n",
          respuesta.text)

