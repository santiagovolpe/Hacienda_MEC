from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd
import mysql.connector
from mysql.connector import Error

start_time = time.time()

year = input("Elija el año: ")

website = "https://www.bcp.gov.py/webapps/web/cotizacion/referencial-fluctuante"
path = 'C:/Users/Usuario/Downloads/chromedriver-win64/chromedriver.exe'

service = Service(executable_path=path)
driver = webdriver.Chrome(service=service)


wait = WebDriverWait(driver, 10)
month_averages = []  # To store averages for each month


# CONFIGURACIÓN DE MySQL
MYSQL_CONFIG = {
    'host': '000.000.00.000',
    'port': 3306,          # debe ser número
    'database': 'base_de_datos',
    'user': 'nombre_de_usuario',
    'password': 'pass',
    'autocommit': True,
    'use_pure': True
}

TABLA_DESTINO = 'bcp'

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

def cargar_a_mysql(connection, df):
    try:
        cursor = connection.cursor()
        columns = list(df.columns)
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f"`{col}`" for col in columns])
        insert_sql = f"""
        INSERT INTO `{TABLA_DESTINO}` ({columns_str}) 
        VALUES ({placeholders})
        """
        data_tuples = [tuple(row) for row in df.values]
        cursor.executemany(insert_sql, data_tuples)
        connection.commit()
        print("Datos cargados exitosamente a MySQL.")
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        connection.rollback()
    finally:
        if cursor:
            cursor.close()

driver.get(website)

try:
    element = wait.until(EC.element_to_be_clickable((By.ID, "dp_cotizacion")))
    element.click()
    time.sleep(1)

    # Elige el año 
    year_select = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker-year")))
    Select(year_select).select_by_visible_text(str(year))

    for month in range(0, 12):  # 0 to 11 for Jan to Dec
        monthly_values = []

        # Selecciona el mes
        month_select = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "ui-datepicker-month")))
        Select(month_select).select_by_value(str(month))
        time.sleep(1.5)

        for fecha in range(1, 32):  # 2 to 31
            try:
                day_str = str(fecha)
                available_dates = driver.find_elements(By.XPATH, f'//td[@title="Available"]/a[text()="{day_str}"]')

                if not available_dates:
                    print(f"Month {month}, Date {day_str} not available — skipping.")
                    continue

                available_dates[0].click()

                cell_xpath = "/html/body/div[2]/div[3]/div/table/tbody/tr[59]/td[2]"
                wait.until(EC.presence_of_element_located((By.XPATH, cell_xpath)))  # Just wait
                value_str = driver.find_element(By.XPATH, cell_xpath).text.strip().replace(".", "").replace(",", ".")

                value = float(value_str)
                monthly_values.append(value)
                print(f"Month {month}, Date {day_str} — Value: {value}")
                time.sleep(1)

                # Reopen calendar after scraping value
                element = wait.until(EC.element_to_be_clickable((By.ID, "dp_cotizacion")))
                element.click()
                time.sleep(1)

            except (TimeoutException, NoSuchElementException, ElementNotInteractableException, ValueError) as e:
                print(f"Error on month {month}, date {fecha}: {e}")
                continue

        # Al final de cada mes calcula y guarda el promedio
        if monthly_values:
            avg_value = sum(monthly_values) / len(monthly_values)
            month_averages.append({"anio": year, "mes": month+1, "compra": avg_value})
            print(f"Month {month} average: {avg_value}")
        else:
            month_averages.append({"Month": month, "AverageValue": None})
            print(f"Month {month} had no available values.")

finally:
    driver.quit()


# Crea DataFrame y guarda en un csv
df = pd.DataFrame(month_averages)
print(df)

print(f"\n--- CONECTANDO A MySQL ---")
mysql_connection = conectar_mysql()
if not mysql_connection:
    print("No se pudo conectar a MySQL. Terminando script.")
    exit(1)

print(f"\n--- INICIANDO CARGA A MySQL ---")
cargar_a_mysql(mysql_connection, df)

if mysql_connection and mysql_connection.is_connected():
    mysql_connection.close()
    print(f"\n--- PROCESO COMPLETADO ---")

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Elapsed time: {elapsed_time:.4f} seconds")
