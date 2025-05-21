from flask import Flask, jsonify, request
from flask_cors import CORS
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

@app.route('/api/ev_metrics')
def get_ev_metrics():
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

if __name__ == "__main__":
    app.run(debug=True)