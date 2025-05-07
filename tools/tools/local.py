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
