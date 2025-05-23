import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from utils.datasetup import AzureDB
import pandas as pd

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path=env_path, override=True)
print(f"Loaded .env from: {env_path}")

# Azure SQL Server database credentials
server = os.environ.get('DB_SERVER', 'etluts04server.database.windows.net')
database = os.environ.get('DB_DATABASE', 'etldb04')
username = os.environ.get('DB_USERNAME', 'vikramdc')
password = os.environ.get('DB_PASSWORD', 'Whyubuggin$19')
driver = "ODBC Driver 18 for SQL Server"
connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
    f"?driver={driver}&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
)
engine = create_engine(connection_string)
azureDB = AzureDB(engine)

def extract_data(azureDB):
    """Extract data from CSV files"""
    print("Starting data extraction...")

    ev_df = azureDB.access_blob_csv('Ev_Population.csv', delimiter=';')
    ev_df.columns = [col.strip().upper().replace(" ", "_") for col in ev_df.columns]
    print(f"Extracted {len(ev_df)} EV records")
    
    electricity_df = azureDB.access_blob_csv('Electricity_Consumption.csv', delimiter=';')
    print(f"Extracted {len(electricity_df)} electricity consumption records")
    
    pollution_df = azureDB.access_blob_csv(
        'Pollution_Index (4).csv',
        delimiter=',',        
        header=2,             
        parse_dates=['Date'],
        dayfirst=True
    )
    pollution_df.columns = pollution_df.columns.str.strip()
    print(f"Extracted {len(pollution_df)} pollution records")
    
    return ev_df, electricity_df, pollution_df

def transform_ev_data(ev_df):
    """Transform EV data"""
    print("Transforming EV data...")
    ev_df.columns = [col.strip().rstrip(';') for col in ev_df.columns]
    ev_df['VEHICLE CATEGORY'] = ev_df['VEHICLE_TYPE'].str.strip()
    ev_df['MODEL YEAR'] = ev_df['MODEL'].str.extract(r'(\d{4})').astype('float')
    ev_df['PRICE'] = ev_df['LISTED_PRICE_($AUD)'].str.replace('*', '').str.strip()
    ev_df['PRICE'] = pd.to_numeric(ev_df['PRICE'], errors='coerce')
    ev_df['RANGE_(KM)'] = ev_df['RANGE_(KM)'].astype(str).str.replace('[^0-9.]', '', regex=True)
    ev_df['RANGE_(KM)'] = pd.to_numeric(ev_df['RANGE_(KM)'], errors='coerce')
    ev_df['SUBURB'] = ev_df['SUBURB'].str.strip()
    
    ev_summary = ev_df.groupby(['SUBURB', 'VEHICLE_TYPE', 'FUEL_TYPE']).agg(
        TOTAL_EVs=('FUEL_TYPE', 'count'),
        AVG_RANGE_KM=('RANGE_(KM)', 'mean'),
        AVG_PRICE=('PRICE', 'mean')
    ).reset_index()
    
    ev_summary = ev_summary.fillna(0)
    return ev_summary

def transform_electricity_data(electricity_df):
    """Transform electricity consumption data"""
    print("Transforming electricity consumption data...")
    electricity_df.columns = [col.strip() for col in electricity_df.columns]
    electricity_subset = electricity_df[['Name', 'F2021_22', 'F2022_23']]
    electricity_subset = electricity_subset.rename(columns={
        'Name': 'SUBURB',
        'F2021_22': 'CONSUMPTION_2022',
        'F2022_23': 'CONSUMPTION_2023'
    })
    electricity_subset['SUBURB'] = electricity_subset['SUBURB'].str.split('+').str[0].str.strip()
    electricity_subset['CONSUMPTION_CHANGE_PCT'] = ((electricity_subset['CONSUMPTION_2023'] - 
                                                     electricity_subset['CONSUMPTION_2022']) / 
                                                    electricity_subset['CONSUMPTION_2022'] * 100)
    return electricity_subset

