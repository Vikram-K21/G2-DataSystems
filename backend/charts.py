from data_loader import load_data, join_tables

def get_ev_distribution():
    data = load_data()
    ev_impact, _ = join_tables(data)
    ev_by_suburb = ev_impact.sort_values(by="TOTAL_EVS", ascending=False)

    return ev_by_suburb[[
        "SUBURB_NAME", "TOTAL_EVS", "BEV_COUNT", "PHEV_COUNT"
    ]].to_dict(orient="records")

def get_ev_price_scatter():
    data = load_data()
    ev_impact, _ = join_tables(data)
    return ev_impact[[
        "SUBURB_NAME", "AVG_PRICE", "TOTAL_EVS"
    ]].to_dict(orient="records")

def get_ev_range_scatter():
    data = load_data()
    ev_impact, _ = join_tables(data)
    return ev_impact[[
        "SUBURB_NAME", "AVG_RANGE_KM", "TOTAL_EVS"
    ]].to_dict(orient="records")

def get_energy_vs_no2_2023():
    data = load_data()
    _, energy = join_tables(data)
    df = energy[energy['YEAR'] == 2023].dropna(subset=["ENERGY_CONSUMPTION", "NO2_LEVEL"])
    return df[["SUBURB_NAME", "ENERGY_CONSUMPTION", "NO2_LEVEL"]].to_dict(orient="records")

def get_no2_trends():
    data = load_data()
    _, energy = join_tables(data)
    df = energy.dropna(subset=["YEAR", "NO2_LEVEL"])
    return df[["SUBURB_NAME", "YEAR", "NO2_LEVEL"]].to_dict(orient="records")
