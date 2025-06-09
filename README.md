# Analisis de los gastos del Ministerio de Educación y Ciencias
## Breve Descripción:
Este proyecto utilza los siguientes softwares:
- 🐍 **Python** para web scraping
- 🛢️ **SQL** para limpieza y manipulación de datos
- 📊 **Power BI** para dashboards interactivos

## Carpetas y Archivos:
### web_scraping
Esta carpeta continene los archivos de python para obtener los datos de las páginas
Hay dos archivos de webscraping para cada página
Los que tienen sqlserver al final del nombre están hechos para cargar los datos a una tabla en un servidor sql
Los otros dos guardan el csv en el local

### sql
Esta carpeta contiene los queries en sql para crear y transformar las tablas y cargar los datos de manera local
Se puede usar los queries para crear las tablas en el servidor si es que se utiliza alguno
Solo se omitirían los queries para cargar datos en caso de utilizar un servidor 

### Power_Bi
Contiene el archivo .pbix donde se podrán ver los dashboards

## Ejemplo del dashboard: 
descargar el archivo raw y abrir en PowerBi, o sino resultará en un archivo corrupto
![image](https://github.com/user-attachments/assets/1755a92f-df4e-48aa-ba22-42cc160b3b06)

![image](https://github.com/user-attachments/assets/04271308-1f6b-4613-9b9c-c3f3cfaca9a4)

![image](https://github.com/user-attachments/assets/73ce7a38-cbab-4e3b-aac8-c4018972bd34)

