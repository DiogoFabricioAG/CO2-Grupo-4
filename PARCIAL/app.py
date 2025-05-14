import streamlit as st
import pandas as pd
import time
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Monitor Sensor", layout="centered")

st.title("📊 Monitor de Sensores en Tiempo Real")

nombre_archivo = 'Datos_arduino.csv'

# Función para convertir LDR a lux (aproximada)
def ldr_to_lux(ldr_val):
    try:
        return round(12.5*ldr_val, 2)
    except ZeroDivisionError:
        return 0

#Clasificación de exposición solar
def clasificar_exposicion(lux):
    if lux < 10000:
        return "Baja"
    elif lux < 25000:
        return "Moderada"
    elif lux < 40000:
        return "Alta"
    elif lux < 50000:
        return "Muy Alta"
    else:
        return "Extrema"

def riesgo_solar(nivel):
    if nivel in ["Alta", "Muy Alta", "Extrema"]:
        return "Peligroso"
    elif nivel == "Moderada":
        return "Precaución"
    else:
        return "Seguro"

def recomendacion(nivel):
    if nivel == "Baja":
        return "No se requiere protección solar"
    elif nivel == "Moderada":
        return "Usar sombrero o protector solar"
    elif nivel == "Alta":
        return "Usar protector solar y gafas de sol"
    elif nivel == "Muy Alta":
        return "Evitar exposición prolongada"
    else:
        return "Permanecer bajo sombra o en interiores"

# Funciones de color
def color_lux(nivel):
    if nivel == "Baja":
        return "Verde"
    elif nivel == "Moderada":
        return "Amarillo"
    else:
        return "Rojo"

def color_temp(temp):
    if temp < 18:
        return "Azul"
    elif temp <= 28:
        return "Verde"
    else:
        return "Rojo"

def color_hum(hum):
    if hum < 60:
        return "Amarillo"
    elif hum <= 85:
        return "Verde"
    else:
        return "Rojo"

def asignar_segmentos(df, columna_color, nombre_segmento):
    segmento = 0
    segmentos = []
    ultimo_color = None
    for color in df[columna_color]:
        if color != ultimo_color:
            segmento += 1
        segmentos.append(segmento)
        ultimo_color = color
    df[nombre_segmento] = segmentos


# Cargar los datos
@st.cache_data(ttl=1)
def cargar_datos():
    df = pd.read_csv(nombre_archivo)
    df['Hora'] = pd.to_datetime(df['Hora'])
    df['Lux'] = df['LdrValorAnalog'].apply(ldr_to_lux)
    df['Exposición'] = df['Lux'].apply(clasificar_exposicion)
    df['Riesgo'] = df['Exposición'].apply(riesgo_solar)
    df['Recomendación'] = df['Riesgo'].apply(recomendacion)
    df['ColorLux'] = df['Exposición'].apply(color_lux)
    df['ColorTemp'] = df['Temperatura'].apply(color_temp)
    df['ColorHumedad'] = df['Humedad'].apply(color_hum)
    asignar_segmentos(df, 'ColorLux', 'SegmentoLux')
    asignar_segmentos(df, 'ColorTemp', 'SegmentoTemp')
    asignar_segmentos(df, 'ColorHumedad', 'SegmentoHumedad')
    return df

# Funcion para colorear el gráfico
def grafico_coloreado(df, columna_valor, columna_color, columna_segmento, titulo, escala_colores, unidad="Q"):
    capas = []
    for color_valor, color_hex in escala_colores.items():
        capa = alt.Chart(df[df[columna_color] == color_valor]).mark_line().encode(
            x='Hora:T',
            y=alt.Y(f'{columna_valor}:{unidad}', title=titulo),
            color=alt.value(color_hex),
            detail=columna_segmento  # ← Agrupa para evitar unión entre segmentos
        )
        capas.append(capa)
    return alt.layer(*capas).resolve_scale(y='shared').properties(height=200)


# Bucle para actualizar en tiempo real
placeholder = st.empty()

while True:
    df = cargar_datos()
    ultima = df.iloc[-1]

    with placeholder.container():
        st.subheader("📊 Datos en Tiempo Real")

        st.subheader("📈 Gráfico de Intensidad Lumínica (Lux)")
        colores_lux = {
            "Amarillo": "orange",
            "Verde": "green",
            "Rojo": "red"
        }
        grafico_lux = grafico_coloreado(df, "Lux", "ColorLux", "SegmentoLux", "Lux", colores_lux)
        st.altair_chart(grafico_lux, use_container_width=True)

        st.subheader("🌡️ Gráfico de Temperatura (°C)")
        colores_temp = {
            "Azul": "blue",
            "Verde": "green",
            "Rojo": "red"
        }
        grafico_temp = grafico_coloreado(df, "Temperatura", "ColorTemp", "SegmentoTemp", "Temperatura", colores_temp)
        st.altair_chart(grafico_temp, use_container_width=True)


        st.subheader("💧 Gráfico de Humedad (%)")
        colores_hum = {
            "Amarillo": "orange",
            "Verde": "green",
            "Rojo": "red"
        }
        grafico_hum = grafico_coloreado(df, "Humedad", "ColorHumedad", "SegmentoHumedad", "Humedad", colores_hum)
        st.altair_chart(grafico_hum, use_container_width=True)

        # Indicadores
        st.subheader("📌 Indicadores en Tiempo Real")
        st.metric("Intensidad lumínica (lux)", f"{ultima['Lux']} lux")
        st.metric("Nivel de exposición solar", ultima['Exposición'])
        st.metric("Estado de riesgo solar", ultima['Riesgo'])
        st.metric("Última hora de medición", ultima['Hora'].strftime("%H:%M:%S"))
        st.info(f"🧠 Recomendación: {ultima['Recomendación']}")

    time.sleep(1)
