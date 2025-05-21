from data_loader import load_data, join_tables

def get_ev_metrics():
    data = load_data()
    ev_impact, _ = join_tables(data)
    total_evs = int(ev_impact["TOTAL_EVS"].sum())
    bev = int(ev_impact["BEV_COUNT"].sum())
    phev = int(ev_impact["PHEV_COUNT"].sum())
    bev_percentage = round((bev / total_evs) * 100, 1) if total_evs else 0

    return {
        "total_evs": total_evs,
        "bev": bev,
        "phev": phev,
        "bev_percentage": bev_percentage
    }
