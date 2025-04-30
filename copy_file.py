import os
from azure.storage.blob import BlobServiceClient

# Set these variables
AZURE_CONNECTION_STRING = "your_connection_string"
CONTAINER_NAME = "your_container_name"
LOCAL_FILE_PATH = "path/to/your/local/file.txt"
BLOB_NAME = os.path.basename(LOCAL_FILE_PATH)

def upload_file_to_azure(local_file_path, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {local_file_path} to {container_name}/{blob_name}")

if __name__ == "__main__":
    upload_file_to_azure(LOCAL_FILE_PATH, CONTAINER_NAME, BLOB_NAME)