def transform_pollution_data(pollution_df):
    """Transform pollution data"""
    print("Transforming pollution data...")
    pollution_cols = [col for col in pollution_df.columns if 'NO2 annual average' in col]
    pollution_cols.append('Date')
    pollution_subset = pollution_df[pollution_cols]
    pollution_long = pd.melt(
        pollution_subset,
        id_vars=['Date'],
        value_vars=[col for col in pollution_cols if col != 'Date'],
        var_name='LOCATION',
        value_name='NO2_LEVEL'
    )
    pollution_long['SUBURB'] = pollution_long['LOCATION'].str.extract(r'(.*) NO2 annual average')
    pollution_long['SUBURB'] = pollution_long['SUBURB'].str.title()
    suburb_mapping = {
        'Alexandria': 'Alexandria',
        'Rozelle': 'Rozelle',
        'Earlwood': 'Earlwood',
        'Cook And Phillip': 'Sydney',
        'Randwick': 'Randwick',
        'Macquarie Park': 'Macquarie Park',
        'Parramatta North': 'Parramatta'
    }
    pollution_long = pollution_long[pollution_long['SUBURB'].isin(suburb_mapping.keys())]
    pollution_long['SUBURB'] = pollution_long['SUBURB'].map(suburb_mapping)
    pollution_long['YEAR'] = pd.to_datetime(pollution_long['Date']).dt.year
    pollution_long = pollution_long[pollution_long['YEAR'].isin([2022, 2023])]
    pollution_pivot = pollution_long.pivot_table(
        index='SUBURB',
        columns='YEAR',
        values='NO2_LEVEL',
        aggfunc='mean'
    ).reset_index()
    pollution_pivot.columns = ['SUBURB', 'NO2_2022', 'NO2_2023']
    pollution_pivot['NO2_CHANGE'] = pollution_pivot['NO2_2023'] - pollution_pivot['NO2_2022']
    pollution_pivot['NO2_CHANGE_PCT'] = ((pollution_pivot['NO2_2023'] - pollution_pivot['NO2_2022']) / 
                                         pollution_pivot['NO2_2022'] * 100)
    return pollution_pivot

def merge_datasets(ev_summary, electricity_subset, pollution_pivot):
    """Merge all transformed datasets"""
    print("Merging datasets...")
    merged_df = pd.merge(ev_summary, electricity_subset, on='SUBURB', how='outer')
    final_df = pd.merge(merged_df, pollution_pivot, on='SUBURB', how='outer')
    final_df = final_df.fillna({
        'TOTAL_EVs': 0,
        'AVG_RANGE_KM': 0,
        'AVG_PRICE': 0,
        'CONSUMPTION_2022': 0,
        'CONSUMPTION_2023': 0,
        'CONSUMPTION_CHANGE_PCT': 0,
        'NO2_2022': 0,
        'NO2_2023': 0,
        'NO2_CHANGE': 0,
        'NO2_CHANGE_PCT': 0
    })
    final_df['EV_PER_ENERGY_UNIT'] = final_df['TOTAL_EVs'] / (final_df['CONSUMPTION_2023'] / 1000000)
    final_df['NO2_PER_EV'] = final_df['NO2_2023'] / final_df['TOTAL_EVs'].replace(0, 1)
    final_df['EV_ADOPTION_SCORE'] = final_df['TOTAL_EVs'] * (1 - final_df['NO2_CHANGE_PCT'] / 100)
    # Add YEAR column for merging with time_dim (set to 2023 for this dataset)
    final_df['YEAR'] = 2023
    return final_df

def create_dimension_tables(final_df, ev_df):
    """Create dimension tables for the star schema"""
    print("Creating dimension tables...")
    time_dim = pd.DataFrame({
        'time_id': [1, 2],
        'YEAR': [2022, 2023],
        'IS_CURRENT_YEAR': [False, True]
    })
    time_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\time_dim.csv', index=False)
    
    suburb_names = sorted(final_df['SUBURB'].dropna().unique())
    suburb_dim = pd.DataFrame({
        'suburb_id': range(1, len(suburb_names) + 1),
        'SUBURB_NAME': suburb_names,
    })
    suburb_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\suburb_dim.csv', index=False)
    
    ev_df.columns = [col.strip().upper().replace(" ", "_") for col in ev_df.columns]
    vehicle_types = sorted(ev_df['VEHICLE_TYPE'].dropna().unique())
    vehicle_dim = pd.DataFrame({
        'vehicle_id': range(1, len(vehicle_types) + 1),
        'VEHICLE_TYPE': vehicle_types
    })
    vehicle_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\vehicle_dim.csv', index=False)
    
    fuel_types = sorted(ev_df['FUEL_TYPE'].dropna().unique())
    fuel_dim = pd.DataFrame({
        'fuel_id': range(1, len(fuel_types) + 1),
        'FUEL_TYPE': fuel_types
    })
    fuel_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\fuel_dim.csv', index=False)
    
    return time_dim, suburb_dim, vehicle_dim, fuel_dim

