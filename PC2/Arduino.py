import serial
import time
import csv
from datetime import datetime

puerto_arduino = 'COM9'
velocidad_trans = 9600  

try:
    s = serial.Serial(puerto_arduino, velocidad_trans, timeout=1)
    print(f"Conexión establecida en {puerto_arduino} a {velocidad_trans}")
except Exception as e:  
    print(f"Error al conectar con el puerto {puerto_arduino}: {e}")
    exit()

nombre_archivo = 'PC2/datos_arduino.csv'

with open(nombre_archivo, mode='w', newline='') as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(['Hora', 'LdrValorAnalog', 'LdrVoltaje', 'LdrResistencia', 'Temperatura', 'Humedad'])


def leer_datos():
    if s.in_waiting > 0:
        data = s.readline().decode('utf-8').strip()
        return data
    return None

def calcular_RLDR(Vout, Vin, Rfija):
    if Vin == Vout:
        raise ValueError("Vout no puede ser igual a Vin")
    Rldr = Rfija*(Vin/Vout - 1)
    return Rldr

while True:
    try:
        data = leer_datos()
        if data:

            data = data.split(',')
            LdrValorAnalog = float(data[0]) # Valor analógico del LDR, entre 0 y 1023, lo cual representa de 0V y 5V
            if(LdrValorAnalog == 0):
                LdrValorAnalog = 0.1
            Temperatura = float(data[1])
            Humedad = float(data[2])

            # Convertir el valor analógico a voltaje (ValueAnalog/1023)*5.0
            LdrValorVoltaje = (LdrValorAnalog/1023.0)* 5.0
            LdrValorVoltaje = round(LdrValorVoltaje, 4)

            LdrResistencia = calcular_RLDR(LdrValorVoltaje, 5.0, 220)
            LdrResistencia = round(LdrResistencia, 2)

            hora_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            with open(nombre_archivo, mode='a', newline='') as archivo:
                escritor = csv.writer(archivo)
                escritor.writerow([hora_actual, LdrValorAnalog, LdrValorVoltaje, LdrResistencia, Temperatura, Humedad])

        time.sleep(5)

    except Exception as e:
        print(f"Error al leer del puerto serial: {e}")
        break