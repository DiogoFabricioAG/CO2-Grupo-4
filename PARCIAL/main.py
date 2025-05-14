# main.py
from mcp.server.fastmcp import FastMCP
import os
import psycopg2
import json
# Create an MCP server
mcp = FastMCP("pg-server", "0.1.0")
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

@mcp.tool(name="query", description="Run a read-only SQL query on the PostgreSQL database")
def run_query(sql: str) -> str:
    """
    Executes a read-only SQL query and returns the result as JSON string.
    
    Args:
        sql (str): A SELECT SQL query.
    
    Returns:
        str: Query results in JSON format.
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
    Returns the column names and data types of a given table.
    
    Args:
        table (str): Table name
    
    Returns:
        str: JSON array of columns with names and types
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