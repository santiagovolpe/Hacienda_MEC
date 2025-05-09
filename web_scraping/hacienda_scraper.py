import os
import time
import requests
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  
from bs4 import BeautifulSoup
# Los requerimientos para importar estan en requirements.txt

# CONFIGURACIÓN
AÑO_DESEADO = "2019"
# pone el path de la carpeta a la que tu sql tenga acceso para importar csvs
CARPETA_DESTINO = f"C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads" 
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# RUTA AL CHROMEDRIVER
# ACTUALIZA esta ruta con la ubicación real si es diferente
ruta_driver = "C:\\Users\\Usuario\\Downloads\\chromedriver-win64\\chromedriver.exe"
# CONFIGURA CHROME HEADLESS
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# CREA EL DRIVER USANDO EL PATH
service = Service(ruta_driver)
driver = webdriver.Chrome(service=service, options=options)

# ACCEDE A LA PÁGINA
url = "https://datos.hacienda.gov.py/data/pgn-gasto/descargas"
driver.get(url)
time.sleep(5)

# PROCESA EL HTML RENDERIZADO
soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

# BUSCA LA TABLA
table = soup.find("table", id="tabla-diccionario")
download_links = soup.select("#tabla-diccionario a[href]")

# FILTRA LOS LINKS DEL AÑO DESEADO
zip_links = [link["href"] for link in download_links if AÑO_DESEADO in link["href"] and link["href"].endswith(".zip")]

print(f"Se encontraron {len(zip_links)} archivos ZIP del año {AÑO_DESEADO}.") //siempre tienen que ser 12

# DESCARGA Y DESCOMPRIME
for url in zip_links:
    filename = os.path.join(CARPETA_DESTINO, url.split("/")[-1])
    print(f"Descargando: {filename}")
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)

    # Descomprime si es ZIP válido
    try:
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(CARPETA_DESTINO)
            print(f"Descomprimido: {filename}")
        
        # Elimina el archivo ZIP después de descomprimirlo
        os.remove(filename)
        print(f"Eliminado archivo ZIP: {filename}")
    except zipfile.BadZipFile:
        print(f"Archivo ZIP corrupto o inválido: {filename}")
