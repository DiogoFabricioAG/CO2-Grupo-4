# climate_db_server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

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


@mcp.tool(name="Registrar datos tiempo real", description="Registra datos de tiempo real en la base de datos PostgreSQL.")
def register_real_time_data(data: str) -> str:
    """
    Registra datos de tiempo real en la base de datos PostgreSQL.
    
    Args:
        data (str): Datos a registrar en formato JSON.
    
    Returns:
        str: Mensaje de éxito o error.
    """
    try:
        data_dict = json.loads(data)
        cursor.execute("""
            INSERT INTO weather_data (temperature, humidity, wind_speed, timestamp)
            VALUES (%s, %s, %s, NOW())
        """, (data_dict["temperature"], data_dict["humidity"], data_dict["wind_speed"]))
        conn.commit()
        return "Datos registrados exitosamente."
    except Exception as e:
        conn.rollback()
        return f"Error al registrar datos: {e}"
    

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



@mcp.resource("columns://{table}")
def get_table_schema(table: str) -> str:
    """
    Retorna las columnas y tipos de datos de una tabla dada.
    
    Args:
        table (str): Nombre de la tabla en la base de datos.
    
    Returns:
        str: Json de los nombres de las columnas y sus tipos de datos.
    """
    try:
        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = %s
        """, (table,))
        rows = cursor.fetchall()
        schema = [{"column": row[0], "type": row[1]} for row in rows]
        return json.dumps(schema, indent=2)
    except Exception as e:
        return f"Error fetching schema for table '{table}': {e}"
    

@mcp.prompt()
def viabilidad_destino(destino:str) -> str:
    return [
        base.UserMessage("Necesito recomendaciones sobre el clima. Pero no se si es viable. debido a los datos que tienes"),
        base.UserMessage(f"Entonces, quiero ir a, {destino}, que me puedes recomendar?"),
    ] 
