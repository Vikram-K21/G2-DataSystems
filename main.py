import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from utils.datasetup import AzureDB
import pandas as pd
from sqlalchemy.exc import DatabaseError

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')
load_dotenv(dotenv_path=env_path, override=True)
print(f"Loaded .env from: {env_path}")
print("Environment variables:")
for key in ['ACCOUNT_STORAGE', 'AZURE_STORAGE_CONNECTION_STRING', 'DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD']:
    value = os.environ.get(key)
    if not value:
        print(f"Environment variable {key} is not set")
        raise ValueError(f"Environment variable {key} is not set")
    print(f"{key}: {value}")

# Azure SQL Server database credentials
server = os.environ.get('DB_SERVER', 'etluts04server.database.windows.net')
database = os.environ.get('DB_DATABASE', 'etldb04')
username = os.environ.get('DB_USERNAME', 'vikramdc')
password = os.environ.get('DB_PASSWORD', 'Whyubuggin$19')

# SQL Server connection
driver = "ODBC Driver 18 for SQL Server"
connection_string = (
    f"mssql+pyodbc://{username}:{password}@{server}:1433/{database}"
    f"?driver={driver}&Encrypt=yes&TrustServerCertificate=no&Connection+Timeout=30"
)
engine = create_engine(connection_string)

# Verify Azure Blob Storage credentials
account_storage = os.environ.get('ACCOUNT_STORAGE')
connect_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
if not account_storage:
    raise ValueError("ACCOUNT_STORAGE environment variable not set")
print(f"Loaded ACCOUNT_STORAGE: {account_storage}")
print(f"Loaded AZURE_STORAGE_CONNECTION_STRING: {connect_str}")

azureDB = AzureDB(engine)
try:
    azureDB.access_container("etlblob04")
    blobs = azureDB.list_blobs()
    if blobs is None:
        raise ValueError("Failed to list blobs: blob list is None")
    required_blobs = ['Ev_Population.csv', 'Electricity_Consumption.csv', 'Pollution_Index (4).csv']
    missing_blobs = [blob for blob in required_blobs if blob not in blobs]
    if missing_blobs:
        raise ValueError(f"Missing required blobs: {missing_blobs}")
except Exception as e:
    print(f"Failed to access container or list blobs: {str(e)}")
    raise

def extract_data(azureDB):
    """Extract data from CSV files"""
    print("Starting data extraction...")

    # Extract EV data
    ev_df = azureDB.access_blob_csv('Ev_Population.csv', delimiter=';')
    print(f"Extracted {len(ev_df)} EV records")
    
    # Extract electricity consumption data
    electricity_df = azureDB.access_blob_csv('Electricity_Consumption.csv', delimiter=';')
    print(f"Extracted {len(electricity_df)} electricity consumption records")
    
    # Extract pollution data
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

    # Clean column names
    ev_df.columns = [col.strip().rstrip(';') for col in ev_df.columns]

    # Extract only BEV (Battery Electric Vehicles) and PHEV (Plug-in Hybrid Electric Vehicles)
    ev_df = ev_df[ev_df['FUEL TYPE'].isin(['BEV', 'PHEV'])]

    # Create a vehicle type category
    ev_df['VEHICLE CATEGORY'] = ev_df['VEHICLE TYPE'].str.strip()

    # Extract year from model
    ev_df['MODEL YEAR'] = ev_df['MODEL'].str.extract(r'(\d{4})').astype('float')

    # Clean price data
    ev_df['PRICE'] = ev_df['LISTED PRICE ($AUD)'].str.replace('*', '').str.strip()
    ev_df['PRICE'] = pd.to_numeric(ev_df['PRICE'], errors='coerce')

    # Process range data
    # Some range values may have non-numeric characters, so clean them
    ev_df['RANGE (km)'] = ev_df['RANGE (km)'].astype(str).str.replace('[^0-9.]', '', regex=True)
    ev_df['RANGE (km)'] = pd.to_numeric(ev_df['RANGE (km)'], errors='coerce')

    # Clean suburb data
    ev_df['SUBURB'] = ev_df['SUBURB'].str.strip()

    # Calculate summary metrics
    ev_summary = pd.DataFrame({
        'SUBURB': ev_df.groupby('SUBURB').size().index,
        'TOTAL_EVs': ev_df.groupby('SUBURB').size().values,
        'BEV_COUNT': ev_df[ev_df['FUEL TYPE'] == 'BEV'].groupby('SUBURB').size().reindex(ev_df['SUBURB'].unique(), fill_value=0).values,
        'PHEV_COUNT': ev_df[ev_df['FUEL TYPE'] == 'PHEV'].groupby('SUBURB').size().reindex(ev_df['SUBURB'].unique(), fill_value=0).values,
        'AVG_RANGE_KM': ev_df.groupby('SUBURB')['RANGE (km)'].mean().values,
        'AVG_PRICE': ev_df.groupby('SUBURB')['PRICE'].mean().values
    })

    # Fill NaN values
    ev_summary = ev_summary.fillna(0)

    return ev_summary

