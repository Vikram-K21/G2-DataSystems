import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datsetup import AzureDB
import pandas as pd

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), '..', 'src', '.env')  # Adjusted to src
load_dotenv(dotenv_path=env_path, override=True)
print(f"Loaded .env from: {env_path}")
print("Environment variables:")
for key in ['ACCOUNT_STORAGE', 'AZURE_STORAGE_CONNECTION_STRING', 'DB_SERVER', 'DB_DATABASE', 'DB_USERNAME', 'DB_PASSWORD']:
    print(f"{key}: {os.environ.get(key)}")

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

# Verify that the ACCOUNT_STORAGE is loaded correctly
account_storage = os.environ.get('ACCOUNT_STORAGE')
connect_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
if not account_storage:
    raise ValueError("ACCOUNT_STORAGE environment variable not set")
print(f"Loaded ACCOUNT_STORAGE: {account_storage}")
print(f"Loaded AZURE_STORAGE_CONNECTION_STRING: {connect_str}")

azureDB = AzureDB()
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
    print("Starting data extraction...")
    try:
        ev_df = azureDB.access_blob_csv('Ev_Population.csv', delimiter=';')
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
    except Exception as e:
        raise Exception(f"Data extraction failed: {str(e)}")

def transform_ev_data(ev_df):
    print("Transforming EV data...")
    try:
        ev_df.columns = ev_df.columns.str.strip().str.upper()
        required_columns = ['FUEL TYPE', 'VEHICLE TYPE', 'MODEL', 'LISTED PRICE ($AUD)', 'RANGE (KM)', 'SUBURB']
        for col in required_columns:
            if col not in ev_df.columns:
                raise KeyError(f"Missing required column: {col}")
        ev_df = ev_df[ev_df['FUEL TYPE'].isin(['BEV', 'PHEV'])].copy()  # Create explicit copy
        ev_df.loc[:, 'VEHICLE CATEGORY'] = ev_df['VEHICLE TYPE'].str.strip()
        ev_df.loc[:, 'MODEL YEAR'] = ev_df['MODEL'].str.extract(r'(\d{4})').astype(float, errors='ignore')
        ev_df.loc[:, 'PRICE'] = pd.to_numeric(
            ev_df['LISTED PRICE ($AUD)'].str.replace(r'[\*\s]', '', regex=True),
            errors='coerce'
        )
        ev_df.loc[:, 'RANGE (KM)'] = pd.to_numeric(ev_df['RANGE (KM)'], errors='coerce')
        ev_df.loc[:, 'SUBURB'] = ev_df['SUBURB'].str.strip()
        suburb_ev_counts = ev_df.groupby(['SUBURB', 'FUEL TYPE']).size().reset_index(name='COUNT')
        ev_summary = pd.DataFrame({
            'TOTAL_EVs': ev_df.groupby('SUBURB').size(),
            'BEV_COUNT': ev_df[ev_df['FUEL TYPE'] == 'BEV'].groupby('SUBURB').size(),
            'PHEV_COUNT': ev_df[ev_df['FUEL TYPE'] == 'PHEV'].groupby('SUBURB').size(),
            'AVG_RANGE_KM': ev_df.groupby('SUBURB')['RANGE (KM)'].mean(),
            'AVG_PRICE': ev_df.groupby('SUBURB')['PRICE'].mean()
        }).reset_index()
        ev_summary = ev_summary.fillna(0)
        return ev_summary
    except Exception as e:
        raise Exception(f"EV data transformation failed: {str(e)}")

def transform_electricity_data(electricity_df):
    print("Transforming electricity consumption data...")
    try:
        electricity_df.columns = [col.strip() for col in electricity_df.columns]
        electricity_subset = electricity_df[['Name', 'F2021_22', 'F2022_23']]
        electricity_subset = electricity_subset.rename(columns={
            'Name': 'SUBURB',
            'F2021_22': 'CONSUMPTION_2022',
            'F2022_23': 'CONSUMPTION_2023'
        })
        electricity_subset['SUBURB'] = electricity_subset['SUBURB'].str.split('+').str[0].str.strip()
        electricity_subset['CONSUMPTION_CHANGE_PCT'] = (
            (electricity_subset['CONSUMPTION_2023'] - electricity_subset['CONSUMPTION_2022']) /
            electricity_subset['CONSUMPTION_2022'].replace(0, 1) * 100
        )
        return electricity_subset
    except Exception as e:
        raise Exception(f"Electricity data transformation failed: {str(e)}")

def transform_pollution_data(pollution_df):
    print("Transforming pollution data...")
    try:
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
        pollution_pivot['NO2_CHANGE_PCT'] = (
            (pollution_pivot['NO2_2023'] - pollution_pivot['NO2_2022']) / pollution_pivot['NO2_2022'].replace(0, 1) * 100
        )
        return pollution_pivot
    except Exception as e:
        raise Exception(f"Pollution data transformation failed: {str(e)}")

