import os
from typing import Optional

import logging
from azure.storage.blob import ContainerClient
from azure.core import exceptions as azure_exceptions

from ai_tools.tools.tools_abstract import AIToolsAbstract
from utils.logger import Logger

class AzureBlobStorageTool(AIToolsAbstract):

    def __init__(self, config: dict, logger : Optional[Logger] = None, log_level: int = logging.INFO):

        super().__init__()
        self.connection_string = config["azure_blob"]["connection_string"]
        self.local_folder = config["local_storage"]["folder"]
        self.default_container = str(config["azure_blob"]["default_container"])

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="Blob Storage Manager", log_level=log_level)

        self.logger.info("Initializing Azure Blob Storage Manager")
        self._tools = {
            "list_blob_files": self.list_blob_files,
            "download_blob": self.download_blob,
            "upload_blob": self.upload_blob,
            "delete_blob": self.delete_blob
        }
        self._tools_description = [
            # Azure Blob Storage tools
            {
                "type": "function",
                "function": {
                    "name": "list_blob_files",
                    "description":
                        "List all files in a specified Azure Blob Storage container. If no container is " \
                        "specified, the default container will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        #"required": ["container_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "download_blob",
                    "description":
                        "Download a blob file from Azure Blob Storage. If no container is specified, the default " \
                        "container will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "blob_name": {
                                "type": "string",
                                "description": "The name of the blob file to download."
                            },
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        "required": ["blob_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "upload_blob",
                    "description":
                        "Upload a file to an Azure Blob Storage. If no container is specified, the default container " \
                        "will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "local_file_path": {
                                "type": "string",
                                "description": "Local file path of file to upload to the Azure Blob Storage container"
                            },
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        "required": ["local_file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_blob",
                    "description":
                        "Delete a blob file from Azure Blob Storage. If no container is specified, the default " \
                        "container will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "blob_name": {
                                "type": "string",
                                "description": "The name of the blob file to download."
                            },
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        "required": ["blob_name"]
                    }
                }
            },
        ]

    def list_blob_files(self, container_name: Optional[str] = None) -> dict:
        """
        Lists all blob files in the specified Azure Blob Storage container.

        Args:
            container_name (str, optional): The name of the container to list blobs from.
                If not provided or is None/empty, the default container will be used.

        Returns:
            dict: A dictionary containing:
                - "container_name" (str): The name of the container.
                - "files" (list): A list of blob file names in the container.

        Raises:
            azure_exceptions.HttpResponseError: If there is an issue accessing the container or listing blobs.
        """

        if container_name in [None, "", "{}"]:
            container_name = self.default_container
  
        if not isinstance(container_name, str):
            container_name = str(container_name)

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

    def download_blob(self, blob_name: str, container_name: Optional[str] = None) -> dict:
        """
        Downloads a blob from an Azure Blob Storage container to a local file.

        Args:
            blob_name (str): The name of the blob to download.
            container_name (str, optional): The name of the container from which to download the blob.
                If not provided or empty, the default container will be used.

        Returns:
            dict: A dictionary containing the following keys:
                - "container_name" (str): The name of the container from which the blob was downloaded.
                - "output_file" (str): The local file path where the blob was downloaded.
                - "status" (str): The status of the operation, either "success" or "error".

        Raises:
            azure_exceptions.HttpResponseError: If an error occurs during the blob download process.

        """

        if container_name in [None, ""]:
            container_name = self.default_container

        if not isinstance(container_name, str):
            container_name = str(container_name)

        self.logger.debug(f"Downloading: '{blob_name}' from container: '{container_name}'")

        container_client = ContainerClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=container_name
        )

        output_file = os.path.join(self.local_folder, os.path.basename(blob_name))
        self.logger.info(f"Downloading blob to: '{output_file}'")

        try:
            with open(file=output_file, mode="wb") as sample_blob:
                download_stream = container_client.download_blob(blob=blob_name)
                sample_blob.write(download_stream.readall())
            status = "success"

        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error while downloading the blob {blob_name}: {e}")
            status = "error"

        return {"container_name": container_name, "output_file": output_file, "status": status}

    def upload_blob(self, local_file_path: str, target_folder : str = "drop_zone",
                    container_name: Optional[str] = None) -> dict:
        """
        Uploads a local file to an Azure Blob Storage container.

        Args:
            local_file_path (str): The path to the local file to be uploaded.
            target_folder (str, optional): The target folder within the container where the file will be uploaded. 
                                           Defaults to "drop_zone".
            container_name (str, optional): The name of the Azure Blob Storage container. If not provided, 
                                            the default container will be used.

        Returns:
            dict: A dictionary containing the following keys:
                - "container_name" (str): The name of the container where the file was uploaded.
                - "output_blob" (str): The path of the uploaded blob within the container.
                - "status" (str): The status of the upload operation ("success" or "error").

        Raises:
            azure_exceptions.HttpResponseError: If an error occurs during the upload process.

        Notes:
            - Logs debug and info messages during the upload process.
            - Logs an error message if the upload fails.
        """
        if container_name in [None, "", "{}"]:
            container_name = self.default_container

        if not isinstance(container_name, str):
            container_name = str(container_name)

        if target_folder in [None, "", "{}"]:
            target_folder = "drop_zone"

        if not isinstance(target_folder, str):
            target_folder = str(target_folder)

        self.logger.debug(
            f"Attempting to upload: '{local_file_path}' to container: '{container_name}' in folder: " \
            f"'{target_folder}'")

        container_client = ContainerClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=container_name
        )

        output_blob = os.path.join(target_folder, os.path.basename(local_file_path))
        self.logger.info(f"Uploading blob to: '{output_blob}'")

        try:
            with open(file=local_file_path, mode="rb") as data:
                container_client.upload_blob(name=output_blob, data=data, overwrite=True)
            status = "success"
        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error while uploading the blob {output_blob}: {e}")
            status = "error"

        return {"container_name": container_name, "output_blob": output_blob, "status": status}

    def delete_blob(self, blob_name: str, container_name: Optional[str] = None) -> dict:
        """
        Deletes a blob from the specified Azure Blob Storage container.

        Args:
            blob_name (str): The name of the blob to delete.
            container_name (str, optional): The name of the container from which the blob will be deleted.
                If not provided or set to None/empty string, the default container will be used.

        Returns:
            dict: A dictionary containing the following keys:
                - "container_name" (str): The name of the container from which the blob was deleted.
                - "blob" (str): The name of the blob that was deleted.
                - "status" (str): The status of the operation, either "success" or "error".
        """
        if container_name in [None, "", "{}"]:
            container_name = self.default_container

        if not isinstance(container_name, str):
            container_name = str(container_name)

        self.logger.debug(f"Deleting: '{blob_name}' from container: '{container_name}'")

        container_client = ContainerClient.from_connection_string(
            conn_str=self.connection_string,
            container_name=container_name
        )

        try:
            self.logger.warning(f"Deleting blob: '{blob_name}'")

            container_client.delete_blob(blob=blob_name)
            status = "success"

        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error while deleting the blob {blob_name}: {e}")
            status = "error"

        return {"container_name": container_name, "blob": blob_name, "status": status}
