import os
from utils.logger import Logger

class LocalStorageTool:
    def __init__(self, config: dict, logger: Logger = None):
        self.default_local_folder = config["local_storage"]["folder"]

        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="Local Storage Tool")

        self.logger.info("Initializing Local Storage Manager")

    def list_local_files(self, local_folder: str) -> list:
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
        if local_folder in [None, ""]:
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
