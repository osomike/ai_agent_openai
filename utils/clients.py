import openai
import tiktoken

from utils.logger import Logger

class AzureOpenAIInterface:
    def __init__(self, config: dict, logger: Logger = None):
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="AzureOpenAIInterface")

        self.config = config

        # Load azure OpenAI configuration
        self.endpoint = self.config["endpoint"]
        self.model_name = self.config["model_name"]
        self.deployment = self.config["deployment"]
        self.api_key = self.config["api_key"]
        self.api_version = self.config["api_version"]

        # Initialize the Azure OpenAI client
        self.client = self.initialize_client()
        self.encoder = self.initialize_encoder()

    def initialize_client(self):
        """
        Initializes the OpenAI client with the provided configuration.
        """
        self.logger.info("Initializing OpenAI client")

        try:
            client = openai.AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )
            self.logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}") from e

        return client

    def initialize_encoder(self):
        """
        Returns the encoder for the specified model.
        """
        self.logger.info(f"Getting encoder for model: {self.model_name}")
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
            encoder_from = self.model_name
        except KeyError:
            self.logger.warning(f"Model {self.model_name} not found in tiktoken encodings, using default encoder")
            encoder_from = "cl100k_base"
            encoding = tiktoken.get_encoding(encoder_from)

        self.logger.info(f"Encoder initialized successfully, using encoder: {encoder_from}")

        return encoding

    def chat_completitions(self, conversation: list[dict], max_tokens: int = 10000, **kwargs):
        """
        Generates a chat completion using the OpenAI client.

        Args:
            conversation (list[dict]): The conversation history.
            **kwargs: Additional parameters for the chat completion.

        Returns:
            dict: The response from the OpenAI API.
        """
        self.logger.info("Generating chat completion")
        try:
            response = self.client.chat.completions.create(
                messages=conversation,
                model=self.deployment,
                max_completion_tokens=max_tokens,
                **kwargs
            )
            self.logger.info("Chat completion generated successfully")
        except Exception as e:
            self.logger.error(f"Failed to generate chat completion: {e}")
            raise RuntimeError(f"Failed to generate chat completion: {e}") from e

        return response
