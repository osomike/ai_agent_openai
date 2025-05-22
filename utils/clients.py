import logging
from typing import Optional, List, Iterable
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionAssistantMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionSystemMessageParam, ChatCompletionToolMessageParam

import openai
import tiktoken

from utils.logger import Logger


class AzureOpenAIInterface:
    def __init__(self, config: dict, logger: Optional[Logger] = None, log_level: int = logging.INFO):
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="AzureOpenAIInterface", log_level=log_level)

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

    def initialize_encoder(self) -> tiktoken.Encoding:
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

    def validate_messages(self, messages: Iterable[dict]) -> List[ChatCompletionMessageParam]:
        """
        Validates and converts a sequence of message dictionaries into their corresponding
        ChatCompletionMessageParam objects.

        Each message dictionary must contain 'role' and 'content' keys, and the 'role' must be
        one of: 'user', 'assistant', 'system', or 'tool'. The method raises a ValueError if any
        message is not a dictionary, is missing required keys, or has an invalid role.

        Args:
            messages (Iterable[dict]): An iterable of message dictionaries to validate and convert.

        Returns:
            List[ChatCompletionMessageParam]: A list of validated and instantiated message objects.

        Raises:
            ValueError: If a message is not a dictionary, is missing required keys, or has an invalid role.
        """
        validated_messages = []

        d = {
            "user": ChatCompletionUserMessageParam,
            "assistant": ChatCompletionAssistantMessageParam,
            "system": ChatCompletionSystemMessageParam,
            "tool": ChatCompletionToolMessageParam,}
        for message in messages:
            if not isinstance(message, dict):
                raise ValueError("Each message must be a dictionary.")
            if "role" not in message or "content" not in message:
                raise ValueError("Each message must contain 'role' and 'content' keys.")

            message_class = d.get(message["role"])
            if message_class is None:
                raise ValueError(f"Invalid role '{message['role']}' in message.")
            msg = message_class(**message)
            validated_messages.append(msg)
        return validated_messages

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
            self.logger.debug("Validating messages paramneters before sending to the LLM...")
            validated_conversation = self.validate_messages(conversation)

            response = self.client.chat.completions.create(
                messages=validated_conversation,
                model=self.deployment,
                max_completion_tokens=max_tokens,
                **kwargs
            )
            self.logger.info("Chat completion generated successfully")
        except Exception as e:
            self.logger.error(f"Failed to generate chat completion: {e}")
            raise RuntimeError(f"Failed to generate chat completion: {e}") from e

        return response
