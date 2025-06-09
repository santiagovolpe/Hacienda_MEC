import os
import time
import requests
import zipfile
import pandas as pd
import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

start_time = time.time()


# CONFIGURACIÓN
AÑO_DESEADO = input("Elija el año: ")
# MES = input("Elija el mes: ")
# MES = "-" + MES
CARPETA_DESTINO = f"C:\\ProgramData\\MySQL\\MySQL Server 8.4\\Uploads"
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# CONFIGURACIÓN DE MySQL
MYSQL_CONFIG = {
    'host': '000.000.00.000',  # Cambia por tu host
    'port': '3306',         # Cambia por tu puerto
    'database': 'nombre_de_base',  # Cambia por tu base de datos
    'user': 'nombre_de_usuario',       # Cambia por tu usuario
    'password': 'contraseña',   # Cambia por tu contraseña
    'autocommit': True,
    'use_pure': True
}

# NOMBRE DE LA TABLA DONDE CARGAR LOS DATOS
TABLA_DESTINO = 'hacienda_import'  # Cambia por el nombre que prefieras

# RUTA AL CHROMEDRIVER
ruta_driver = "C:\\Users\\Usuario\\Downloads\\chromedriver-win64\\chromedriver.exe"

def conectar_mysql():
    """Establece conexión con MySQL"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        if connection.is_connected():
            print(f"Conectado exitosamente a MySQL - {MYSQL_CONFIG['database']}")
            return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None
        

def cargar_csv_a_mysql(connection, csv_path):
    """Carga un archivo CSV a la tabla MySQL"""
    try:
        # Leer CSV con pandas
        df = pd.read_csv(csv_path, encoding='latin1', low_memory=False)
        print(f"Archivo CSV leído: {len(df)} filas encontradas")
        
        # Crear tabla si es el primer archivo
        if not hasattr(cargar_csv_a_mysql, 'tabla_creada'):
            cargar_csv_a_mysql.tabla_creada = True
        
        # Preparar los datos para inserción
        cursor = connection.cursor()
        
        # Construir la consulta INSERT dinámicamente
        columns = list(df.columns)
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f"`{col}`" for col in columns])
        
        insert_sql = f"""
        INSERT INTO `{TABLA_DESTINO}` ({columns_str}) 
        VALUES ({placeholders})
        """
        
        # Convertir DataFrame a lista de tuplas
        data_to_insert = [tuple(row) for row in df.values]
        
        # Insertar datos en lotes para mejor rendimiento
        batch_size = 50000
        total_rows = len(data_to_insert)
        
        for i in range(0, total_rows, batch_size):
            batch = data_to_insert[i:i + batch_size]
            cursor.executemany(insert_sql, batch)
            connection.commit()
            print(f"Insertadas {min(i + batch_size, total_rows)}/{total_rows} filas")
        
        print(f"✓ CSV cargado exitosamente: {os.path.basename(csv_path)}")
        return True
        
    except Exception as e:
        print(f"Error al cargar CSV {csv_path}: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()

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
zip_links = [link["href"] for link in download_links 
            if AÑO_DESEADO in link["href"] in link["href"] and link["href"].endswith(".zip")]

print(f"Se encontraron {len(zip_links)} archivos ZIP del año {AÑO_DESEADO}.")



# VERIFICAR QUE TENEMOS URLs PARA DESCARGAR
if not zip_links:
    print("No se encontraron enlaces para descargar. Terminando script.")
    exit(1)

print(f"URLs encontradas:")
for i, url in enumerate(zip_links, 1):
    print(f"  {i}. {url}")

# CONECTAR A MySQL ANTES DE DESCARGAR
print(f"\n--- CONECTANDO A MySQL ---")
mysql_connection = conectar_mysql()
if not mysql_connection:
    print("No se pudo conectar a MySQL. Terminando script.")
    exit(1)

# DESCARGA, DESCOMPRIME Y CARGA A MySQL
csv_files_to_delete = []

print(f"\n--- INICIANDO DESCARGA Y DESCOMPRESIÓN ---")
for i, url in enumerate(zip_links, 1):
    try:
        filename = os.path.join(CARPETA_DESTINO, url.split("/")[-1])
        print(f"\n[{i}/{len(zip_links)}] Descargando: {filename}")
        
        # Verificar que la URL es completa
        if not url.startswith('http'):
            # Si es una URL relativa, completarla
            base_url = "https://datos.hacienda.gov.py"
            url = base_url + url if url.startswith('/') else base_url + '/' + url
            print(f"URL completa: {url}")
        
        r = requests.get(url, timeout=30)
        print(f"Respuesta HTTP: {r.status_code}")
        
        if r.status_code != 200:
            print(f"Error al descargar: HTTP {r.status_code}")
            continue
            
        with open(filename, "wb") as f:
            f.write(r.content)
        
        print(f"Archivo descargado: {len(r.content)} bytes")
        
        # Descomprime si es ZIP válido
        try:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                extracted_files = zip_ref.namelist()
                print(f"Archivos en ZIP: {extracted_files}")
                zip_ref.extractall(CARPETA_DESTINO)
                print(f"Descomprimido: {filename}")
                
                # Buscar archivos CSV extraídos
                csv_count = 0
                for extracted_file in extracted_files:
                    if extracted_file.endswith('.csv'):
                        csv_path = os.path.join(CARPETA_DESTINO, extracted_file)
                        csv_files_to_delete.append(csv_path)
                        csv_count += 1
                        print(f"  CSV encontrado: {extracted_file}")
                
                print(f"Total CSVs encontrados en este ZIP: {csv_count}")
            
            # Elimina el archivo ZIP después de descomprimirlo
            os.remove(filename)
            print(f"Eliminado archivo ZIP: {filename}")
            
        except zipfile.BadZipFile as e:
            print(f"Archivo ZIP corrupto o inválido: {filename} - Error: {e}")
        except Exception as e:
            print(f"Error al procesar ZIP {filename}: {e}")
            
    except requests.RequestException as e:
        print(f"Error al descargar {url}: {e}")
    except Exception as e:
        print(f"Error general procesando {url}: {e}")

# CARGAR TODOS LOS CSV A MySQL
print(f"\n--- INICIANDO CARGA A MySQL ---")
archivos_cargados = 0

for csv_file in csv_files_to_delete:
    if os.path.exists(csv_file):
        print(f"\nCargando: {os.path.basename(csv_file)}")
        if cargar_csv_a_mysql(mysql_connection, csv_file):
            archivos_cargados += 1
            # Eliminar CSV después de carga exitosa
            os.remove(csv_file)
            print(f"✓ Eliminado CSV: {os.path.basename(csv_file)}")
        else:
            print(f"✗ Error al cargar: {os.path.basename(csv_file)}")

# CERRAR CONEXIÓN MySQL
if mysql_connection and mysql_connection.is_connected():
    mysql_connection.close()
    print(f"\n--- PROCESO COMPLETADO ---")
    print(f"Archivos cargados exitosamente: {archivos_cargados}/{len(csv_files_to_delete)}")
    print("Conexión a MySQL cerrada.")

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.4f} seconds")
