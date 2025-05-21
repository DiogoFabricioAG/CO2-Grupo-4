# climate_db_server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import requests
import os
import psycopg2
import json

# Create an MCP server
mcp = FastMCP("pg-server-climate", "0.1.0")

# Load environment variables
db_host = os.environ.get("DB_HOST", "localhost")
db_name = os.environ.get("DB_NAME", "dataClimateBase")
db_user = os.environ.get("DB_USER", "postgres")
db_password = os.environ.get("DB_PASSWORD", "123")

try:
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
    cursor = conn.cursor()
    print("Conexión a PostgreSQL exitosa!")
except psycopg2.Error as e:
    print(f"Error al conectar a PostgreSQL: {e}")
    exit()

@mcp.tool(description="Devuelve los valores de Longitud y Latitud de una Ciudad utilizando una Api Externa.")
def get_lat_long(city: str) -> str:
    """
    Obtiene la latitud y longitud de una ciudad utilizando la API de Open Meteo.
    
    Args:
        city (str): Nombre de la ciudad.
    
    Returns:
        str: Latitud y longitud de la ciudad en formato JSON.
    """
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
    
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        # Verifica si la respuesta es exitosa
        if response.status_code == 200:
            lat = data["results"][0]['latitude']
            lon = data["results"][0]['longitude']
            return json.dumps({"lat": lat, "lon": lon})
        else:
            return f"Error: {data['message']}"
    except Exception as e:
        return f"Error al obtener datos: {e}"

@mcp.tool(description="Devuelve el clima actual de una ciudad utilizando una Api Externa.")
def get_wheather(lat: str, lon: str) -> str:
    """
    Obtiene el clima actual de una ciudad utilizando la API de Open Meteo.
    
    Args:
        lat (str): Latitud de la ciudad.
        lon (str): Longitud de la ciudad.
    
    Returns:
        str: Clima actual de la ciudad en formato JSON.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,weather_code&hourly=temperature_2m&timezone=auto&forecast_days=1"
    
    try:
        response = requests.get(url)
        data = json.loads(response.text)
        # Verifica si la respuesta es exitosa
        if response.status_code == 200:
            return json.dumps(data, indent=2)
        else:
            return f"Error: {data['message']}"
    except Exception as e:
        return f"Error al obtener datos: {e}"

@mcp.tool(description="Registra datos de tiempo real en la base de datos PostgreSQL.")
def register_real_time_data() -> str:
    """
    Registra datos de tiempo real en la base de datos PostgreSQL.
    
    Returns:
        str: Mensaje de éxito o error.
    """
    try:
        cursor.execute("""
            COPY sensor_data(Dia, Hora, LdrValorAnalog, LdrVoltaje, LdrResistencia, Temperatura, Humedad)
            FROM 'd:/UNI/6TO CICLO/ANALITICA DE DATOS/Proyecto SI150/PC2/datos_arduino_simulado.csv'
            DELIMITER ','
            CSV HEADER;
        """)
        conn.commit()
        return "Datos registrados exitosamente."
    except Exception as e:
        conn.rollback()
        return f"Error al registrar datos: {e}"
    
@mcp.tool(description="Elimina duplicados por una ejecucion incorrecta de la herramienta de register.")
def eliminar_duplicados() -> str:
    """
    Elimina duplicados en la tabla sensor_data.
    
    Returns:
        str: Mensaje de éxito o error.
    """
    try:
        cursor.execute("""
            DELETE FROM sensor_data
            WHERE ctid NOT IN (
                SELECT MIN(ctid)
                FROM sensor_data
                GROUP BY Dia, Hora, LdrValorAnalog, LdrVoltaje, LdrResistencia, Temperatura, Humedad
            );
        """)
        conn.commit()
        return "Duplicados eliminados exitosamente."
    except Exception as e:
        conn.rollback()
        return f"Error al eliminar duplicados: {e}"

@mcp.tool(name="query", description="Ejecuta una consulta SQL en la base de datos PostgreSQL, es una base de datos sobre el clima.")
def run_query(sql: str) -> str:
    """
    Ejecuta una consulta SQL en la base de datos PostgreSQL y devuelve los resultados en formato JSON.
    Args:
        sql (str): Una query SQL válida. Solo se permiten consultas de lectura.
    
    Returns:
        str: Resultados de la consulta en formato JSON.
    """
    try:
        cursor.execute("BEGIN TRANSACTION READ ONLY;")
        cursor.execute(sql)
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]
        cursor.execute("ROLLBACK;")
        return json.dumps(results, indent=2)
    except Exception as e:
        cursor.execute("ROLLBACK;")
        return f"Error executing query: {e}"



@mcp.resource("columns://data")
def get_table_columns() -> str:
    """
    Retorna las columnas de una tabla dada. Aparte se da el nombre de la tabla "sensor_data"
    
    Returns:
        str: Json de los nombres de las columnas y sus tipos de datos.
    """
    return {
        "hora": "time",
        "dia": "date",
        "temperatura": "float",
        "ldrvaloranalog":"float",
        "ldrvoltaje":"float",
        "ldresistencia":"float",
        "humedad": "integer",
    }

@mcp.resource("data://table")
def get_nombre_tabla() -> str:
    """
    Retorna el nombre de la tabla.
    Args:
        table (str): Nombre de la tabla en la base de datos.

    Returns:
        str: Nombre de la tabla.
    """
    return f"Nombre de la tabla: sensor_data"

@mcp.prompt()
def viabilidad_destino(destino:str) -> str:
    return [
        base.UserMessage("Necesito recomendaciones sobre el clima. Pero no se si es viable. debido a los datos que tienes"),
        base.UserMessage(f"Entonces, quiero ir a, {destino}, que me puedes recomendar?"),
    ] 
