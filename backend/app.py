from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import pyodbc
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

# Table preview route just forp experimentation

@app.route("/api/<table_name>")
def get_table_data(table_name):
    allowed_tables = [
        "energy_pollution_fact", "ev_impact_fact", "fuel_type_fact",
        "suburb_dim", "time_dim", "vehicle_type_dim"
    ]
    if table_name not in allowed_tables:
        return jsonify({"error": "Invalid table name"}), 400

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        query = f"SELECT TOP 5 * FROM dbo.{table_name}"
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the App ---

if __name__ == "__main__":
    app.run(debug=True)
    print(conn_str)