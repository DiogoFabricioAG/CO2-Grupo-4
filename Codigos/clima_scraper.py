from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import csv
from time import sleep
import os
from datetime import datetime

# Configurar Chrome en modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Crear carpeta si no existe
os.makedirs('datos_clima', exist_ok=True)

# Generar nombre de archivo con fecha
fecha_actual = datetime.now().strftime('%Y%m%d')
nombre_archivo = f'datos_clima/dato_{fecha_actual}.csv'


# Inicializar el driver
driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://www.tiempo3.com/south-america/peru/huancavelica?page=today")
    
    # Esperar a que la página cargue
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#day-table"))
    )
    # Hacer clic en el botón "Hora por hora"
    hour_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button#intervals-1")))
    driver.execute_script("arguments[0].click();", hour_button)
    
    # Esperar a que cargue la tabla
    sleep(3)  # Espera explícita para carga dinámica
    
    # Obtener la tabla
    table = driver.find_element(By.CSS_SELECTOR, "table.weather_table.day_table_24")
    
    # Extraer cabeceras (horas)
    headers = [th.text for th in table.find_elements(By.CSS_SELECTOR, "thead th")][1:]  # Excluir el th vacío
    
    # Extraer filas de datos
    data = []
    for row in table.find_elements(By.CSS_SELECTOR, "tbody tr"):
        cells = row.find_elements(By.TAG_NAME, "td")
        if not cells:
            continue
            
        row_name = row.find_element(By.TAG_NAME, "th").text
        row_data = [cell.text.replace("\n", " ") for cell in cells]
        data.append([row_name] + row_data)

    # Guardar en CSV
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Hora"] + headers)  # Escribir cabeceras
        writer.writerows(data)  # Escribir datos
    print(f"Datos guardados en: {nombre_archivo}")

finally:
    driver.quit()