def merge_datasets(ev_summary, electricity_subset, pollution_pivot):
    print("Merging datasets...")
    try:
        merged_df = pd.merge(ev_summary, electricity_subset, on='SUBURB', how='outer')
        final_df = pd.merge(merged_df, pollution_pivot, on='SUBURB', how='outer')
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
        final_df['EV_PER_ENERGY_UNIT'] = final_df['TOTAL_EVs'] / (final_df['CONSUMPTION_2023'].replace(0, 1) / 1_000_000)
        final_df['NO2_PER_EV'] = final_df['NO2_2023'] / final_df['TOTAL_EVs'].replace(0, 1)
        final_df['EV_ADOPTION_SCORE'] = final_df['TOTAL_EVs'] * (1 - final_df['NO2_CHANGE_PCT'] / 100)
        scale_cols = [
            'TOTAL_EVs', 'AVG_RANGE_KM', 'AVG_PRICE', 'CONSUMPTION_2023',
            'NO2_2023', 'EV_PER_ENERGY_UNIT', 'NO2_PER_EV', 'EV_ADOPTION_SCORE'
        ]
        for col in scale_cols:
            min_val = final_df[col].min()
            max_val = final_df[col].max()
            if max_val - min_val != 0:
                final_df[f'{col}_SCALED'] = (final_df[col] - min_val) / (max_val - min_val)
            else:
                final_df[f'{col}_SCALED'] = 0
        return final_df
    except Exception as e:
        raise Exception(f"Dataset merging failed: {str(e)}")

def create_dimension_tables(final_df, ev_df):
    print("Creating dimension tables...")
    try:
        time_dim = pd.DataFrame({
            'TIME_KEY': [2022, 2023],
            'YEAR': [2022, 2023],
            'IS_CURRENT_YEAR': [False, True]
        })
        unique_suburbs = final_df['SUBURB'].dropna().unique()
        suburb_dim = pd.DataFrame({
            'SUBURB_KEY': range(1, len(unique_suburbs) + 1),
            'SUBURB_NAME': sorted(unique_suburbs)
        })
        vehicle_type_dim = pd.DataFrame({
            'VEHICLE_TYPE_KEY': range(1, len(ev_df['VEHICLE TYPE'].unique()) + 1),
            'VEHICLE_TYPE': sorted(ev_df['VEHICLE TYPE'].unique())
        })
        vehicle_type_dim['VEHICLE_TYPE'] = vehicle_type_dim['VEHICLE_TYPE'].astype(str) # Ensure no nulls
        fuel_type_dim = pd.DataFrame({
            'FUEL_TYPE_KEY': [1, 2],
            'FUEL_TYPE': ['BEV', 'PHEV'],
            'FUEL_DESCRIPTION': ['Battery Electric Vehicle', 'Plug-in Hybrid Electric Vehicle']
        })
        final_df = final_df.merge(suburb_dim, how='left', left_on='SUBURB', right_on='SUBURB_NAME')
        final_df['YEAR'] = 2023
        final_df = final_df.merge(time_dim[['TIME_KEY', 'YEAR']], how='left', on='YEAR')
        if 'SUBURB_KEY' not in final_df.columns:
            raise KeyError("SUBURB_KEY column missing in final_df after merge with suburb_dim")
        final_df = final_df.drop(columns=['SUBURB_NAME'], errors='ignore')
        return time_dim, suburb_dim, vehicle_type_dim, fuel_type_dim, final_df
    except Exception as e:
        raise Exception(f"Dimension table creation failed: {str(e)}")

def create_fact_tables(final_df, suburb_dim):
    print("Creating fact tables...")
    try:
        final_df_with_keys = final_df
        ev_impact_fact = pd.DataFrame({
            'SUBURB_KEY': final_df_with_keys['SUBURB_KEY'],
            'TIME_KEY': final_df_with_keys['TIME_KEY'],
            'TOTAL_EVS': final_df_with_keys['TOTAL_EVs'],
            'BEV_COUNT': final_df_with_keys['BEV_COUNT'],
            'PHEV_COUNT': final_df_with_keys['PHEV_COUNT'],
            'AVG_RANGE_KM': final_df_with_keys['AVG_RANGE_KM'],
            'AVG_PRICE': final_df_with_keys['AVG_PRICE'],
            'EV_ADOPTION_SCORE': final_df_with_keys['EV_ADOPTION_SCORE']
        })
        energy_pollution_fact = pd.DataFrame({
            'SUBURB_KEY': final_df_with_keys['SUBURB_KEY'],
            'TIME_KEY': final_df_with_keys['TIME_KEY'],
            'ENERGY_CONSUMPTION': final_df_with_keys['CONSUMPTION_2023'],
            'ENERGY_CHANGE_PCT': final_df_with_keys['CONSUMPTION_CHANGE_PCT'],
            'NO2_LEVEL': final_df_with_keys['NO2_2023'],
            'NO2_CHANGE': final_df_with_keys['NO2_CHANGE'],
            'NO2_CHANGE_PCT': final_df_with_keys['NO2_CHANGE_PCT'],
            'EV_PER_ENERGY_UNIT': final_df_with_keys['EV_PER_ENERGY_UNIT'],
            'NO2_PER_EV': final_df_with_keys['NO2_PER_EV']
        })
        energy_pollution_fact_2022 = pd.DataFrame({
            'SUBURB_KEY': final_df_with_keys['SUBURB_KEY'],
            'TIME_KEY': 2022,
            'ENERGY_CONSUMPTION': final_df_with_keys['CONSUMPTION_2022'],
            'ENERGY_CHANGE_PCT': 0,
            'NO2_LEVEL': final_df_with_keys['NO2_2022'],
            'NO2_CHANGE': 0,
            'NO2_CHANGE_PCT': 0,
            'EV_PER_ENERGY_UNIT': final_df_with_keys['TOTAL_EVs'] / (final_df_with_keys['CONSUMPTION_2022'].replace(0, 1e-6) / 1_000_000),
            'NO2_PER_EV': final_df_with_keys['NO2_2022'] / final_df_with_keys['TOTAL_EVs'].replace(0, 1)
        })
        energy_pollution_fact = pd.concat([energy_pollution_fact, energy_pollution_fact_2022], ignore_index=True)
        return ev_impact_fact, energy_pollution_fact
    except Exception as e:
        raise Exception(f"Fact table creation failed: {str(e)}")

