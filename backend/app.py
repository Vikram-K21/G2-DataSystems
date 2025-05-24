from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
import re

# Load .env variables
load_dotenv()

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

# Whitelist of allowed tables for security
ALLOWED_TABLES = {
    'energy_fact',
    'ev_fact', 
    'fuel_dim',
    'suburb_dim',
    'time_dim',
    'vehicle_dim'
}

# API Routes

@app.route('/api/dashboard-data')
def dashboard_data():
    """Get all data needed for dashboard initialization."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        # Energy metrics - using actual column names
        energy_query = """
        SELECT 
            COUNT(*) as total_records,
            AVG(ENERGY_CONSUMPTION) as avg_energy_consumption,
            SUM(ENERGY_CONSUMPTION) as total_energy_consumption,
            AVG(NO2_LEVEL) as avg_no2_level,
            AVG(EV_PER_ENERGY_UNIT) as avg_ev_per_energy_unit
        FROM dbo.energy_fact
        WHERE ENERGY_CONSUMPTION IS NOT NULL
        """
        energy_df = execute_query(energy_query)
        energy_data = dataframe_to_json_serializable(energy_df)[0]
        
        # EV metrics
        ev_query = """
        SELECT 
            SUM(TOTAL_EVS) as total_evs,
            SUM(BEV_COUNT) as bev_count,
            SUM(PHEV_COUNT) as phev_count,
            COUNT(*) as total_records
        FROM dbo.ev_fact
        """
        ev_df = execute_query(ev_query)
        ev_data = dataframe_to_json_serializable(ev_df)[0]
        
        # Calculate percentages
        total_evs = ev_data['total_evs'] if ev_data['total_evs'] else 0
        bev_count = ev_data['bev_count'] if ev_data['bev_count'] else 0
        phev_count = ev_data['phev_count'] if ev_data['phev_count'] else 0
        
        dashboard_data = {
            'energy': {
                'total_records': energy_data['total_records'] or 0,
                'avg_energy_consumption': round(energy_data['avg_energy_consumption'] or 0, 2),
                'total_energy_consumption': round(energy_data['total_energy_consumption'] or 0, 2),
                'avg_no2_level': round(energy_data['avg_no2_level'] or 0, 2),
                'avg_ev_per_energy_unit': round(energy_data['avg_ev_per_energy_unit'] or 0, 4)
            },
            'ev': {
                'total_evs': total_evs,
                'bev_count': bev_count,
                'phev_count': phev_count,
                'total_records': ev_data['total_records'] or 0,
                'bev_percentage': round((bev_count / total_evs * 100) if total_evs > 0 else 0, 1),
                'phev_percentage': round((phev_count / total_evs * 100) if total_evs > 0 else 0, 1)
            }
        }
        
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/energy-trends')
def energy_trends():
    """Get energy consumption trends by year."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            t.YEAR,
            COUNT(*) as record_count,
            AVG(e.ENERGY_CONSUMPTION) as avg_energy_consumption,
            SUM(e.ENERGY_CONSUMPTION) as total_energy_consumption,
            AVG(e.NO2_LEVEL) as avg_no2_level,
            AVG(e.ENERGY_CHANGE_PCT) as avg_energy_change_pct
        FROM dbo.energy_fact e
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        WHERE e.ENERGY_CONSUMPTION IS NOT NULL
        GROUP BY t.YEAR
        ORDER BY t.YEAR
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round the float values for better display
        for row in result:
            if row['avg_energy_consumption']:
                row['avg_energy_consumption'] = round(row['avg_energy_consumption'], 2)
            if row['total_energy_consumption']:
                row['total_energy_consumption'] = round(row['total_energy_consumption'], 2)
            if row['avg_no2_level']:
                row['avg_no2_level'] = round(row['avg_no2_level'], 2)
            if row['avg_energy_change_pct']:
                row['avg_energy_change_pct'] = round(row['avg_energy_change_pct'], 2)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ev-trends')
