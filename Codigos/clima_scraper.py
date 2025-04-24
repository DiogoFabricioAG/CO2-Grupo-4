from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import os
import csv

# Configuración robusta para GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'datos_clima')
os.makedirs(data_dir, exist_ok=True)

fecha_actual = datetime.now().strftime('%Y%m%d')
nombre_archivo = os.path.join(data_dir, f'dato_{fecha_actual}.csv')


try:
    # Configuración automática del driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Resto del código de scraping (mantener tu lógica original)
    driver.get("https://www.tiempo3.com/south-america/peru/huancavelica?page=today")
    
    WebDriverWait(driver, 20).until(
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