import os

from utils.logger import Logger

from azure.storage.blob import ContainerClient
from azure.core import exceptions as azure_exceptions

class AzureBlobStorageTool:

    def __init__(self, config: dict, logger : Logger = None):

        self.connection_string = config["azure_blob"]["connection_string"]
        self.local_folder = config["local_storage"]["folder"]
        self.default_container = config["azure_blob"]["default_container"]

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="Blob Storage Manager")

        self.logger.info("Initializing Azure Blob Storage Manager")

    def list_blob_files(self, container_name: str = None) -> list:

        if container_name in [None, ""]:
            container_name = self.default_container

        self.logger.debug(f"Listing blobs in container: '{container_name}'")

        container_client = ContainerClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=container_name
        )

        blob_list = container_client.list_blobs()
        try:
            files = [blob.name for blob in blob_list]
            self.logger.debug(f"Found {len(files)} files in container.")
        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error listing blobs from container '{container_name}': {e}")
            files = []

        return {"container_name": container_name, "files": files}

    def download_blob(self, blob_name: str, container_name: str = None) -> list:

        if container_name in [None, ""]:
            container_name = self.default_container

        self.logger.debug(f"Downloading: '{blob_name}' from container: '{container_name}'")

        container_client = ContainerClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=container_name
        )

        try:
            output_file = os.path.join(self.local_folder, os.path.basename(blob_name))
            self.logger.info(f"Downloading blob to: '{output_file}'")

            with open(file=output_file, mode="wb") as sample_blob:
                download_stream = container_client.download_blob(blob=blob_name)
                sample_blob.write(download_stream.readall())
            status = "success"

        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error while downloading the blob {blob_name}: {e}")
            status = "error"

        return {"container_name": container_name, "output_file": output_file, "status": status}

    def upload_blob(self, local_file_path: str, target_folder : str = "drop_zone", container_name: str = None) -> list:
        if container_name in [None, ""]:
            container_name = self.default_container

        if target_folder is None:
            target_folder = "drop_zone"

        self.logger.debug(f"Attempting to upload: '{local_file_path}' to container: '{container_name}' in folder: '{target_folder}'")

        container_client = ContainerClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=container_name
        )

        try:
            output_blob = os.path.join(target_folder, os.path.basename(local_file_path))

            self.logger.info(f"Uploading blob to: '{output_blob}'")
            with open(file=local_file_path, mode="rb") as data:
                blob_client = container_client.upload_blob(name=output_blob, data=data, overwrite=True)
            status = "success"
        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error while uploading the blob {output_blob}: {e}")
            status = "error"

        return {"container_name": container_name, "output_blob": output_blob, "status": status}

