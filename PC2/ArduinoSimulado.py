import random
import time
import csv
from datetime import datetime
import serial

puerto_arduino = 'COM5'
velocidad_trans = 9600 

nombre_archivo = 'PC2/datos_arduino_simulado.csv'

with open(nombre_archivo, mode='w', newline='') as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(['Hora', 'LdrValorAnalog', 'LdrVoltaje', 'LdrResistencia', 'Temperatura', 'Humedad'])

try:
    s = serial.Serial(puerto_arduino, velocidad_trans, timeout=1)
    print(f"Conexión establecida en {puerto_arduino} a {velocidad_trans}")
except Exception as e:  
    print(f"Error al conectar con el puerto {puerto_arduino}: {e}")
    exit()

def leer_datos():
    if s.in_waiting > 0:
        data = s.readline().decode('utf-8').strip()
        return data
    return None

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
