import yaml
import json

import tiktoken
from openai import AzureOpenAI
from azure.storage.blob import ContainerClient
from logger import DiPLogger
from utils import format_terminal_text
from azure.core import exceptions as azure_exceptions
class AiAgent:
    def __init__(self, name: str = 'AI Agent', config_path: str = 'config/settings.yaml'):
        self.name = name

        self.assistant_name = 'AI Agent'
        self.user_name = 'Human User'
        self.logger = DiPLogger(logger_name=name, log_level="DEBUG")

        self.logger.info(f'Loading config file from \'{config_path}\'...')
        with open(config_path) as f:
            config = yaml.safe_load(f)

        # Load azure OpenAI configuration
        self.endpoint = config['azure_openai']['endpoint']
        self.model_name = config['azure_openai']['model_name']
        self.deployment = config['azure_openai']['deployment']
        self.api_key = config['azure_openai']['api_key']
        self.api_version = config['azure_openai']['api_version']

        self.logger.info('starting OpenAI client...')
        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )

        # Start with a system prompt and empty conversation
        self.system_prompt = "You are a helpful chat assistant."
        self.conversation = [{"role": "system", "content": self.system_prompt}]
        self.total_token_counter = 0   

        try:
            self.encoding = tiktoken.encoding_for_model(self.model_name)
            encoder_from = self.model_name
        except KeyError:
            encoder_from = "cl100k_base"
            self.encoding = tiktoken.encoding_for_model(self.model_name)

        self.logger.info(f"Using encoder: {encoder_from}")

        # Load Azure storage account configuration
        self.storage_connection_string = config['azure_blob']['connection_string']
        self.container = config['azure_blob']['container_name']

        # Available tools for the agent
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the current weather for a specified location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city or location to get the weather for."
                            }
                        },
                        "required": ["location"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_files_in_blob",
                    "description": "List files in an given Azure Blob Storage container.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "container_name": {
                                "type": "string",
                                "description": "Name of the Azure Blob Storage container."
                            }
                        },
                        "required": ["container_name"]
                    }
                }
            }
        ]

    def get_weather(self, location: str) -> dict:
        self.logger.debug(f"Getting weather for location: {location}")
        return {"location": location, "temperature": "25°C", "condition": "Sunny"}

    def list_blob_files(self, container_name: str = None) -> list:
        if container_name is None:
            container_name = self.container
        self.logger.debug(f"Listing blobs in container: {container_name}")
        
        container_client = ContainerClient.from_connection_string(
            conn_str=self.storage_connection_string,
            container_name=container_name
        )

        blob_list = container_client.list_blobs()
        self.logger.debug(f"blob list {blob_list}")
        try:
            files = [blob.name for blob in blob_list]
            self.logger.debug(f"Found {len(files)} files in container.")
        except azure_exceptions.HttpResponseError as e:
            self.logger.error(f"Error listing blobs from container {container_name}: {e}")
            files = []

        return {"container_name": container_name, "files": files}

    def ask(self, user_prompt: str,
                      system_prompt: str = 'You are chat assistant and willing to help to a human user.',
                      temperature: float = 0.5,
                      max_completion_tokens: int = 10000) -> str:
        """
        Ask something to the OpenAI model and get the response.
        """
        self.logger.info("Asking something to the OpenAI model...")
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            model=self.deployment
        )

        reply = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": reply})

        return reply

    def chat(self, user_prompt: str, temperature: float = 0.5, max_tokens: int = 10000) -> str:
        #self.logger.info("Adding user message to chat history...")
        self.conversation.append({"role": "user", "content": user_prompt})

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=self.conversation,
            #temperature=temperature,
            tools=self.tools,
            max_completion_tokens=max_tokens,
        )
        if response.choices[0].message.tool_calls:
            self.logger.info(f"A call to tools have been performed: \'{response.choices[0].message.tool_calls}\'")

            tool_calls_list = []
            tool_response_list = []
            for tool_call in response.choices[0].message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                match function_name:
                    case "get_weather":
                        tools_result_i = self.get_weather(arguments.get("location"))
                    case "get_files_in_blob":
                        tools_result_i = self.list_blob_files(arguments.get("container_name"))
                    case _:
                        self.logger.error(f"Unknown function call: {function_name}")
                        tools_result_i = {"error": f"Unknown function call \'{function_name}\'"}
                        self.logger.error(f"Non existen function call returned: {tools_result_i}")
                        continue

                self.logger.debug(f"Function call result: {tools_result_i}")
                tool_calls_list.append({
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": str(arguments)
                        }
                    })
                tool_response_list.append(
                    {"role": "tool",
                     #"name": function_name,
                     "content": json.dumps(tools_result_i),
                     "tool_call_id": tool_call.id})

            self.conversation.append(
                            {"role": "assistant",
                            "content": None,
                            "tool_calls": tool_calls_list})
            for tool_response in tool_response_list:
                self.conversation.append(tool_response)
            self.logger.debug(f"Tool call result added to conversation history: {self.conversation}")

        final_response = self.client.chat.completions.create(
            model=self.deployment,
            tools=self.tools,
            messages=self.conversation,
            max_completion_tokens=max_tokens,
        )

        reply = final_response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": reply})
        return reply


    def count_tokens(self, message):

        # This structure is valid for GPT-4-turbo / o1
        # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 3
        tokens_per_name = 1
        total_tokens = 0

        total_tokens += tokens_per_message
        total_tokens += len(self.encoding.encode(message))
        total_tokens += tokens_per_name
        total_tokens += 3  # Priming

        return total_tokens

    def reset_conversation(self):
        self.logger.info("Resetting conversation history...")
        self.conversation = [{"role": "system", "content": self.system_prompt}]

    def start(self):
        self.logger.info("Starting conversation...")

        user_name_formated = format_terminal_text(text=self.user_name, color="green", bold=True)
        ai_name_formated = format_terminal_text(text=self.assistant_name, color="cyan", bold=True)
        system_name_formated = format_terminal_text(text='system', color="yellow", bold=True)
        tool_name_formated = format_terminal_text(text='AI tool', color="magenta", bold=True)
        content_label_formated = format_terminal_text(text='content', color="red", bold=False)
        message_label_formated = format_terminal_text(text='message', color="red", bold=False)
        tool_calls_label_formated = format_terminal_text(text='tool_calls', color="red", bold=False)
        while True:
            
            user_input = input(f"{user_name_formated}: ")
            if user_input.lower() == "exit/":
                print("Exiting chat...")
                break

            if user_input.lower() == "reset/":
                self.reset_conversation()
                print(f"{self.assistant_name}: Conversation reset.")
                continue

            if user_input.lower() == "tokens/":
                total_tokens = self.count_tokens()
                print(f"{self.assistant_name}: Total tokens in conversation: {total_tokens}")
                continue

            if user_input.lower() == "history/":
                
                print("Chat history:")
                print("-" * 50)
                for message in self.conversation:
                    role = message["role"]
                    content = message["content"]
                    tool_calls = message.get("tool_calls", None)

                    if role == "assistant":
                        print(f"{ai_name_formated}:\n\t{content_label_formated}: {content}\n\t{tool_calls_label_formated}: {tool_calls}")
                        if tool_calls is None:
                            print("-" * 50)
                    elif role == "user":
                        print(f"{user_name_formated}:\n\t{content_label_formated}: {content}")
                    elif role == "system":
                        print(f"{system_name_formated}:\n\t{content_label_formated}: {content}")
                    elif role == "tool":
                        print(f"{tool_name_formated}:\n\t{content_label_formated}: {content}")
                    else:
                        print(f"{role}: {content}")
                continue

            response = self.chat(user_input)
            user_tokens = self.count_tokens(user_input)

            print(f"{ai_name_formated}: {response}")

            assistant_tokens = self.count_tokens(response)
            self.total_token_counter += user_tokens + assistant_tokens
            total_tokens_formatter = format_terminal_text(text=f'Total tokens on chat history: {self.total_token_counter}', color="red", bold=True)

            self.logger.info(f"Last user message tokens: {user_tokens} | Last assistant message tokens: {assistant_tokens} | {total_tokens_formatter}")

if __name__ == "__main__":
    agent = AiAgent()
    #print(agent.list_blob_files())
    agent.start()