def transform_electricity_data(electricity_df):
    """Transform electricity consumption data"""
    print("Transforming electricity consumption data...")
    
    # Clean column names
    electricity_df.columns = [col.strip() for col in electricity_df.columns]
    
    # Extract data for 2022-2023
    electricity_subset = electricity_df[['Name', 'F2021_22', 'F2022_23']]
    
    # Rename columns for clarity
    electricity_subset = electricity_subset.rename(columns={
        'Name': 'SUBURB',
        'F2021_22': 'CONSUMPTION_2022',
        'F2022_23': 'CONSUMPTION_2023'
    })
    
    # Clean suburb names
    electricity_subset['SUBURB'] = electricity_subset['SUBURB'].str.split('+').str[0].str.strip()
    
    # Calculate year-over-year change
    electricity_subset['CONSUMPTION_CHANGE_PCT'] = ((electricity_subset['CONSUMPTION_2023'] - 
                                                    electricity_subset['CONSUMPTION_2022']) / 
                                                   electricity_subset['CONSUMPTION_2022'] * 100)
    
    return electricity_subset

def transform_pollution_data(pollution_df):
    """Transform pollution data"""
    print("Transforming pollution data...")
    
    # Extract relevant columns for NO2 pollution
    pollution_cols = [col for col in pollution_df.columns if 'NO2 annual average' in col]
    pollution_cols.append('Date')
    
    pollution_subset = pollution_df[pollution_cols]
    
    # Reshape data from wide to long format
    pollution_long = pd.melt(
        pollution_subset,
        id_vars=['Date'],
        value_vars=[col for col in pollution_cols if col != 'Date'],
        var_name='LOCATION',
        value_name='NO2_LEVEL'
    )
    
    # Extract suburb name from location
    pollution_long['SUBURB'] = pollution_long['LOCATION'].str.extract(r'(.*) NO2 annual average')
    pollution_long['SUBURB'] = pollution_long['SUBURB'].str.title()
    
    # Map pollution measurement locations to suburbs
    suburb_mapping = {
        'Alexandria': 'Alexandria',
        'Rozelle': 'Rozelle',
        'Earlwood': 'Earlwood',
        'Cook And Phillip': 'Sydney',
        'Randwick': 'Randwick',
        'Macquarie Park': 'Macquarie Park',
        'Parramatta North': 'Parramatta'
    }
    
    # Filter for mapped suburbs only and rename
    pollution_long = pollution_long[pollution_long['SUBURB'].isin(suburb_mapping.keys())]
    pollution_long['SUBURB'] = pollution_long['SUBURB'].map(suburb_mapping)
    
    # Convert date to year
    pollution_long['YEAR'] = pd.to_datetime(pollution_long['Date']).dt.year
    
    # Keep only 2022 and 2023 data
    pollution_long = pollution_long[pollution_long['YEAR'].isin([2022, 2023])]
    
    # Pivot to get pollution by suburb and year
    pollution_pivot = pollution_long.pivot_table(
        index='SUBURB',
        columns='YEAR',
        values='NO2_LEVEL',
        aggfunc='mean'
    ).reset_index()
    
    pollution_pivot.columns = ['SUBURB', 'NO2_2022', 'NO2_2023']
    
    # Calculate year-over-year change
    pollution_pivot['NO2_CHANGE'] = pollution_pivot['NO2_2023'] - pollution_pivot['NO2_2022']
    pollution_pivot['NO2_CHANGE_PCT'] = ((pollution_pivot['NO2_2023'] - pollution_pivot['NO2_2022']) / 
                                        pollution_pivot['NO2_2022'] * 100)
    
    return pollution_pivot

