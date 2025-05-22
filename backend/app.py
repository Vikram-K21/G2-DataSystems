from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

from metrics import get_ev_metrics
from data_loader import load_data, join_tables
from charts import (
    get_ev_distribution,
    get_ev_price_scatter,
    get_ev_range_scatter,
    get_energy_vs_no2_2023,
    get_no2_trends
)
from db_helper import get_table_data, execute_query

app = Flask(__name__)
CORS(app)

# IMPORTANT DATABASE CONFIG STUFF LOADING FROM ENV
DB_SERVER = os.getenv("DB_SERVER") 
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Connection string
conn_str = os.getenv("AZURE_SQL_CONNECTIONSTRING")

# API Routes
@app.route('/api/ev_metrics')
def ev_metrics():
    data = load_data()
    ev_data, _ = join_tables(data)
    metrics = {
        "total_evs": int(ev_data['TOTAL_EVS'].sum()),
        "bev": int(ev_data['BEV_COUNT'].sum()),
        "phev": int(ev_data['PHEV_COUNT'].sum()),
        "bev_percentage": round(ev_data['BEV_COUNT'].sum() / ev_data['TOTAL_EVS'].sum() * 100, 1)
    }
    return jsonify(metrics)

@app.route("/api/ev-distribution")
def ev_distribution():
    return jsonify(get_ev_distribution())

@app.route("/api/ev-price-scatter")
def ev_price_scatter():
    return jsonify(get_ev_price_scatter())

@app.route("/api/ev-range-scatter")
def ev_range_scatter():
    return jsonify(get_ev_range_scatter())

@app.route("/api/energy-vs-no2")
def energy_vs_no2():
    return jsonify(get_energy_vs_no2_2023())

@app.route("/api/no2-trends")
def no2_trends():
    return jsonify(get_no2_trends())

# New routes for direct table access

@app.route("/api/tables/<table_name>")
def get_table(table_name):
    """Get data from a specific table with optional parameters."""
    allowed_tables = [
        "energy_pollution_fact", "ev_impact_fact", "fuel_type_fact",
        "suburb_dim", "time_dim", "vehicle_type_dim", "energy_fact"
    ]
    
    if table_name not in allowed_tables:
        return jsonify({"error": "Invalid table name"}), 400
    
    try:
        # Get query parameters
        limit = request.args.get('limit', default=100, type=int)
        
        # Get the data
        df = get_table_data(table_name, limit=limit)
        
        # Convert to list of dictionaries for JSON response
        result = df.to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/custom-query")
def custom_query():
    """Execute a custom query with parameters."""
    try:
        # This should be secured in production to prevent SQL injection
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        df = execute_query(query)
        result = df.to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example of a specific data endpoint
@app.route("/api/energy-data")
def energy_data():
    """Get energy data with optional filtering."""
    try:
        # Get query parameters
        year = request.args.get('year')
        suburb = request.args.get('suburb')
        
        # Build where clause
        where_clauses = []
        if year:
            where_clauses.append(f"year = {year}")
        if suburb:
            where_clauses.append(f"suburb_id = '{suburb}'")
        
        where_clause = " AND ".join(where_clauses) if where_clauses else None
        
        # Get the data
        df = get_table_data("energy_fact", where_clause=where_clause)
        
        # Convert to list of dictionaries for JSON response
        result = df.to_dict(orient='records')
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the App ---

if __name__ == "__main__":
    app.run(debug=True)
    print(conn_str)