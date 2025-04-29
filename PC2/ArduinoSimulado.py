import random
import time
import csv
from datetime import datetime

nombre_archivo = 'PC2/datos_arduino_simulado.csv'

with open(nombre_archivo, mode='w', newline='') as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(['Hora', 'LdrValorAnalog', 'LdrVoltaje', 'LdrResistencia', 'Temperatura', 'Humedad'])

def leer_datos():
    # Simulación de datos similares a los reales:
    LdrValorAnalog = random.uniform(0.0, 10.0)   # Similar a lo que viste: entre 0 y 10 aprox
    Temperatura = random.uniform(25.0, 27.0)     # Entre 25°C y 27°C
    Humedad = random.uniform(44.0, 46.0)         # Entre 44% y 46%
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
            LdrValorAnalog = float(data[0])
            if LdrValorAnalog == 0:
                LdrValorAnalog = 0.1
            Temperatura = float(data[1])
            Humedad = float(data[2])

            LdrValorVoltaje = (LdrValorAnalog / 1023.0) * 5.0
            LdrValorVoltaje = round(LdrValorVoltaje, 4)

            LdrResistencia = calcular_RLDR(LdrValorVoltaje, 5.0, 220)
            LdrResistencia = round(LdrResistencia, 2)

            hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(nombre_archivo, mode='a', newline='') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([hora_actual, LdrValorAnalog, LdrValorVoltaje, LdrResistencia, Temperatura, Humedad])

            print(f"Hora: {hora_actual}, LDR: {LdrValorAnalog}, Voltaje: {LdrValorVoltaje}, "
                  f"Resistencia: {LdrResistencia}, Temp: {Temperatura}, Humedad: {Humedad}")

        time.sleep(1)

    except Exception as e:
        print(f"Error al simular datos: {e}")
        break
