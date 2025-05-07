import json

from config.config_loader import ConfigLoader
from utils.clients import AzureOpenAIInterface
from utils.logger import Logger
from utils.text_formatting import format_terminal_text
from ai_tools.tools_manager import ToolsManager

class AIAgent:
    def __init__(self, config_path: str, logger: Logger = None):

        self.config = ConfigLoader(config_path=config_path).config
        self.assistant_name = "AI Assistant"
        self.user_name = "Human User"


        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="AI Agent")

        self.logger.info("Initializing AI Agent")
        self.logger.info(f"Config: {self.config}")
        self.ai_client = AzureOpenAIInterface(config=self.config["azure_openai"])

        # Start with a system prompt and empty conversation
        self.system_prompt = \
            "You are a helpful AI assistant. You have access to several tools and can use more than one tool if the " \
            "user request requires it. Always reason about whether one or multiple tool calls are needed before " \
            "responding."
        self.conversation = [{"role": "system", "content": self.system_prompt}]

        # Initialize the tools manager
        self.tools_manager = ToolsManager(config=self.config)

        # Initialize the text formatting
        self.formatted_names = {
            "user": format_terminal_text(text=self.user_name, color="green", bold=True),
            "assistant": format_terminal_text(text=self.assistant_name, color="cyan", bold=True),
            "system": format_terminal_text(text="system", color="yellow", bold=True),
            "tool": format_terminal_text(text="AI tool", color="magenta", bold=True),
            "content_label": format_terminal_text(text="content", color="red", bold=False),
            "tool_calls_label": format_terminal_text(text="tool_calls", color="red", bold=False)
        }

    def print_conversation(self):

        for message in self.conversation:
            role = message["role"]
            content = message["content"]
            tool_calls = message.get("tool_calls", None)

            if role == "assistant":
                print(
                    f"{self.formatted_names['assistant']}:\n\t{self.formatted_names['content_label']}: {content}\n\t{self.formatted_names['tool_calls_label']}: {tool_calls}")
                if tool_calls is None:
                    print("-" * 50)
            elif role == "user":
                print(f"{self.formatted_names['user']}:\n\t{self.formatted_names['content_label']}: {content}")
            elif role == "system":
                print(f"{self.formatted_names['system']}:\n\t{self.formatted_names['content_label']}: {content}")
            elif role == "tool":
                print(f"{self.formatted_names['tool']}:\n\t{self.formatted_names['content_label']}: {content}")
            else:
                print(f"{role}: {content}")

    def ask(self, user_prompt: str) -> str:
        """
        Sends a message to the AI assistant and returns the response.

        Args:
            user_prompt (str): The message from the user.

        Returns:
            str: The response from the AI assistant.
        """
        self.conversation.append({"role": "user", "content": user_prompt})

        try:
            # Call the LLM API
            response = self.ai_client.chat_completitions(
                conversation=self.conversation,
                tools=self.tools_manager.tools_description)
            #self.conversation.append({"role": "assistant", "content": reply})

            # Check if the assistant's response contains tool calls
            if response.choices[0].message.tool_calls:
                self.logger.info(f"A call to tools have been performed: \'{response.choices[0].message.tool_calls}\'")
                tool_calls_list = []
                tool_response_list = []
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    # execute tool
                    tools_result = self.tools_manager.execute_tool(tool_name=function_name, arguments=arguments)
                    self.logger.debug(f"Function call result: {tools_result}")
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
                        "content": json.dumps(tools_result),
                        "tool_call_id": tool_call.id})

                # Add the tool calls to the conversation
                self.conversation.append({"role": "assistant", "content": None, "tool_calls": tool_calls_list})
                # Add the tool responses to the conversation
                for tool_response in tool_response_list:
                    self.conversation.append(tool_response)
                self.logger.debug(f"Tool call result added to conversation history: {self.conversation}")

                # Add the assistant's final response to the conversation
                final_response = self.ai_client.chat_completitions(
                        conversation=self.conversation,
                        tools=self.tools_manager.tools_description,
                    )
                reply = final_response.choices[0].message.content
                self.conversation.append({"role": "assistant", "content": reply})
            else:
                self.logger.info("No tool calls were made.")
                reply = response.choices[0].message.content
                self.conversation.append({"role": "assistant", "content": reply})
        except Exception as e:
            self.logger.error(f"Error from LLM API: {e}")
            raise RuntimeError(f"Error from LLM API: {e}")
            #return "I'm sorry, I couldn't process your request."
        return reply

    def start(self):
        self.logger.info("Starting conversation...")

        while True:
            user_input = input(f"{self.formatted_names['user']}: ")
            match user_input:
                case "exit/":
                    self.logger.info("Exiting conversation...")
                    break
                case "reset/":
                    self.logger.info("Reseting conversation history...")
                    self.conversation = [{"role": "system", "content": self.system_prompt}]
                    continue
                case "print/":
                    self.logger.info("Printing conversation history...")
                    self.print_conversation()
                    continue
                case _:
                    reply = self.ask(user_input)
                    print(f"{self.formatted_names['assistant']}: {reply}")
                    # print(f"{tool_name_formated}: {self.conversation[-1]['tool_calls']}")
