import yaml
from utils.logger import Logger

class ConfigLoader:
    def __init__(self, config_path : str, logger: Logger = None):
        """
        Responsible for loading and managing configuration files.

        Attributes:
            config_path (str): The file path to the configuration file.
            logger (Logger): An optional logger instance for logging messages. If not provided, a default logger
                is created.
            config (dict): The loaded configuration data.
        """
        self.config_path = config_path

        # Initialize logger
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="ConfigLoader")

        # Load the config file
        self.config = self.load_config()

    def load_config(self) -> dict:
        """
        Loads the configuration from a YAML file specified by the `config_path` attribute.

        This method reads the YAML file located at the path stored in `self.config_path`
        and parses its contents into a Python dictionary.

        Returns:
            dict: The parsed configuration data from the YAML file.

        Raises:
            FileNotFoundError: If the file at `self.config_path` does not exist.
            yaml.YAMLError: If there is an error parsing the YAML file.
        """
        self.logger.info(f"Loading config from {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
