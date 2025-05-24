import pyodbc
import os
import pandas as pd
import numpy as np
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

def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    return obj

def dataframe_to_json_serializable(df):
    """Convert DataFrame to JSON serializable format."""
    # Replace NaN values with None
    df = df.where(pd.notnull(df), None)
    
    # Convert to dict and handle numpy types
    records = df.to_dict(orient='records')
    
    # Convert numpy types to native Python types
    for record in records:
        for key, value in record.items():
            record[key] = convert_numpy_types(value)
    
    return records

def get_table_data(table_name, limit=None, columns=None, where_clause=None):
    """Get data from a specific table. Loads entire table by default."""
    try:
        # Build the query
        cols = "*" if not columns else ", ".join(columns)
        
        # Only add TOP clause if limit is specified
        limit_clause = f"TOP {limit}" if limit else ""
        where_str = f"WHERE {where_clause}" if where_clause else ""
        
        # Keep the dbo. schema prefix as it worked before
        query = f"SELECT {limit_clause} {cols} FROM dbo.{table_name} {where_str}".strip()
        
        print(f"Executing query: {query}")  # Debug print to see the actual query
        
        return execute_query(query)
    except Exception as e:
        print(f"Error getting data from {table_name}: {e}")
        raise

def check_table_exists(table_name):
    """Check if a table exists in the dbo schema."""
    try:
        query = """
        SELECT COUNT(*) as table_count
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = ? AND TABLE_SCHEMA = 'dbo'
        """
        df = execute_query(query, params=[table_name])
        return bool(df.iloc[0]['table_count'] > 0)  # Explicitly convert to Python bool
    except Exception as e:
        print(f"Error checking if table {table_name} exists: {e}")
        return False

def get_all_tables():
    """Get list of all tables in the database."""
    try:
        query = """
        SELECT 
            TABLE_SCHEMA,
            TABLE_NAME,
            TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_SCHEMA, TABLE_NAME
        """
        df = execute_query(query)
        return dataframe_to_json_serializable(df)
    except Exception as e:
        print(f"Error getting table list: {e}")
        raise

def get_table_schema(table_name):
    """Get the schema/structure of a specific table in dbo schema."""
    try:
        query = """
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ? AND TABLE_SCHEMA = 'dbo'
        ORDER BY ORDINAL_POSITION
        """
        df = execute_query(query, params=[table_name])
        return dataframe_to_json_serializable(df)
    except Exception as e:
        print(f"Error getting schema for table {table_name}: {e}")
        raise

def get_table_row_count(table_name):
    """Get the number of rows in a table."""
    try:
        query = f"SELECT COUNT(*) as row_count FROM dbo.{table_name}"
        df = execute_query(query)
        return int(df.iloc[0]['row_count'])  # Explicitly convert to Python int
    except Exception as e:
        print(f"Error getting row count for {table_name}: {e}")
        raise
