from typing import Optional
import logging
import os

class Logger:
    """
    A custom logger class for handling logging functionality.
    """
    def __init__(self, logger_name: str = "Default Logger", log_level=logging.INFO, log_to_stdout: bool = True,
                 log_to_file: bool = False, log_file_folder_path: str ="./",
                 logger_name_max_length: Optional[int] = None, prefix: str = 'log') -> None:

        """
        Initializes the DiPLogger.

        Parameters:
            logger_name (str): A name for the logger to be represented within the output strings.
            log_level (logging.INFO): Log level to set. Available: logging.INFO, logging.DEBUG, logging.WARNING,
                logging.ERROR. Defaults to logging.INFO.
            log_to_stdout (bool): Whether to log messages to standard output (stdout).
            log_to_file (bool): Whether to log messages to a file.
            log_file_folder_path (str): The folder path where the log file will be created.
            prefix (str): prefix to add to the logger file name. It defaults to a 'now' datetime
        """

        if logger_name_max_length is None:
            self.logger_name_max_length = len(str(logger_name))
        # additional parameters
        self.log_to_stdout = log_to_stdout
        self.log_to_file = log_to_file
        self.log_file_folder_path = log_file_folder_path
        self.logger_name = logger_name[:self.logger_name_max_length]
        self.prefix = prefix
        self.log_file_path = self._get_log_file_path()

        # setting logger
        self.logger = logging.Logger(name=self.logger_name, level=log_level)

        # Define log formatting
        formatter = \
            logging.Formatter(
                fmt=f"%(asctime)s | %(name)-{self.logger_name_max_length}s | %(levelname)-8s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S")

        # Clear existing handlers to avoid accumulation
        self.clear_handlers()

        if log_to_stdout:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(log_level)
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

        # Create a file handler if log_to_file is True
        if log_to_file:
            file_handler = logging.FileHandler(self.log_file_path, mode="w")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            self.logger.addHandler(file_handler)

    def __str__(self) -> str:
        """
        Generates a string representation of the logger

        Returns:
            str: representation
        """
        return self.logger_name

    def _get_log_file_path(self) -> str:
        """
        Generates the log file path by using the logger path, name abd prefix datetime provided during initialization

        Returns:
            str: The modified log file path.
        """

        # Create folder path if it does not exist
        if not os.path.exists(self.log_file_folder_path):
            os.makedirs(self.log_file_folder_path)

        # replace unwanted characters on the log file name
        log_file_name = self.logger_name.replace(' ', '')

        log_file_path = os.path.join(self.log_file_folder_path, f'{self.prefix}_{log_file_name}.log')

        return log_file_path

    def clear_handlers(self):
        """
        Clears existing logging handlers attached to the logger.
        """
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

    def info(self, message: str) -> None:
        """
        Logs an INFO-level message.

        Parameters:
            message (str): The message to be logged.
        """

        self.logger.info(message)

    def error(self, message: str) -> None:
        """
        Logs an ERROR-level message.

        Parameters:
            message (str): The message to be logged.
        """
        self.logger.error(message)

    def warning(self, message: str) -> None:
        """
        Logs a WARNING-level message.

        Parameters:
            message (str): The message to be logged.
        """

        self.logger.warning(message)

    def debug(self, message: str) -> None:
        """
        Logs a DEBUG-level message.

        Parameters:
            message (str): The message to be logged.
        """
        self.logger.debug(message)