def load_to_azure(azureDB, time_dim, suburb_dim, vehicle_type_dim, fuel_type_dim, ev_impact_fact, energy_pollution_fact):
    print("Starting Step 3: Loading data to Azure SQL database...")
    try:
        print("Uploading dimension tables...")
        azureDB.upload_dataframe_sqldatabase('time_dim', blob_data=time_dim)
        azureDB.upload_dataframe_sqldatabase('suburb_dim', blob_data=suburb_dim)
        azureDB.upload_dataframe_sqldatabase('vehicle_type_dim', blob_data=vehicle_type_dim)
        azureDB.upload_dataframe_sqldatabase('fuel_type_dim', blob_data=fuel_type_dim)
        print("Dimension tables uploaded.")
        print("Uploading fact tables...")
        azureDB.upload_dataframe_sqldatabase('ev_impact_fact', blob_data=ev_impact_fact)
        azureDB.upload_dataframe_sqldatabase('energy_pollution_fact', blob_data=energy_pollution_fact)
        print("Fact tables uploaded.")
        print("Adding primary and foreign key constraints...")
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE time_dim ADD CONSTRAINT PK_time_dim PRIMARY KEY (TIME_KEY);"))
            conn.execute(text("ALTER TABLE suburb_dim ADD CONSTRAINT PK_suburb_dim PRIMARY KEY (SUBURB_KEY);"))
            conn.execute(text("ALTER TABLE vehicle_type_dim ADD CONSTRAINT PK_vehicle_type_dim PRIMARY KEY (VEHICLE_TYPE_KEY);"))
            conn.execute(text("ALTER TABLE fuel_type_dim ADD CONSTRAINT PK_fuel_type_dim PRIMARY KEY (FUEL_TYPE_KEY);"))
            conn.execute(text("""
                ALTER TABLE ev_impact_fact
                ADD CONSTRAINT FK_ev_impact_fact_suburb FOREIGN KEY (SUBURB_KEY) REFERENCES suburb_dim(SUBURB_KEY),
                    CONSTRAINT FK_ev_impact_fact_time FOREIGN KEY (TIME_KEY) REFERENCES time_dim(TIME_KEY);
            """))
            conn.execute(text("""
                ALTER TABLE energy_pollution_fact
                ADD CONSTRAINT FK_energy_pollution_fact_suburb FOREIGN KEY (SUBURB_KEY) REFERENCES suburb_dim(SUBURB_KEY),
                    CONSTRAINT FK_energy_pollution_fact_time FOREIGN KEY (TIME_KEY) REFERENCES time_dim(TIME_KEY);
            """))
        print("Constraints added.")
    except Exception as e:
        raise Exception(f"Failed to load data to Azure: {str(e)}")

def main():
    print("Starting ETL process...")
    try:
        # Extract data
        ev_df, electricity_df, pollution_df = extract_data(azureDB)

        # Transform data
        ev_summary = transform_ev_data(ev_df)
        electricity_subset = transform_electricity_data(electricity_df)
        pollution_pivot = transform_pollution_data(pollution_df)

        # Merge datasets
        final_df = merge_datasets(ev_summary, electricity_subset, pollution_pivot)

        # Create dimension and fact tables
        time_dim, suburb_dim, vehicle_type_dim, fuel_type_dim, final_df = create_dimension_tables(final_df, ev_df)
        ev_impact_fact, energy_pollution_fact = create_fact_tables(final_df, suburb_dim)

        # Print final_df for verification
        print("\nFinal merged and scaled data:")
        print(final_df.head())

        # Save final_df to CSV
        final_df.to_csv('final_scaled_dataset.csv', index=False)
        print("\nFinal dataset saved with scaled metrics to 'final_scaled_dataset.csv'")
        
        # Load to Azure
        load_to_azure(azureDB, time_dim, suburb_dim, vehicle_type_dim, fuel_type_dim, ev_impact_fact, energy_pollution_fact)

        print("\nETL process completed successfully.")
    except Exception as e:
        print(f"ETL process failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
