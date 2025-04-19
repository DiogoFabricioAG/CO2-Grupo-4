from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

url = "https://www.tiempo3.com/south-america/peru/huancavelica?page=past-weather"

# Configurar Selenium con Chrome (modo headless opcional)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Ejecutar en segundo plano
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Ruta a tu chromedriver (ajústala)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(url)

try:
    # Esperar hasta que la tabla esté presente (hasta 20 segundos)
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.weather_table.day_table")))
    
    # Dar tiempo adicional si es necesario (ajustable)
    time.sleep(3)
    
    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table = soup.select_one("table.weather_table.day_table")
    
    if not table:
        raise ValueError("Tabla no encontrada después de la espera.")
    
    # Extraer horas (encabezados)
    header_row = table.thead.find("tr")
    horas = [td.get_text(strip=True) for td in header_row.find_all("td")]

    # Extraer filas de datos (igual que antes)
    data_rows = []
    for row in table.tbody.find_all("tr"):
        row_header = row.th.get_text(strip=True)
        celdas = row.find_all("td")
        
        valores = []
        for celda in celdas:
            if row_header == "Temperatura":
                valor = celda.find("span", class_="day_temp").get("data-temp", "").replace(".", ",")
            elif row_header == "Clima":
                valor = celda.find("div", class_="weather_des").get_text(strip=True)
            elif row_header == "Precipitaciones":
                valor = celda.find("span").get("data-length", "").replace(".", ",")
            elif row_header in ["Velocidad del viento", "Ráfaga de viento"]:
                valor = celda.find("span", class_="day_wind").get("data-wind", "").replace(".", ",")
            elif row_header == "Visibilidad":
                valor = celda.find("span", class_="visibility").get("data-wind", "")
            else:
                valor = celda.get_text(strip=True).replace("%", "").replace("Km/h", "").strip()
            valores.append(valor)
        
        data_rows.append([row_header] + valores)

    # Guardar en CSV
    with open("tiempo_huancavelica_selenium.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Metrica"] + horas)
        writer.writerows(data_rows)
        
    print("¡Datos guardados en tiempo_huancavelica_selenium.csv!")

finally:
    driver.quit()  # Cerrar el navegador siempre