def create_fact_tables(final_df, suburb_dim, vehicle_dim, fuel_dim, time_dim):
    """Create fact tables for the star schema"""
    print("Creating fact tables...")
    final_df_with_keys = pd.merge(
        final_df,
        suburb_dim,
        left_on='SUBURB',
        right_on='SUBURB_NAME',
        how='left'
    )
    final_df_with_keys = pd.merge(
        final_df_with_keys,
        vehicle_dim,
        left_on='VEHICLE_TYPE',
        right_on='VEHICLE_TYPE',
        how='left'
    )
    final_df_with_keys = pd.merge(
        final_df_with_keys,
        fuel_dim,
        left_on='FUEL_TYPE',
        right_on='FUEL_TYPE',
        how='left'
    )
    # Merge with time_dim to get time_id
    final_df_with_keys = pd.merge(
        final_df_with_keys,
        time_dim,
        on='YEAR',
        how='left'
    )
    ev_fact = pd.DataFrame({
        'ev_fact_id': range(1, len(final_df_with_keys) + 1),
        'suburb_id': final_df_with_keys['suburb_id'].fillna(0).astype(int),
        'vehicle_id': final_df_with_keys['vehicle_id'].fillna(0).astype(int),
        'fuel_id': final_df_with_keys['fuel_id'].fillna(0).astype(int),
        'time_id': final_df_with_keys['time_id'].fillna(0).astype(int),
        'TOTAL_EVs': final_df_with_keys['TOTAL_EVs'],
        'FUEL_TYPE': final_df_with_keys['FUEL_TYPE'],
        'AVG_RANGE_KM': final_df_with_keys['AVG_RANGE_KM'],
        'AVG_PRICE': final_df_with_keys['AVG_PRICE'],
        'EV_ADOPTION_SCORE': final_df_with_keys['EV_ADOPTION_SCORE']
    })
    energy_fact = pd.DataFrame({
        'energy_fact_id': range(1, len(final_df_with_keys) + 1),
        'suburb_id': final_df_with_keys['suburb_id'].fillna(0).astype(int),
        'vehicle_id': final_df_with_keys['vehicle_id'].fillna(0).astype(int),
        'fuel_id': final_df_with_keys['fuel_id'].fillna(0).astype(int),
        'time_id': final_df_with_keys['time_id'].fillna(0).astype(int),
        'ENERGY_CONSUMPTION': final_df_with_keys['CONSUMPTION_2023'],
        'ENERGY_CHANGE_PCT': final_df_with_keys['CONSUMPTION_CHANGE_PCT'],
        'NO2_LEVEL': final_df_with_keys['NO2_2023'],
        'NO2_CHANGE': final_df_with_keys['NO2_CHANGE'],
        'NO2_CHANGE_PCT': final_df_with_keys['NO2_CHANGE_PCT'],
        'EV_PER_ENERGY_UNIT': final_df_with_keys['EV_PER_ENERGY_UNIT'],
        'NO2_PER_EV': final_df_with_keys['NO2_PER_EV']
    })
    # Clean float columns for SQL Server compatibility.
    float_cols = energy_fact.select_dtypes(include=['float', 'float64']).columns
    energy_fact[float_cols] = energy_fact[float_cols].replace([float('inf'), float('-inf')], 0.0)
    energy_fact[float_cols] = energy_fact[float_cols].fillna(0.0)
    energy_fact[float_cols] = energy_fact[float_cols].round(6)
    ev_fact.to_csv('ev_fact.csv', index=False)
    energy_fact.to_csv('energy_fact.csv', index=False)
    return ev_fact, energy_fact


