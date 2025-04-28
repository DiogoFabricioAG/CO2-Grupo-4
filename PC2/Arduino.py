import serial
import time

puerto_arduino = 'COM5'
velocidad_trans = 9600  

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
    Rldr = (Vout * Rfija) / (Vin - Vout)
    return Rldr

while True:
    try:
        data = leer_datos()
        if data:

            data = data.split(',')
            LdrValorAnalog = float(data[0]) # Valor analógico del LDR, entre 0 y 1023, lo cual representa de 0V y 5V
            Temperatura = float(data[1])
            Humedad = float(data[2])

            # Convertir el valor analógico a voltaje (ValueAnalog/1023)*5.0
            LdrValor = (LdrValorAnalog/1023.0)* 5.0
            LdrValor = round(LdrValor, 2)

            # Calcular la resistencia del LDR
            Rldr = calcular_RLDR(LdrValor, 5.0, 220)
            Rldr = round(Rldr, 2)

            print(f"Valor analogico ldr: {LdrValorAnalog}, Voltaje ldr: {LdrValor}, Resistencia ldr: {Rldr} / Temperatura: {Temperatura}°C , Humedad: {Humedad}%")

        time.sleep(1)

    except Exception as e:
        print(f"Error al leer del puerto serial: {e}")
        break