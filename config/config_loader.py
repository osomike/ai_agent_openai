import yaml
from utils.logger import Logger

class ConfigLoader:
    def __init__(self, config_path : str, logger: Logger = None):

        self.config_path = config_path

        # Initialize logger
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="ConfigLoader")

        # Load the config file
        self.config = self.load_config()

    def load_config(self) -> dict:
        self.logger.info(f"Loading config from {self.config_path}")
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)