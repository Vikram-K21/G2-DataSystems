import pandas as pd

def load_data():
    #Load all dimension and fact tables from CSV.
    data = {
        "dim_time": pd.read_csv("extracted/time_dim.csv"),
        "dim_suburb": pd.read_csv("extracted/suburb_dim.csv"),
        "dim_vehicle_type": pd.read_csv("extracted/vehicle_dim.csv"),
        "dim_fuel_type": pd.read_csv("extracted/fuel_dim.csv"),
        "fact_ev_impact": pd.read_csv("extracted/ev_fact.csv"),
        "fact_energy_pollution": pd.read_csv("extracted/energy_fact.csv")
    }
    return data

def join_tables(data):
    #Join dimensions with fact tables.
    ev_impact = pd.merge(
        data["fact_ev_impact"],
        data["dim_suburb"],
        on="SUBURB_KEY",
        how="left"
    )

    energy_pollution = pd.merge(
        data["fact_energy_pollution"],
        data["dim_suburb"],
        on="SUBURB_KEY",
        how="left"
    )

    return ev_impact, energy_pollution
