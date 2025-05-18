import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Page configuration
st.set_page_config(
    page_title="EV Impact Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS for the dashboard
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4CAF50;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2196F3;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to load data from CSV files - please do NOT change names of CSVs because it may cause confusion
@st.cache_data
def load_data():
    try:
        data = {}
        data["dim_time"] = pd.read_csv(r'extracted\time_dim.csv')
        data["dim_suburb"] = pd.read_csv(r'extracted\suburb_dim.csv')
        data["dim_vehicle_type"] = pd.read_csv(r'extracted\vehicle_dim.csv')
        data["dim_fuel_type"] = pd.read_csv(r'extracted\fuel_dim.csv')
        data["fact_ev_impact"] = pd.read_csv(r'extracted\ev_fact.csv')
        data["fact_energy_pollution"] = pd.read_csv(r'extracted\energy_fact.csv')
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Function to join dimension and fact tables
def join_tables(data):
    """Join dimension and fact tables for analysis"""
    # Join suburb dimension with EV impact fact
    ev_impact_with_suburb = pd.merge(
        data["fact_ev_impact"],
        data["dim_suburb"],
        left_on="SUBURB_KEY",
        right_on="SUBURB_KEY",
        how="left"
    )
    
    # Join suburb dimension with energy pollution fact
    energy_pollution_with_suburb = pd.merge(
        data["fact_energy_pollution"],
        data["dim_suburb"],
        left_on="SUBURB_KEY",
        right_on="SUBURB_KEY",
        how="left"
    )
    
    return ev_impact_with_suburb, energy_pollution_with_suburb



        # !!! #
### MAIN PAGE CODE BELOW ###
        # !!! #


# Main function
def main():
    # Top page

    st.title(":blue[EcoWatt]")

    # st.header("In Sydney, ever since the introduction of electric vehicles (EVs), have they made any impact on the reducing the amount of pollution yearly?")
    st.markdown("<h1 style='text-align: center;padding-top:240px;'>In Sydney, ever since the introduction of electric vehicles (EVs), have they made any impact on the reducing the amount of pollution yearly?</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>The answer is yes, but not as much as we would like to see.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;padding-bottom:340px;'>Below, shows some stats based off recent data from Sydney Power and Car registration data.</p>", unsafe_allow_html=True)
    # st.markdown('<p class="main-header">EV Impact & Environmental Analysis Dashboard</p>', unsafe_allow_html=True)
    
    st.write("""
    This dashboard analyzes the relationship between electric vehicle adoption, 
    electricity consumption, and pollution levels across different suburbs.
    """)

    ###################
    # !!- LOAD DATA -!! 
    ###################

    # Load data
    data = load_data()
    
    if data is None:
        st.error("Failed to load data. Please check that your CSV files exist in the correct location.")
        return
    
    # Join tables
    ev_impact_with_suburb, energy_pollution_with_suburb = join_tables(data)

    ###################
    # !!- SHOW DATA -!! 
    ###################

    # Dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "EV Adoption Overview", 
        "Environmental Impact", 
        "Suburb Analysis",
        "Data Explorer"
    ])

    # TAB 1: EV Adoption Overview
    
    with tab1:
        st.markdown("<p style='text-align: center;padding-bottom:50px;padding-top:50px;'>ADD TEXT HERE.</p>", unsafe_allow_html=True)
        st.markdown('<p class="sub-header">EV Adoption Metrics</p>', unsafe_allow_html=True)
        
        # Create metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total EVs", f"{int(ev_impact_with_suburb['TOTAL_EVS'].sum())}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Battery EVs (BEV)", f"{int(ev_impact_with_suburb['BEV_COUNT'].sum())}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Plug-in Hybrid EVs (PHEV)", f"{int(ev_impact_with_suburb['PHEV_COUNT'].sum())}")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            bev_percentage = (ev_impact_with_suburb['BEV_COUNT'].sum() / 
                            ev_impact_with_suburb['TOTAL_EVS'].sum()) * 100
            st.metric("BEV Percentage", f"{bev_percentage:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # EV Distribution by Suburb
        st.subheader("Battery EVs(BEV) and Plug-in Hybrid EVs(PHEV) Distribution by Suburb", divider="gray")
        
        # Sort for better visualization
        ev_by_suburb = ev_impact_with_suburb.sort_values(by="TOTAL_EVS", ascending=False)
        
        fig = px.bar(
            ev_by_suburb,
            x="SUBURB_NAME",
            y=["BEV_COUNT", "PHEV_COUNT"],
            labels={"value": "Number of Vehicles", "SUBURB_NAME": "Suburb", "variable": "EV Type"},
            color_discrete_map={"BEV_COUNT": "#2196F3", "PHEV_COUNT": "#4CAF50"},
            barmode="stack"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # EV Price and Range Analysis
        st.subheader("EV Price and Range Analysis", divider="gray")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.scatter(
                ev_impact_with_suburb,
                x="AVG_PRICE",
                y="TOTAL_EVS",
                size="TOTAL_EVS",
                color="SUBURB_NAME",
                hover_name="SUBURB_NAME",
                title="EV Adoption vs Average Price",
                labels={"AVG_PRICE": "Average EV Price ($)", "TOTAL_EVS": "Number of EVs"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = px.scatter(
                ev_impact_with_suburb,
                x="AVG_RANGE_KM",
                y="TOTAL_EVS",
                size="TOTAL_EVS",
                color="SUBURB_NAME",
                hover_name="SUBURB_NAME",
                title="EV Adoption vs Average Range",
                labels={"AVG_RANGE_KM": "Average Range (km)", "TOTAL_EVS": "Number of EVs"}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 2: Environmental Impact Analysis

    with tab2:
        st.markdown("<p style='text-align: center;padding-bottom:50px;padding-top:50px;'>ADD TEXT HERE.</p>", unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Environmental Impact Analysis</p>', unsafe_allow_html=True)
        
        # Filter for 2023 data for current analysis
        energy_2023 = energy_pollution_with_suburb[energy_pollution_with_suburb['YEAR'] == 2023]
        
        # Energy consumption vs NO2 levels
        st.subheader("Energy Consumption vs NO2 Pollution (2023)")
        
        # Create scatter plot without size parameter
        fig = px.scatter(
            energy_2023,
            x="ENERGY_CONSUMPTION", 
            y="NO2_LEVEL",
            color="SUBURB_NAME",
            hover_name="SUBURB_NAME",
            title="Energy Consumption vs NO2 Levels by Suburb",
            labels={
                "ENERGY_CONSUMPTION": "Energy Consumption (kWh)",
                "NO2_LEVEL": "NO2 Levels (μg/m³)"
            },
            
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Yearly comparison
        st.subheader("Environmental Correlation Across All Suburbs")

        # Make sure data is not empty
        if energy_pollution_with_suburb.empty:
            st.error("No data available.")
        else:
            # Drop rows with missing values to avoid errors
            df = energy_pollution_with_suburb.dropna(subset=["ENERGY_CONSUMPTION", "NO2_LEVEL"])

            # Pearson correlation for all data
            if len(df) >= 2:
                corr = np.corrcoef(df["ENERGY_CONSUMPTION"], df["NO2_LEVEL"])[0, 1]
                st.metric(label="Pearson Correlation (Energy vs NO₂)", value=f"{corr:.2f}")

                # Create scatter plot
                

                fig = px.line(
                df,
                x="YEAR",
                y="NO2_LEVEL",
                color="SUBURB_NAME",
                markers=True,
                title="NO₂ Levels Over Years by Suburb",
                labels={
                    "YEAR": "Year",
                    "NO2_LEVEL": "NO₂ Level (μg/m³)",
                    "SUBURB_NAME": "Suburb"
                }
            )

            fig.update_layout(
                margin=dict(l=40, r=40, t=60, b=40),
                height=600,
                template="plotly_white"
            )

            st.plotly_chart(fig, use_container_width=True)

    
    # TAB 3: Suburb Comparison

    with tab3:
        st.markdown("<p style='text-align: center;padding-bottom:50px;padding-top:50px;'>ADD TEXT HERE.</p>", unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Suburb Comparison</p>', unsafe_allow_html=True)
        
        # Join EV impact and energy pollution for combined analysis
        # First ensure both dataframes have SUBURB_KEY
        if 'SUBURB_KEY' in ev_impact_with_suburb.columns and energy_2023.shape[0] > 0:
            if 'SUBURB_KEY' in energy_2023.columns:
                columns_to_get = ['SUBURB_KEY', 'ENERGY_CONSUMPTION', 'NO2_LEVEL']
                if 'NO2_CHANGE_PCT' in energy_2023.columns:
                    columns_to_get.append('NO2_CHANGE_PCT')
                    
                combined_data = pd.merge(
                    ev_impact_with_suburb,
                    energy_2023[columns_to_get],
                    on="SUBURB_KEY",
                    how="left"
                )
            else:
                # If no SUBURB_KEY in energy_2023, just use the EV data
                combined_data = ev_impact_with_suburb.copy()
                combined_data['ENERGY_CONSUMPTION'] = 0
                combined_data['NO2_LEVEL'] = 0
                combined_data['NO2_CHANGE_PCT'] = 0
        else:
            # Create an empty dataframe with the needed columns
            combined_data = pd.DataFrame(columns=[
                'SUBURB_KEY', 'SUBURB_NAME', 'TOTAL_EVS', 'BEV_COUNT', 'PHEV_COUNT',
                'AVG_RANGE_KM', 'AVG_PRICE', 'EV_ADOPTION_SCORE', 'ENERGY_CONSUMPTION',
                'NO2_LEVEL', 'NO2_CHANGE_PCT'
            ])
        
        # Calculate EV adoption score and normalize it if we have data
        if not combined_data.empty and 'EV_ADOPTION_SCORE' in combined_data.columns:
            # Check if we have more than one value and they're not all the same
            if (combined_data['EV_ADOPTION_SCORE'].nunique() > 1):
                combined_data['EV_ADOPTION_NORMALIZED'] = (combined_data['EV_ADOPTION_SCORE'] - 
                                                      combined_data['EV_ADOPTION_SCORE'].min()) / \
                                                     (combined_data['EV_ADOPTION_SCORE'].max() - 
                                                      combined_data['EV_ADOPTION_SCORE'].min()) * 100
            else:
                # If all values are the same, set to 50
                combined_data['EV_ADOPTION_NORMALIZED'] = 50
        
        # Create radar chart for suburb comparison
        st.subheader("Suburb Comparison - Key Metrics")
        
        # Select suburbs to compare
        selected_suburbs = st.multiselect(
            "Select Suburbs to Compare",
            options=combined_data['SUBURB_NAME'].unique(),
            default=combined_data['SUBURB_NAME'].unique()[:3]  # Default to first 3 suburbs
        )
        
        if selected_suburbs:
            # Filter data for selected suburbs
            radar_data = combined_data[combined_data['SUBURB_NAME'].isin(selected_suburbs)]
            
            # Create radar chart
            fig = go.Figure()
            
            # Metrics to include in radar chart
            metrics = [
                "TOTAL_EVS", 
                "AVG_RANGE_KM", 
                "AVG_PRICE", 
                "ENERGY_CONSUMPTION", 
                "NO2_LEVEL"
            ]
            
            # Normalize metrics for better visualization
            radar_normalized = pd.DataFrame()
            for metric in metrics:
                max_val = radar_data[metric].max()
                min_val = radar_data[metric].min()
                if max_val == min_val:
                    radar_normalized[metric] = 50  # Set to middle value if all are the same
                else:
                    if metric in ["NO2_LEVEL", "AVG_PRICE"]:  # Lower is better
                        radar_normalized[metric] = 100 - ((radar_data[metric] - min_val) / (max_val - min_val) * 100)
                    else:  # Higher is better
                        radar_normalized[metric] = ((radar_data[metric] - min_val) / (max_val - min_val) * 100)
            
            radar_normalized['SUBURB_NAME'] = radar_data['SUBURB_NAME'].values
            
            # Better labels for radar chart
            radar_labels = {
                "TOTAL_EVS": "EV Adoption",
                "AVG_RANGE_KM": "EV Range",
                "AVG_PRICE": "Price Affordability",
                "ENERGY_CONSUMPTION": "Energy Usage",
                "NO2_LEVEL": "Air Quality"
            }
            
            # Add traces for each suburb
            for suburb in selected_suburbs:
                suburb_data = radar_normalized[radar_normalized['SUBURB_NAME'] == suburb]
                
                fig.add_trace(go.Scatterpolar(
                    r=[
                        suburb_data['TOTAL_EVS'].values[0],
                        suburb_data['AVG_RANGE_KM'].values[0],
                        suburb_data['AVG_PRICE'].values[0],
                        suburb_data['ENERGY_CONSUMPTION'].values[0],
                        suburb_data['NO2_LEVEL'].values[0]
                    ],
                    theta=list(radar_labels.values()),
                    fill='toself',
                    name=suburb
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                title="Suburb Comparison (Higher is Better for All Metrics)",
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # EV Adoption vs NO2 Reduction
            st.subheader("EV Adoption vs NO2 Reduction")
            
            fig = px.scatter(
                combined_data,
                x="TOTAL_EVS",
                y="NO2_CHANGE_PCT",
                color="SUBURB_NAME",
                size="ENERGY_CONSUMPTION",
                hover_name="SUBURB_NAME",
                title="Relationship between EV Adoption and NO2 Change",
                labels={
                    "TOTAL_EVS": "Total EVs",
                    "NO2_CHANGE_PCT": "NO2 Change (%)",
                    "ENERGY_CONSUMPTION": "Energy Consumption"
                },
                
            )
            
            # Add a horizontal line at y=0 to show the boundary between increase and decrease
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            # Add explanatory text
            fig.add_annotation(
                x=combined_data['TOTAL_EVS'].max() * 0.8,
                y=5,
                text="NO2 Increase",
                showarrow=False,
                font=dict(color="red")
            )
            
            fig.add_annotation(
                x=combined_data['TOTAL_EVS'].max() * 0.8,
                y=-5,
                text="NO2 Decrease",
                showarrow=False,
                font=dict(color="green")
            )
            
            fig.update_traces(textposition="top center")
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: Data Explorer
    
    with tab4:
        st.markdown("<p style='text-align: center;padding-bottom:50px;padding-top:50px;'>ADD TEXT HERE.</p>", unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Data Explorer</p>', unsafe_allow_html=True)
        
        # Display raw data tables
        st.subheader("Raw Data Tables")
        
        # Select which table to view
        table_option = st.selectbox(
            "Select Table to View",
            options=[
                "EV Impact Fact Table",
                "Energy Pollution Fact Table",
                "Suburb Dimension Table",
                "Vehicle Type Dimension Table",
                "Fuel Type Dimension Table",
                "Time Dimension Table"
            ]
        )
        
        # Display selected table
        if table_option == "EV Impact Fact Table":
            st.dataframe(data["fact_ev_impact"])
        elif table_option == "Energy Pollution Fact Table":
            st.dataframe(data["fact_energy_pollution"])
        elif table_option == "Suburb Dimension Table":
            st.dataframe(data["dim_suburb"])
        elif table_option == "Vehicle Type Dimension Table":
            st.dataframe(data["dim_vehicle_type"])
        elif table_option == "Fuel Type Dimension Table":
            st.dataframe(data["dim_fuel_type"])
        elif table_option == "Time Dimension Table":
            st.dataframe(data["dim_time"])
            
        # Custom query option for more advanced users
        st.subheader("Custom Analysis")
        
        st.write("""
        Select dimensions and metrics to create a custom visualization.
        """)
        
        # Let user select table to analyze
        analysis_table = st.radio(
            "Select primary table for analysis",
            options=["EV Impact", "Energy & Pollution"]
        )
        
        if analysis_table == "EV Impact":
            df_to_analyze = ev_impact_with_suburb
            x_options = ["SUBURB_NAME", "BEV_COUNT", "PHEV_COUNT", "AVG_RANGE_KM", "AVG_PRICE"]
            y_options = ["TOTAL_EVS", "BEV_COUNT", "PHEV_COUNT", "AVG_RANGE_KM", "AVG_PRICE", "EV_ADOPTION_SCORE"]
            color_options = ["SUBURB_NAME", "BEV_COUNT", "PHEV_COUNT", "AVG_RANGE_KM", "AVG_PRICE"]
        else:
            df_to_analyze = energy_pollution_with_suburb
            x_options = ["SUBURB_NAME", "YEAR", "ENERGY_CONSUMPTION", "NO2_LEVEL"]
            y_options = ["ENERGY_CONSUMPTION", "ENERGY_CHANGE_PCT", "NO2_LEVEL", "NO2_CHANGE", "NO2_CHANGE_PCT"]
            color_options = ["SUBURB_NAME", "YEAR", "NO2_CHANGE_PCT", "ENERGY_CHANGE_PCT"]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            x_axis = st.selectbox("X-Axis", options=x_options)
        
        with col2:
            y_axis = st.selectbox("Y-Axis", options=y_options)
        
        with col3:
            color_by = st.selectbox("Color By", options=color_options)
        
        # Chart type selection
        chart_type = st.radio("Chart Type", options=["Bar", "Line", "Scatter"])
        
                    # Create the chart
        if not df_to_analyze.empty:
            # Make sure the columns exist
            if x_axis in df_to_analyze.columns and y_axis in df_to_analyze.columns and color_by in df_to_analyze.columns:
                if chart_type == "Bar":
                    fig = px.bar(
                        df_to_analyze,
                        x=x_axis,
                        y=y_axis,
                        color=color_by,
                        title=f"{y_axis} by {x_axis}",
                        labels={x_axis: x_axis.replace("_", " "), y_axis: y_axis.replace("_", " ")}
                    )
                elif chart_type == "Line":
                    fig = px.line(
                        df_to_analyze,
                        x=x_axis,
                        y=y_axis,
                        color=color_by,
                        title=f"{y_axis} by {x_axis}",
                        labels={x_axis: x_axis.replace("_", " "), y_axis: y_axis.replace("_", " ")}
                    )
                else:  # Scatter
                    fig = px.scatter(
                        df_to_analyze,
                        x=x_axis,
                        y=y_axis,
                        color=color_by,
                        title=f"{y_axis} vs {x_axis}",
                        labels={x_axis: x_axis.replace("_", " "), y_axis: y_axis.replace("_", " ")}
                    )
            else:
                st.error(f"One or more selected columns not found in the data.")
                fig = go.Figure()
        else:
            st.error("No data available for visualization.")
            fig = go.Figure()
        
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()