def merge_datasets(ev_summary, electricity_subset, pollution_pivot):
    """Merge all transformed datasets"""
    print("Merging datasets...")
    
    # First merge EV and electricity data
    merged_df = pd.merge(ev_summary, electricity_subset, on='SUBURB', how='outer')
    
    # Then merge with pollution data
    final_df = pd.merge(merged_df, pollution_pivot, on='SUBURB', how='outer')
    
    # Fill NaN values
    final_df = final_df.fillna({
        'TOTAL_EVs': 0,
        'BEV_COUNT': 0,
        'PHEV_COUNT': 0,
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
    
    # Calculate additional metrics
    final_df['EV_PER_ENERGY_UNIT'] = final_df['TOTAL_EVs'] / (final_df['CONSUMPTION_2023'] / 1000000)
    final_df['NO2_PER_EV'] = final_df['NO2_2023'] / final_df['TOTAL_EVs'].replace(0, 1)
    final_df['EV_ADOPTION_SCORE'] = final_df['TOTAL_EVs'] * (1 - final_df['NO2_CHANGE_PCT'] / 100)
    
    return final_df

def create_dimension_tables(final_df, ev_df):
    """Create dimension tables for the star schema"""
    print("Creating dimension tables...")
    
    # Time dimension
    time_dim = pd.DataFrame({
        'TIME_KEY': [2022, 2023],
        'YEAR': [2022, 2023],
        'IS_CURRENT_YEAR': [False, True]
    })
    time_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\time_dim.csv')
    
    # Suburb dimension
    suburb_dim = pd.DataFrame({
        'SUBURB_KEY': range(1, len(final_df) + 1),
        'SUBURB_NAME': final_df['SUBURB'],
    })
    suburb_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\suburb_dim.csv')
    
    # Standardize column names in ev_df to avoid KeyError
    ev_df.columns = [col.strip().upper().replace(" ", "_") for col in ev_df.columns]
    # Vehicle type dimension
    vehicle_dim = pd.DataFrame({
        'VEHICLE_TYPE_KEY': range(1, len(ev_df['VEHICLE_TYPE'].unique()) + 1),
        'VEHICLE_TYPE': sorted(ev_df['VEHICLE_TYPE'].unique())
    })
    vehicle_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\vehicle_dim.csv')
    
    # FUEL TYPE dimension
    fuel_dim = pd.DataFrame({
        'FUEL TYPE_KEY': [1, 2],
        'FUEL TYPE': ['BEV', 'PHEV'],
        'FUEL DESCRIPTION': ['Battery Electric Vehicle', 'Plug-in Hybrid Electric Vehicle']
    })
    fuel_dim.to_csv(r'C:\Users\HP\FinalVS\G2-DataSystems\extracted\fuel_dim.csv')
    
    return time_dim, suburb_dim, vehicle_dim, fuel_dim

def create_fact_tables(final_df, suburb_dim):
    """Create fact tables for the star schema"""
    print("Creating fact tables...")
    
    # Join suburb dimension to get keys
    final_df_with_keys = pd.merge(
        final_df,
        suburb_dim,
        left_on='SUBURB',
        right_on='SUBURB_NAME',
        how='left'
    )
    
    # EV impact fact table
    ev_fact = pd.DataFrame({
        'SUBURB_KEY': final_df_with_keys['SUBURB_KEY'],
        'YEAR': 2023,
        'TOTAL_EVS': final_df_with_keys['TOTAL_EVs'],
        'BEV_COUNT': final_df_with_keys['BEV_COUNT'],
        'PHEV_COUNT': final_df_with_keys['PHEV_COUNT'],
        'AVG_RANGE_KM': final_df_with_keys['AVG_RANGE_KM'],
        'AVG_PRICE': final_df_with_keys['AVG_PRICE'],
        'EV_ADOPTION_SCORE': final_df_with_keys['EV_ADOPTION_SCORE']
    })
    
    # Energy vs Pollution fact table
    energy_fact = pd.DataFrame({
        'SUBURB_KEY': final_df_with_keys['SUBURB_KEY'],
        'YEAR': 2023,
        'ENERGY_CONSUMPTION': final_df_with_keys['CONSUMPTION_2023'],
        'ENERGY_CHANGE_PCT': final_df_with_keys['CONSUMPTION_CHANGE_PCT'],
        'NO2_LEVEL': final_df_with_keys['NO2_2023'],
        'NO2_CHANGE': final_df_with_keys['NO2_CHANGE'],
        'NO2_CHANGE_PCT': final_df_with_keys['NO2_CHANGE_PCT'],
        'EV_PER_ENERGY_UNIT': final_df_with_keys['EV_PER_ENERGY_UNIT'],
        'NO2_PER_EV': final_df_with_keys['NO2_PER_EV']
        
    })
    energy_fact = energy_fact.fillna(0.0)
    # Create historical rows for 2022
    energy_fact_2022 = pd.DataFrame({
        'SUBURB_KEY': final_df_with_keys['SUBURB_KEY'],
        'YEAR': 2022,
        'ENERGY_CONSUMPTION': final_df_with_keys['CONSUMPTION_2022'],
        'ENERGY_CHANGE_PCT': 0,  # No previous year for comparison
        'NO2_LEVEL': final_df_with_keys['NO2_2022'],
        'NO2_CHANGE': 0,  # No previous year for comparison
        'NO2_CHANGE_PCT': 0,  # No previous year for comparison
        'EV_PER_ENERGY_UNIT': final_df_with_keys['TOTAL_EVs'] / (final_df_with_keys['CONSUMPTION_2022'] / 1000000),
        'NO2_PER_EV': final_df_with_keys['NO2_2022'] / final_df_with_keys['TOTAL_EVs'].replace(0, 1)
    })
    
    # Combine 2022 and 2023 data
    energy_fact = pd.concat([energy_fact, energy_fact_2022])
    energy_fact = pd.concat([energy_fact, energy_fact_2022])

    # Clean up float columns for SQL Server compatibility
    float_cols = energy_fact.select_dtypes(include=['float', 'float64']).columns
    energy_fact[float_cols] = energy_fact[float_cols].replace([float('inf'), float('-inf')], 0.0)
    energy_fact[float_cols] = energy_fact[float_cols].fillna(0.0)
    energy_fact[float_cols] = energy_fact[float_cols].round(6)
    ev_fact.to_csv('ev_fact.csv')
    energy_fact.to_csv('energy_fact.csv')

    
    return ev_fact, energy_fact

def load_to_azure(azureDB, time_dim, suburb_dim, vehicle_dim, fuel_dim, ev_fact, energy_fact):
    """Load dimension and fact tables to Azure"""
    print("\n=== LOADING DATA TO AZURE ===")
    
    # Load dimension tables
    print("\nLoading dimension tables to Azure SQL database...")
    azureDB.upload_dataframe_sqldatabase("time_dim", time_dim)
    azureDB.upload_dataframe_sqldatabase("suburb_dim", suburb_dim)
    azureDB.upload_dataframe_sqldatabase("vehicle_dim", vehicle_dim)
    azureDB.upload_dataframe_sqldatabase("fuel_dim", fuel_dim)
    
    # Load fact tables
    print("\nLoading fact tables to Azure SQL database...")
    azureDB.upload_dataframe_sqldatabase("ev_fact", ev_fact)
    azureDB.upload_dataframe_sqldatabase("energy_fact", energy_fact)



def main():
    print("Extracting Data")
    ev_df, electricity_df, pollution_df = extract_data(azureDB)
    
    print("Transforming EV Data")
    ev_summary = transform_ev_data(ev_df)
    print("\nSample of transformed EV data:")
    print(ev_summary.head())

    print("Transforming Electricty Data")
    electricity_subset = transform_electricity_data(electricity_df)
    print("\nSample of transformed Electricity data:")
    print(electricity_subset.head())

    print("Transforming Pollution Data")
    pollution_pivot= transform_pollution_data(pollution_df)
    print("\nSample of transformed Pollution data:")
    print(pollution_pivot.head())
    
    # Merge datasets
    final_df = merge_datasets(ev_summary, electricity_subset, pollution_pivot)
    # Quick shape & head
    print("Final merged shape:", final_df.shape)
    print(final_df.head(), "\n")

    # Unique-SUBURB counts
    print("Unique suburbs:",
          "EV:", ev_summary['SUBURB'].nunique(),
          "Elec:", electricity_subset['SUBURB'].nunique(),
          "Poll:", pollution_pivot['SUBURB'].nunique(),
          "Final:", final_df['SUBURB'].nunique()
    )

    # Dimension Tables
    time_dim, suburb_dim, vehicle_dim, fuel_dim = \
        create_dimension_tables(final_df, ev_df)

    print("Time DT")
    print("Shape:", time_dim.shape)
    print(time_dim, "\n")

    print("Suburb DT")
    print("Shape:", suburb_dim.shape)
    print(suburb_dim.head(), "\n")

    print("Vehicle-Type DT")
    print("Shape:", vehicle_dim.shape)
    print(vehicle_dim, "\n")

    print("Fuel-Type DT")
    print("Shape:", fuel_dim.shape)
    print(fuel_dim, "\n")

    # Fact tables
    ev_fact, energy_fact = create_fact_tables(final_df, suburb_dim)

    print("EV Impact Fact")
    print("Shape:", ev_fact.shape)
    print(ev_fact.head(), "\n")

    print("Energy vs Pollution Fact")
    print("Shape:", energy_fact.shape)
    print(energy_fact.head(), "\n")

    # … after create_dimension_tables and create_fact_tables …
    load_to_azure(azureDB, time_dim, suburb_dim, vehicle_dim, fuel_dim, 
                 ev_fact, energy_fact)

if __name__ == "__main__":
    main()
