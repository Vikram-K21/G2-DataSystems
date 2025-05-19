import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import io
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text
import pyodbc
print(pyodbc.drivers())

# Load environment variables
load_dotenv()

# Azure Blob Storage credentials
account_storage = os.environ.get('ACCOUNT_STORAGE', 'etluts04')
connect_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
server = os.environ.get('DB_SERVER', 'etluts04server.database.windows.net')
database = os.environ.get('DB_DATABASE', 'etldb04')
username = os.environ.get('DB_USERNAME', 'vikramdc')
password = os.environ.get('DB_PASSWORD', 'Whyubuggin$19')
container_name = os.environ.get('CONTAINER_NAME', 'etlblob04')

# Validate environment variables
if not account_storage:
    raise ValueError("ACCOUNT_STORAGE environment variable is missing.")
print("Loaded ACCOUNT_STORAGE:", account_storage)
print("Loaded AZURE_STORAGE_CONNECTION_STRING:", connect_str if connect_str else "None (will use DefaultAzureCredential)")


engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+18+for+SQL+Server')



 
class AzureDB:
    def __init__(self, engine, local_path="./data", account_storage=account_storage):
        self.engine = engine  # Store the SQLAlchemy engine
        self.local_path = local_path
        self.account_url = f"https://{account_storage}.blob.core.windows.net"
        self.default_credential = DefaultAzureCredential()
        try:
            if connect_str and "AccountKey" in connect_str:
                self.blob_service_client = BlobServiceClient.from_connection_string(connect_str)
                print("Initialized BlobServiceClient with connection string")
            else:
                self.blob_service_client = BlobServiceClient(account_url=self.account_url, credential=self.default_credential)
                print("Initialized BlobServiceClient with DefaultAzureCredential")
        except Exception as e:
            print(f"Failed to initialize BlobServiceClient: {str(e)}")
            raise
        
    def access_container(self, container_name): 
        self.container_name = container_name
        try:
            self.container_client = self.blob_service_client.get_container_client(container=container_name)
            self.container_client.create_container()
            print(f"Created container {container_name}")
        except Exception as ex:
            print(f"Accessing existing container {container_name}: {ex}")
            self.container_client = self.blob_service_client.get_container_client(container=container_name)
            
    def delete_container(self):
        print("Deleting blob container...")
        try:
            self.container_client.delete_container()
            print("Done")
        except Exception as e:
            print(f"Failed to delete container: {str(e)}")
            raise
        
    def upload_blob(self, blob_name, blob_data=None):
        local_file_name = blob_name
        upload_file_path = os.path.join(self.local_path, local_file_name)
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=local_file_name)
        print(f"Uploading to Azure Storage as blob: {local_file_name}")
        try:
            if blob_data is not None:
                blob_client.upload_blob(blob_data, overwrite=True)
            else:
                with open(file=upload_file_path, mode="rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
        except Exception as e:
            print(f"Failed to upload blob {local_file_name}: {str(e)}")
            raise
                
    def list_blobs(self):
        print("Listing blobs...")
        blob_list = []
        try:
            blobs = self.container_client.list_blobs()
            for blob in blobs:
                print(f"\t{blob.name}")
                blob_list.append(blob.name)
            return blob_list
        except Exception as e:
            print(f"Failed to list blobs: {str(e)}")
            return blob_list
            
    def download_blob(self, blob_name):
        download_file_path = os.path.join(self.local_path, blob_name)
        print(f"Downloading blob to {download_file_path}")
        try:
            with open(file=download_file_path, mode="wb") as download_file:
                download_file.write(self.container_client.download_blob(blob_name).readall())
        except Exception as e:
            print(f"Failed to download blob {blob_name}: {str(e)}")
            raise
                
    def delete_blob(self, container_name: str, blob_name: str):
        print(f"Deleting blob {blob_name}")
        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.delete_blob()
        except Exception as e:
            print(f"Failed to delete blob {blob_name}: {str(e)}")
            raise
        
    def access_blob_csv(self, blob_name: str, **read_csv_kwargs) -> pd.DataFrame:
        print(f"Accessing blob {blob_name}")
        try:
            content = self.container_client.download_blob(blob_name).readall().decode('utf-8')
            return pd.read_csv(io.StringIO(content), **read_csv_kwargs)
        except Exception as e:
            print(f"Failed to access blob {blob_name}: {str(e)}")
            raise
    
    def upload_dataframe_sqldatabase(self, table_name, blob_data):
        try:
            blob_data.to_sql(table_name, self.engine, if_exists='replace', index=False)
            print(f"Table '{table_name}' uploaded successfully.")
        except Exception as e:
            print(f"Failed to upload table '{table_name}': {str(e)}")
            raise
                
    def append_dataframe_sqldatabase(self, blob_name, blob_data):
        print(f"Appending to table: {blob_name}")
        try:
            blob_data.to_sql(blob_name, self.engine, if_exists='append', index=False)
        except Exception as e:
            print(f"Failed to append table {blob_name}: {str(e)}")
            raise
    
    def delete_sqldatabase(self, table_name):
        try:
            with self.engine.connect() as con:
                trans = con.begin()
                con.execute(text(f"DROP TABLE IF EXISTS [dbo].[{table_name}]"))
                trans.commit()
                print(f"Table '{table_name}' deleted successfully.")
        except Exception as e:
            print(f"Failed to delete table '{table_name}': {str(e)}")
            raise
            
    def get_sql_table(self, query):        
        try:
            df = pd.read_sql_query(query, self.engine)
            result = df.to_dict(orient='records')
            return result
        except Exception as e:
            print(f"Failed to execute query: {str(e)}")
            raise
