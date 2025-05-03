import streamlit as st
import pandas as pd
import time
import altair as alt

st.set_page_config(page_title="Monitor Sensor", layout="centered")

st.title("📊 Monitor de Sensores en Tiempo Real")

nombre_archivo = 'PC2/datos_arduino_simulado.csv'

# Cargar los datos
@st.cache_data(ttl=1)
def cargar_datos():
    df = pd.read_csv(nombre_archivo)
    df['Hora'] = pd.to_datetime(df['Hora'])
    return df

# Bucle para actualizar en tiempo real
placeholder = st.empty()

while True:
    df = cargar_datos()

    with placeholder.container():
        st.subheader("Gráfico del Voltaje del LDR")
        chart1 = alt.Chart(df).mark_line().encode(
            x='Hora:T',
            y='LdrValorAnalog:Q'
        ).properties(height=200)
        st.altair_chart(chart1, use_container_width=True)

        st.subheader("Gráfico de Temperatura")
        chart2 = alt.Chart(df).mark_line().encode(
            x='Hora:T',
            y='Temperatura:Q'
        ).properties(height=200)
        st.altair_chart(chart2, use_container_width=True)

        st.subheader("Gráfico de Humedad")
        chart3 = alt.Chart(df).mark_line().encode(
            x='Hora:T',
            y='Humedad:Q'
        ).properties(height=200)
        st.altair_chart(chart3, use_container_width=True)

    time.sleep(1)