def load_to_azure(azureDB, ev_fact, energy_fact, suburb_dim, vehicle_dim, fuel_dim, time_dim):
    print("\n=== LOADING DATA TO AZURE ===")
    with engine.connect() as con:
        for fact_table in ['ev_fact', 'energy_fact']:
                con.execute(text(f"DROP TABLE IF EXISTS [dbo].[{fact_table}]"))
                print(f"Dropped {fact_table} if it existed.")
        for dim_table in ['suburb_dim', 'vehicle_dim', 'fuel_dim', 'time_dim']:
                con.execute(text(f"DROP TABLE IF EXISTS [dbo].[{dim_table}]"))
                print(f"Dropped {dim_table} if it existed.")
    #remove duplicates from dimension tables
    suburb_dim = suburb_dim.drop_duplicates(subset=['suburb_id'])
    vehicle_dim = vehicle_dim.drop_duplicates(subset=['vehicle_id'])
    fuel_dim = fuel_dim.drop_duplicates(subset=['fuel_id'])
    time_dim = time_dim.drop_duplicates(subset=['time_id'])

   #upload dimension tables
    azureDB.upload_dataframe_sqldatabase("suburb_dim", suburb_dim)
    azureDB.upload_dataframe_sqldatabase("vehicle_dim", vehicle_dim)
    azureDB.upload_dataframe_sqldatabase("fuel_dim", fuel_dim)
    azureDB.upload_dataframe_sqldatabase("time_dim", time_dim)

    # Reload fact tables
    azureDB.upload_dataframe_sqldatabase("ev_fact", ev_fact)
    azureDB.upload_dataframe_sqldatabase("energy_fact", energy_fact)

    # 4. Re-add foreign key constraints
    with engine.connect() as con:
        fact_tables = ['ev_fact', 'energy_fact']
        dimension_tables = [
            ('suburb_id', 'suburb_dim'),
            ('vehicle_id', 'vehicle_dim'),
            ('fuel_id', 'fuel_dim'),
            ('time_id', 'time_dim')
        ]

        for fact_table in fact_tables:
            for id_column, dim_table in dimension_tables:
                try:
                    con.execute(
                        text(
                            f'ALTER TABLE [dbo].[{fact_table}] WITH NOCHECK ADD CONSTRAINT [FK_{fact_table}_{id_column}_dim] '
                            f'FOREIGN KEY ([{id_column}]) REFERENCES [dbo].[{dim_table}] ([{id_column}]) '
                            'ON UPDATE CASCADE ON DELETE CASCADE;'
                        )
                    )
                    print(f"Added FK constraint FK_{fact_table}_{id_column}_dim")
                except Exception as e:
                    print(f"Could not add FK constraint FK_{fact_table}_{id_column}_dim: {e}")
    print("All tables loaded to Azure SQL Database ")
def main():
    # Initialize the blob container client before extracting data
    azureDB.access_container(os.environ.get('CONTAINER_NAME', 'etlblob04'))

    print("Extracting Data")
    ev_df, electricity_df, pollution_df = extract_data(azureDB)
    
    print("Transforming EV Data")
    ev_summary = transform_ev_data(ev_df)
    print("\nSample of transformed EV data:")
    print(ev_summary)
    
    print("Transforming Electricity Data")
    electricity_subset = transform_electricity_data(electricity_df)
    print("\nSample of transformed Electricity data:")
    print(electricity_subset.head())
    
    print("Transforming Pollution Data")
    pollution_pivot = transform_pollution_data(pollution_df)
    print("\nSample of transformed Pollution data:")
    print(pollution_pivot.head())
    
    final_df = merge_datasets(ev_summary, electricity_subset, pollution_pivot)
    print("Final merged shape:", final_df.shape)
    print(final_df.head(), "\n")
    
    print("Unique suburbs:",
          "EV:", ev_summary['SUBURB'].nunique(),
          "Elec:", electricity_subset['SUBURB'].nunique(),
          "Poll:", pollution_pivot['SUBURB'].nunique(),
          "Final:", final_df['SUBURB'].nunique()
    )
    
    time_dim, suburb_dim, vehicle_dim, fuel_dim = create_dimension_tables(final_df, ev_df)
    print("Time Dimension Table:")
    print(time_dim, "\n")
    print("Suburb Dimension Table:")
    print(suburb_dim.head(), "\n")
    print("Vehicle Dimension Table:")
    print(vehicle_dim, "\n")
    print("Fuel Dimension Table:")
    print(fuel_dim, "\n")
    
    ev_fact, energy_fact = create_fact_tables(final_df, suburb_dim, vehicle_dim, fuel_dim, time_dim)
    print("EV Impact Fact Table:")
    print(ev_fact.head(), "\n")
    print("Energy vs Pollution Fact Table:")
    print(energy_fact.head(), "\n")
    
    load_to_azure(azureDB,ev_fact, energy_fact,suburb_dim, vehicle_dim, fuel_dim,time_dim)

if __name__ == "__main__":
    main()
