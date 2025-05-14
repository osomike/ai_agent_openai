import os
from utils.logger import Logger
from ai_tools.tools.tools_abstract import AIToolsAbstract

class LocalStorageTool(AIToolsAbstract):

    def __init__(self, config: dict, logger: Logger = None, log_level: str = "INFO"):

        super().__init__()
        self.default_local_folder = config["local_storage"]["folder"]

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="Local Storage Tool", log_level=log_level)

        self.logger.info("Initializing Local Storage Manager")

        self._tools = {
            "list_local_files": self.list_local_files,
            "delete_local_file": self.delete_local_file
        }

        self._tools_description = [
            {
                "type": "function",
                "function": {
                    "name": "list_local_files",
                    "description":
                        "List local files on a given folder path. If no path is specified, the default path will " \
                        "be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "local_folder": {
                                "type": "string",
                                "description": "(Optional) The folder path where the files scan will be performed"
                            }
                        },
                        #"required": ["local_folder"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_local_file",
                    "description":
                        "Delete a local file given its full path.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The full file path of the local file to delete"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
        ]

    def list_local_files(self, local_folder: str) -> dict:
        """
        Lists the files in a specified local folder.

        Args:
            local_folder (str): The path to the local folder. If None or an empty string is provided, 
                                the default local folder will be used.

        Returns:
            dict: A dictionary containing:
                - "local_folder" (str): The path of the folder that was listed.
                - "files" (list): A list of file names in the specified folder. Empty if an error occurs.
                - "status" (str): The status of the operation, either "success" or "error".
        """
        if local_folder in [None, "", "{}"]:
            local_folder = self.default_local_folder
        self.logger.debug(f"Listing files in local folder: '{local_folder}'")
        try:
            files = os.listdir(local_folder)
            self.logger.debug(f"Found {len(files)} files in local folder.")
            status = "success"
        except FileNotFoundError as e:
            self.logger.error(f"Error listing files from local folder '{local_folder}': {e}")
            files = []
            status = "error"

        return {"local_folder": local_folder, "files": files, "status": status}

    def delete_local_file(self, file_path: str) -> dict:
        """
        Deletes a local file at the specified file path.

        Args:
            file_path (str): The path to the file to be deleted.

        Returns:
            dict: A dictionary containing:
                - "file_path" (str): The path of the file that was attempted to be deleted.
                - "status" (str): The status of the operation, either "success" if the file was deleted,
                  or "error" if the file was not found or could not be deleted.
        """
        self.logger.warning(f"Deleting local file '{file_path}'")
        try:
            os.remove(file_path)
            self.logger.debug(f"Deleted file: {file_path}")
            status = "success"
        except FileNotFoundError as e:
            self.logger.error(f"Error deleting file '{file_path}': {e}")
            status = "error"

        return {"file_path": file_path, "status": status}
