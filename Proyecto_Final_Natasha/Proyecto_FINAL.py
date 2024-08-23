#Importo las librerias
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_data():
    # URL del Sitio Web para el scraping 
    PAGINA_PRINCIPAL = "https://www.scrapethissite.com/pages/simple/"
    navegador = webdriver.Firefox()
    navegador.get(PAGINA_PRINCIPAL)
    navegador.implicitly_wait(10)

    datos = []
    try:
        paises = WebDriverWait(navegador, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.country'))
        )
        for pais in paises:
            nombre = pais.find_element(By.CSS_SELECTOR, ".country-name").text
            capital = pais.find_element(By.CSS_SELECTOR, ".country-capital").text
            poblacion = pais.find_element(By.CSS_SELECTOR, ".country-population").text
            superficie = pais.find_element(By.CSS_SELECTOR, ".country-area").text
            datos.append({
                'nombre': nombre,
                'capital': capital,
                'poblacion': poblacion,
                'superficie': superficie
            })
    except Exception as e:
        raise e
    finally:
        navegador.quit()

    #Crear el DataFrame y guardarlo en un CSV 
    df = pd.DataFrame(datos)
    return df

df = scrape_data()
file_path = os.path.join(os.getcwd(), "paises_exportados.csv")
df.to_csv(file_path, index=False)
df.head()

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/datos', methods=['GET'])
def obtener_datos():
    # Cargar el archivo CSV
    df = pd.read_csv("paises_exportados.csv")
    
    # Obtener el parámetro de filtro desde la URL
    min_poblacion = request.args.get('min_poblacion', default=0, type=int)
    
    # Filtrar los datos según la población mínima
    datos_filtrados = df[df['poblacion'].astype(int) > min_poblacion]
    
    # Convertir los datos filtrados en una lista de diccionarios
    resultado = datos_filtrados.to_dict(orient='records')
    
    # Devolver los datos como una respuesta JSON
    return jsonify(resultado)

# Ejecutar Flask en segundo plano
from threading import Thread
server = Thread(target=lambda: app.run(debug=False, use_reloader=False))
server.start()

import requests
import seaborn as sns
import matplotlib.pyplot as plt

# URL de la API para consumir los datos
url = 'http://127.0.0.1:5000/datos?min_poblacion=5000000'
response = requests.get(url)

if response.status_code == 200:
    datos = response.json()
    df = pd.DataFrame(datos)
else:
    print("Error al consumir la API")
    df = pd.DataFrame()

# Verificar si el DataFrame no está vacío
if not df.empty:
    # Ejemplo de categorización según el nombre del país
    df['continente'] = df['nombre'].apply(lambda x: 'América' if x in ['Canadá', 'México', 'Estados Unidos'] else 'Otro')

    # Gráfico Categórico: Población por Continente
    plt.figure(figsize=(10, 6))
    sns.barplot(x='continente', y='poblacion', data=df, ci=None)
    plt.title('Población por Continente')
    plt.show()

    # Gráfico Relacional: Relación entre Superficie y Población
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='superficie', y='poblacion', data=df)
    plt.title('Relación entre Superficie y Población')
    plt.xlabel('Superficie (km²)')
    plt.ylabel('Población')
    plt.show()

    # Gráfico de Distribución: Distribución de la Población
    plt.figure(figsize=(10, 6))
    sns.histplot(df['poblacion'], kde=True)
    plt.title('Distribución de la Población')
    plt.xlabel('Población')
    plt.show()