def ev_trends():
    """Get EV adoption trends by year."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            t.YEAR,
            SUM(e.TOTAL_EVS) as total_evs,
            SUM(e.BEV_COUNT) as bev_count,
            SUM(e.PHEV_COUNT) as phev_count,
            COUNT(*) as record_count
        FROM dbo.ev_fact e
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        GROUP BY t.YEAR
        ORDER BY t.YEAR
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/suburb-data')
def suburb_data():
    """Get data by suburb with optional filtering."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        year = request.args.get('year', type=int)
        
        # Build the query with joins - using correct column names
        where_clause = ""
        if year:
            where_clause = f"WHERE t.YEAR = {year}"
        
        query = f"""
        SELECT TOP {limit}
            s.SUBURB_NAME,
            t.YEAR,
            COUNT(*) as energy_records,
            AVG(e.ENERGY_CONSUMPTION) as avg_energy_consumption,
            AVG(e.NO2_LEVEL) as avg_no2_level,
            AVG(e.EV_PER_ENERGY_UNIT) as avg_ev_per_energy_unit
        FROM dbo.energy_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        {where_clause}
        GROUP BY s.SUBURB_NAME, t.YEAR
        ORDER BY avg_energy_consumption DESC
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round float values
        for row in result:
            if row['avg_energy_consumption']:
                row['avg_energy_consumption'] = round(row['avg_energy_consumption'], 2)
            if row['avg_no2_level']:
                row['avg_no2_level'] = round(row['avg_no2_level'], 2)
            if row['avg_ev_per_energy_unit']:
                row['avg_ev_per_energy_unit'] = round(row['avg_ev_per_energy_unit'], 4)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/energy-data")
def energy_data():
    """Get energy data with optional filtering."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        # Get query parameters
        year = request.args.get('year', type=int)
        suburb = request.args.get('suburb')
        limit = request.args.get('limit', 100, type=int)
        
        # Build where clause
        where_clauses = []
        if year:
            where_clauses.append(f"t.YEAR = {year}")
        if suburb:
            where_clauses.append(f"s.SUBURB_NAME LIKE '%{suburb}%'")
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get the data with joins - using correct column names
        query = f"""
        SELECT TOP {limit}
            e.energy_fact_id,
            e.ENERGY_CONSUMPTION,
            e.ENERGY_CHANGE_PCT,
            e.NO2_LEVEL,
            e.NO2_CHANGE,
            e.NO2_CHANGE_PCT,
            e.EV_PER_ENERGY_UNIT,
            e.NO2_PER_EV,
            s.SUBURB_NAME,
            t.YEAR,
            t.IS_CURRENT_YEAR
        FROM dbo.energy_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        WHERE {where_clause}
        ORDER BY t.YEAR DESC, s.SUBURB_NAME
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        return jsonify({
            "filters": {
                "year": year,
                "suburb": suburb,
                "limit": limit
            },
            "row_count": len(result),
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ev-price-scatter', methods=['GET'])
def ev_price_scatter():
    """Get EV adoption vs average price scatter plot data."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            s.SUBURB_NAME,
            AVG(e.AVG_PRICE) as avg_price,
            SUM(e.TOTAL_EVs) as total_evs
        FROM dbo.ev_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        WHERE e.AVG_PRICE IS NOT NULL 
        AND e.TOTAL_EVs IS NOT NULL 
        AND e.TOTAL_EVs > 0
        GROUP BY s.SUBURB_NAME
        HAVING AVG(e.AVG_PRICE) > 0
        ORDER BY total_evs DESC
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round values for better display
        for row in result:
            if row['avg_price']:
                row['avg_price'] = round(row['avg_price'], 0)
            if row['total_evs']:
                row['total_evs'] = round(row['total_evs'], 1)
        
        return jsonify({
            "data": result,
            "x_key": "avg_price",
            "y_key": "total_evs"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/ev-range-scatter', methods=['GET'])
def ev_range_scatter():
    """Get EV adoption vs average range scatter plot data."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            s.SUBURB_NAME,
            AVG(e.AVG_RANGE_KM) as avg_range,
            SUM(e.TOTAL_EVs) as total_evs
        FROM dbo.ev_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        WHERE e.AVG_RANGE_KM IS NOT NULL 
        AND e.TOTAL_EVs IS NOT NULL 
        AND e.TOTAL_EVs > 0
        GROUP BY s.SUBURB_NAME
        HAVING AVG(e.AVG_RANGE_KM) > 0
        ORDER BY total_evs DESC
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round values for better display
        for row in result:
            if row['avg_range']:
                row['avg_range'] = round(row['avg_range'], 1)
            if row['total_evs']:
                row['total_evs'] = round(row['total_evs'], 1)
        
        return jsonify({
            "data": result,
            "x_key": "avg_range",
            "y_key": "total_evs"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/energy-vs-no2', methods=['GET'])
def energy_vs_no2():
    """Get energy consumption vs NO2 pollution data."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            s.SUBURB_NAME,
            AVG(en.ENERGY_CONSUMPTION) as ENERGY_CONSUMPTION,
            AVG(en.NO2_LEVEL) as NO2_LEVEL
        FROM dbo.energy_fact en
        JOIN dbo.suburb_dim s ON en.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON en.time_id = t.time_id
        WHERE en.ENERGY_CONSUMPTION IS NOT NULL
        AND en.NO2_LEVEL IS NOT NULL
        GROUP BY s.SUBURB_NAME
        HAVING AVG(en.ENERGY_CONSUMPTION) > 0 AND AVG(en.NO2_LEVEL) > 0
        ORDER BY s.SUBURB_NAME
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round values for better display
        for row in result:
            if row['ENERGY_CONSUMPTION']:
                row['ENERGY_CONSUMPTION'] = round(row['ENERGY_CONSUMPTION'], 2)
            if row['NO2_LEVEL']:
                row['NO2_LEVEL'] = round(row['NO2_LEVEL'], 2)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/no2-trends', methods=['GET'])
def no2_trends():
    """Get NO2 levels over years by suburb."""
    try:
        from db_helper import dataframe_to_json_serializable
        from flask import request
        
        # Get years from query parameters, default to 2022 and 2023
        years = request.args.getlist('years')
        if not years:
            years = ['2022', '2023']
        
        # Convert to integers and create SQL IN clause
        year_list = [int(year) for year in years]
        year_placeholders = ','.join(['?' for _ in year_list])
        
        query = f"""
        SELECT 
            s.SUBURB_NAME,
            t.YEAR,
            AVG(en.NO2_LEVEL) as NO2_LEVEL
        FROM dbo.energy_fact en
        JOIN dbo.suburb_dim s ON en.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON en.time_id = t.time_id
        WHERE en.NO2_LEVEL IS NOT NULL
        AND t.YEAR IN ({year_placeholders})
        GROUP BY s.SUBURB_NAME, t.YEAR
        HAVING AVG(en.NO2_LEVEL) > 0
        ORDER BY t.YEAR, s.SUBURB_NAME
        """
        
        df = execute_query(query, params=year_list)
        result = dataframe_to_json_serializable(df)
        
        # Round values for better display
        for row in result:
            if row['NO2_LEVEL']:
                row['NO2_LEVEL'] = round(row['NO2_LEVEL'], 2)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ev-distribution', methods=['GET'])
def ev_distribution():
    """Get EV distribution by suburb (Top 10) split by BEV and PHEV."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        WITH SuburbTotals AS (
            SELECT 
                s.SUBURB_NAME,
                SUM(e.TOTAL_EVs) as total_evs
            FROM dbo.ev_fact e
            JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
            WHERE e.TOTAL_EVs IS NOT NULL AND e.TOTAL_EVs > 0
            GROUP BY s.SUBURB_NAME
        ),
        TopSuburbs AS (
            SELECT TOP 10 SUBURB_NAME
            FROM SuburbTotals
            ORDER BY total_evs DESC
        )
        SELECT 
            s.SUBURB_NAME,
            e.FUEL_TYPE,
            SUM(e.TOTAL_EVs) as total_evs
        FROM dbo.ev_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        WHERE e.TOTAL_EVs IS NOT NULL 
        AND e.TOTAL_EVs > 0
        AND s.SUBURB_NAME IN (SELECT SUBURB_NAME FROM TopSuburbs)
        AND e.FUEL_TYPE IN ('BEV', 'PHEV')
        GROUP BY s.SUBURB_NAME, e.FUEL_TYPE
        ORDER BY s.SUBURB_NAME, e.FUEL_TYPE
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Get top 10 suburbs by total EVs first
        suburb_totals = {}
        for row in result:
            suburb = row['SUBURB_NAME']
            count = int(row['total_evs'])
            if suburb not in suburb_totals:
                suburb_totals[suburb] = 0
            suburb_totals[suburb] += count
        
        # Sort suburbs by total and take top 10
        top_suburbs = sorted(suburb_totals.items(), key=lambda x: x[1], reverse=True)[:10]
        top_suburb_names = [suburb[0] for suburb in top_suburbs]
        
        # Organize data by suburb and fuel type
        suburbs = {}
        for suburb_name in top_suburb_names:
            suburbs[suburb_name] = {'BEV': 0, 'PHEV': 0}
        
        for row in result:
            suburb = row['SUBURB_NAME']
            if suburb in suburbs:
                fuel_type = row['FUEL_TYPE']
                count = int(row['total_evs'])
                suburbs[suburb][fuel_type] = count
        
        # Create the format expected by the component
        labels = top_suburb_names
        bev_data = [suburbs[suburb]['BEV'] for suburb in labels]
        phev_data = [suburbs[suburb]['PHEV'] for suburb in labels]
        
        return jsonify({
            "labels": labels,
            "bev_data": bev_data,
            "phev_data": phev_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Also add an endpoint to get EV summary by fuel type
@app.route('/api/ev-summary-by-fuel')
def ev_summary_by_fuel():
    """Get EV summary grouped by fuel type."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            e.FUEL_TYPE,
            t.YEAR,
            SUM(e.TOTAL_EVs) as total_evs,
            AVG(e.AVG_RANGE_KM) as avg_range_km,
            AVG(e.AVG_PRICE) as avg_price,
            AVG(e.EV_ADOPTION_SCORE) as avg_adoption_score,
            COUNT(*) as record_count,
            COUNT(DISTINCT s.suburb_id) as suburb_count
        FROM dbo.ev_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        WHERE e.TOTAL_EVs IS NOT NULL AND e.TOTAL_EVs > 0
        GROUP BY e.FUEL_TYPE, t.YEAR
        ORDER BY t.YEAR DESC, total_evs DESC
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round float values
        for row in result:
            if row['total_evs']:
                row['total_evs'] = round(row['total_evs'], 1)
            if row['avg_range_km']:
                row['avg_range_km'] = round(row['avg_range_km'], 1)
            if row['avg_price']:
                row['avg_price'] = round(row['avg_price'], 0)
            if row['avg_adoption_score']:
                row['avg_adoption_score'] = round(row['avg_adoption_score'], 2)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/environmental-impact')
def environmental_impact():
    """Get environmental impact data showing relationship between energy and NO2."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            s.SUBURB_NAME,
            t.YEAR,
            AVG(e.ENERGY_CONSUMPTION) as avg_energy_consumption,
            AVG(e.NO2_LEVEL) as avg_no2_level,
            AVG(e.NO2_CHANGE_PCT) as avg_no2_change_pct,
            AVG(e.EV_PER_ENERGY_UNIT) as avg_ev_per_energy_unit,
            AVG(e.NO2_PER_EV) as avg_no2_per_ev
        FROM dbo.energy_fact e
        JOIN dbo.suburb_dim s ON e.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON e.time_id = t.time_id
        WHERE e.ENERGY_CONSUMPTION IS NOT NULL 
        AND e.NO2_LEVEL IS NOT NULL
        GROUP BY s.SUBURB_NAME, t.YEAR
        ORDER BY t.YEAR, avg_energy_consumption DESC
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round float values
        for row in result:
            for key in ['avg_energy_consumption', 'avg_no2_level', 'avg_no2_change_pct', 'avg_ev_per_energy_unit', 'avg_no2_per_ev']:
                if row[key] is not None:
                    row[key] = round(row[key], 4)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/ev-efficiency-analysis', methods=['GET'])
def ev_efficiency_analysis():
    """Analyze EV efficiency (EVs per energy unit) vs NO2 reduction."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            s.SUBURB_NAME,
            t.YEAR,
            AVG(en.EV_PER_ENERGY_UNIT) as EV_EFFICIENCY,
            AVG(en.NO2_CHANGE_PCT) as NO2_REDUCTION_PCT,
            AVG(en.ENERGY_CHANGE_PCT) as ENERGY_CHANGE_PCT,
            AVG(en.NO2_PER_EV) as NO2_PER_EV
        FROM dbo.energy_fact en
        JOIN dbo.suburb_dim s ON en.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON en.time_id = t.time_id
        WHERE en.EV_PER_ENERGY_UNIT IS NOT NULL
        AND en.NO2_CHANGE_PCT IS NOT NULL
        GROUP BY s.SUBURB_NAME, t.YEAR
        ORDER BY t.YEAR DESC, EV_EFFICIENCY DESC
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round values for better display
        for row in result:
            if row['EV_EFFICIENCY']:
                row['EV_EFFICIENCY'] = round(row['EV_EFFICIENCY'], 6)
            if row['NO2_REDUCTION_PCT']:
                row['NO2_REDUCTION_PCT'] = round(row['NO2_REDUCTION_PCT'], 2)
            if row['ENERGY_CHANGE_PCT']:
                row['ENERGY_CHANGE_PCT'] = round(row['ENERGY_CHANGE_PCT'], 2)
            if row['NO2_PER_EV']:
                row['NO2_PER_EV'] = round(row['NO2_PER_EV'], 3)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/energy-environmental-impact', methods=['GET'])
def energy_environmental_impact():
    """Compare energy consumption changes with environmental impact."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT 
            s.SUBURB_NAME,
            AVG(en.ENERGY_CONSUMPTION) as AVG_ENERGY_CONSUMPTION,
            AVG(en.ENERGY_CHANGE_PCT) as ENERGY_CHANGE_PCT,
            AVG(en.NO2_LEVEL) as AVG_NO2_LEVEL,
            AVG(en.NO2_CHANGE_PCT) as NO2_CHANGE_PCT,
            AVG(en.EV_PER_ENERGY_UNIT) as EV_EFFICIENCY,
            COUNT(*) as data_points
        FROM dbo.energy_fact en
        JOIN dbo.suburb_dim s ON en.suburb_id = s.suburb_id
        JOIN dbo.time_dim t ON en.time_id = t.time_id
        WHERE en.ENERGY_CONSUMPTION IS NOT NULL
        AND en.NO2_LEVEL IS NOT NULL
        GROUP BY s.SUBURB_NAME
        HAVING COUNT(*) > 1  -- Ensure we have multiple data points
        ORDER BY NO2_CHANGE_PCT ASC  -- Best NO2 improvement first
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        # Round values and add performance categories
        for row in result:
            if row['AVG_ENERGY_CONSUMPTION']:
                row['AVG_ENERGY_CONSUMPTION'] = round(row['AVG_ENERGY_CONSUMPTION'], 0)
            if row['ENERGY_CHANGE_PCT']:
                row['ENERGY_CHANGE_PCT'] = round(row['ENERGY_CHANGE_PCT'], 2)
            if row['AVG_NO2_LEVEL']:
                row['AVG_NO2_LEVEL'] = round(row['AVG_NO2_LEVEL'], 2)
            if row['NO2_CHANGE_PCT']:
                row['NO2_CHANGE_PCT'] = round(row['NO2_CHANGE_PCT'], 2)
            if row['EV_EFFICIENCY']:
                row['EV_EFFICIENCY'] = round(row['EV_EFFICIENCY'], 6)
            
            # Add performance category
            no2_change = row['NO2_CHANGE_PCT'] or 0
            if no2_change < -10:
                row['ENVIRONMENTAL_PERFORMANCE'] = 'Excellent'
            elif no2_change < 0:
                row['ENVIRONMENTAL_PERFORMANCE'] = 'Good'
            elif no2_change < 10:
                row['ENVIRONMENTAL_PERFORMANCE'] = 'Moderate'
            else:
                row['ENVIRONMENTAL_PERFORMANCE'] = 'Needs Improvement'
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Secure table access with whitelist
@app.route("/api/tables/<table_name>")
def get_table(table_name):
    """Get data from a specific table. Loads entire table by default."""
    
    # Security check - only allow whitelisted tables
    if table_name not in ALLOWED_TABLES:
        return jsonify({
            "error": f"Access to table '{table_name}' is not allowed",
            "allowed_tables": list(ALLOWED_TABLES)
        }), 403
    
    try:
        # Get query parameters - limit is optional now
        limit = request.args.get('limit', type=int)  # No default limit
        
        # Check if table exists first
        from db_helper import check_table_exists, get_table_row_count, dataframe_to_json_serializable
        
        if not check_table_exists(table_name):
            return jsonify({
                "error": f"Table dbo.{table_name} does not exist",
                "hint": "Use /api/list-tables to see available tables"
            }), 404
        
        # Get row count for info
        row_count = get_table_row_count(table_name)
        
        # Get the data (entire table unless limit specified)
        from db_helper import get_table_data
        df = get_table_data(table_name, limit=limit)
        
        # Convert to JSON serializable format
        result = dataframe_to_json_serializable(df)
        
        return jsonify({
            "table_name": f"dbo.{table_name}",
            "total_rows_in_table": row_count,
            "rows_returned": len(result),
            "limited": limit is not None,
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Updated list tables to show only allowed tables
@app.route("/api/list-tables")
def list_tables():
    """List all available tables in the database."""
    try:
        from db_helper import get_all_tables
        all_tables = get_all_tables()
        
        # Filter to only show allowed tables
        filtered_tables = []
        if isinstance(all_tables, dict) and 'tables' in all_tables:
            for table in all_tables['tables']:
                table_name = table.get('table_name', '').replace('dbo.', '')
                if table_name in ALLOWED_TABLES:
                    filtered_tables.append(table)
        
        return jsonify({
            "schema": "dbo",
            "allowed_tables_only": True,
            "tables": filtered_tables
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Check if the specified table exists in SQL database
@app.route("/api/check-table/<table_name>")
def check_table(table_name):
    """Check if a specific table exists in dbo schema."""
    
    # Security check - only allow whitelisted tables
    if table_name not in ALLOWED_TABLES:
        return jsonify({
            "error": f"Access to table '{table_name}' is not allowed",
            "allowed_tables": list(ALLOWED_TABLES)
        }), 403
    
    try:
        from db_helper import check_table_exists, get_table_row_count
        exists = check_table_exists(table_name)
        
        response = {
            "table_name": f"dbo.{table_name}",
            "exists": exists
        }
        
        if exists:
            try:
                response["row_count"] = get_table_row_count(table_name)
            except:
                response["row_count"] = "Unable to determine"
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Get info about a table in the SQL database    
@app.route("/api/table-info/<table_name>")
def table_info(table_name):
    """Get detailed information about a table."""
    
    # Security check - only allow whitelisted tables
    if table_name not in ALLOWED_TABLES:
        return jsonify({
            "error": f"Access to table '{table_name}' is not allowed",
            "allowed_tables": list(ALLOWED_TABLES)
        }), 403
    
    try:
        from db_helper import check_table_exists, get_table_schema, get_table_row_count
        
        if not check_table_exists(table_name):
            return jsonify({"error": f"Table dbo.{table_name} does not exist"}), 404
        
        schema_data = get_table_schema(table_name)  # This now returns JSON serializable data
        row_count = get_table_row_count(table_name)
        
        return jsonify({
            "table_name": f"dbo.{table_name}",
            "row_count": row_count,
            "columns": schema_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/explore/<table_name>")
def explore_table(table_name):
    """Explore a table to see sample data and column info."""
    
    # Security check - only allow whitelisted tables
    if table_name not in ALLOWED_TABLES:
        return jsonify({
            "error": f"Access to table '{table_name}' is not allowed",
            "allowed_tables": list(ALLOWED_TABLES)
        }), 403
    
    try:
        from db_helper import get_table_schema, get_table_data, dataframe_to_json_serializable
        
        # Get schema
        schema = get_table_schema(table_name)
        
        # Get sample data (first 5 rows)
        sample_df = get_table_data(table_name, limit=5)
        sample_data = dataframe_to_json_serializable(sample_df)
        
        return jsonify({
            "table_name": f"dbo.{table_name}",
            "schema": schema,
            "sample_data": sample_data,
            "column_names": [col['COLUMN_NAME'] for col in schema]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/schemas")
def get_all_schemas():
    """Get schemas for all allowed tables."""
    try:
        from db_helper import get_table_schema
        
        schemas = {}
        for table_name in ALLOWED_TABLES:
            try:
                schemas[table_name] = get_table_schema(table_name)
            except Exception as e:
                schemas[table_name] = {"error": str(e)}
        
        return jsonify(schemas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Secure custom query endpoint with basic SQL injection protection
@app.route("/api/custom-query", methods=['GET', 'POST'])
def custom_query():
    """Execute a custom query with security restrictions."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        # Get query from either GET or POST
        if request.method == 'POST':
            data = request.get_json()
            query = data.get('query') if data else None
        else:
            query = request.args.get('query')
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Basic security checks
        query_upper = query.upper().strip()
        
        # Only allow SELECT statements
        if not query_upper.startswith('SELECT'):
            return jsonify({"error": "Only SELECT statements are allowed"}), 400
        
        # Block dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return jsonify({"error": f"Keyword '{keyword}' is not allowed"}), 400
        
        # Ensure query only references allowed tables
        query_words = re.findall(r'\b\w+\b', query_upper)
        referenced_tables = set()
        
        # Look for table references after FROM and JOIN
        for i, word in enumerate(query_words):
            if word in ['FROM', 'JOIN'] and i + 1 < len(query_words):
                next_word = query_words[i + 1]
                if next_word.startswith('DBO.'):
                    table_name = next_word[4:]  # Remove 'DBO.' prefix
                else:
                    table_name = next_word
                referenced_tables.add(table_name.lower())
        
        # Check if all referenced tables are allowed
        for table in referenced_tables:
            if table not in {t.lower() for t in ALLOWED_TABLES}:
                return jsonify({
                    "error": f"Access to table '{table}' is not allowed",
                    "allowed_tables": list(ALLOWED_TABLES)
                }), 403
        
        # Execute the query
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        
        return jsonify({
            "query": query,
            "row_count": len(result),
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        test_query = "SELECT 1 as test"
        execute_query(test_query)
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "allowed_tables": list(ALLOWED_TABLES)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 500

# Get available years for filtering
@app.route("/api/available-years")
def available_years():
    """Get all available years from the time dimension."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT DISTINCT YEAR 
        FROM dbo.time_dim 
        WHERE YEAR IS NOT NULL 
        ORDER BY YEAR
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        years = [row['YEAR'] for row in result]
        
        return jsonify({
            "years": years,
            "count": len(years)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get available suburbs for filtering
@app.route("/api/available-suburbs")
def available_suburbs():
    """Get all available suburbs."""
    try:
        from db_helper import dataframe_to_json_serializable
        
        query = """
        SELECT DISTINCT SUBURB_NAME 
        FROM dbo.suburb_dim 
        WHERE SUBURB_NAME IS NOT NULL 
        ORDER BY SUBURB_NAME
        """
        
        df = execute_query(query)
        result = dataframe_to_json_serializable(df)
        suburbs = [row['SUBURB_NAME'] for row in result]
        
        return jsonify({
            "suburbs": suburbs,
            "count": len(suburbs)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# --- Run the App ---

if __name__ == "__main__":
    app.run(debug=True)
    print(f"Connection string: {conn_str}")