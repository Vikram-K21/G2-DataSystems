import pyodbc
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connection string
conn_str = os.getenv("AZURE_SQL_CONNECTIONSTRING")

def get_db_connection():
    """Create and return a connection to the database."""
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise

def execute_query(query, params=None):
    """Execute a query and return the results as a pandas DataFrame."""
    try:
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"Error executing query: {e}")
        raise

def get_table_data(table_name, limit=None, columns=None, where_clause=None):
    """Get data from a specific table."""
    try:
        # Build the query
        cols = "*" if not columns else ", ".join(columns)
        limit_clause = f"TOP {limit}" if limit else ""
        where_str = f"WHERE {where_clause}" if where_clause else ""
        
        query = f"SELECT {limit_clause} {cols} FROM dbo.{table_name} {where_str}"
        
        return execute_query(query)
    except Exception as e:
        print(f"Error getting data from {table_name}: {e}")
        raise