import random
import time
import csv
from datetime import datetime
import os

nombre_archivo = "D:/UNI/6TO CICLO/ANALITICA DE DATOS/Proyecto SI150/PC2/datos_arduino_simulado.csv"

with open(nombre_archivo, mode='w', newline='') as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(['Dia', 'Hora', 'LdrValorAnalog', 'LdrVoltaje', 'LdrResistencia', 'Temperatura', 'Humedad'])

def leer_datos():
    # Simulación de datos similares a los reales:
    LdrValorAnalog = random.uniform(0.0, 10.0)   # Similar a lo que viste: entre 0 y 10 aprox
    Temperatura = random.uniform(25.0, 27.0)     # Entre 25°C y 27°C
    Humedad = random.randint(40, 46)         # Entre 44% y 46%
    return f"{LdrValorAnalog},{Temperatura},{Humedad}"

def calcular_RLDR(Vout, Vin, Rfija):
    if Vin == Vout:
        raise ValueError("Vout no puede ser igual a Vin")
    Rldr = Rfija * (Vin / Vout - 1)
    return Rldr

while True:
    try:
        data = leer_datos()
        if data:
            data = data.split(',')
            LdrValorAnalog = round(float(data[0]),2)
            if LdrValorAnalog == 0:
                LdrValorAnalog = 0.1
            Temperatura = round(float(data[1]),2)
            Humedad = int(data[2])

            LdrValorVoltaje = (LdrValorAnalog / 1023.0) * 5.0
            LdrValorVoltaje = round(LdrValorVoltaje, 4)

            LdrResistencia = calcular_RLDR(LdrValorVoltaje, 5.0, 220)
            LdrResistencia = round(LdrResistencia, 2)

            now = datetime.now()
            dia_actual = now.strftime('%Y-%m-%d')
            hora_actual = now.strftime('%H:%M:%S')

            with open(nombre_archivo, mode='a', newline='') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([dia_actual, hora_actual, LdrValorAnalog, LdrValorVoltaje, LdrResistencia, Temperatura, Humedad])

            print(f"Dia: {dia_actual}, Hora: {hora_actual}, LDR: {LdrValorAnalog}, Voltaje: {LdrValorVoltaje}, "
                  f"Resistencia: {LdrResistencia}, Temp: {Temperatura}, Humedad: {Humedad}")

        time.sleep(5)

    except Exception as e:
        print(f"Error al simular datos: {e}")
        break