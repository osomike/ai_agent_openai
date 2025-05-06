from config.config_loader import ConfigLoader
from utils.clients import AzureOpenAIInterface
from utils.logger import Logger
from utils.text_formatting import format_terminal_text

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
        # self.tools = tool_manager.get_tools()
        # self.blob_manager = blob_manager
        # self.logger = logger
        # self.conversation = [{"role": "system", "content": self.config['system_prompt']}]
        # self.client = self._initialize_openai_client()

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
            reply = self.ai_client.chat_completitions(conversation=self.conversation)
            self.conversation.append({"role": "assistant", "content": reply})
        except Exception as e:
            self.logger.error(f"Error from LLM API: {e}")
            raise RuntimeError(f"Error from LLM API: {e}")
            #return "I'm sorry, I couldn't process your request."
        return reply

    def start(self):
        self.logger.info("Starting conversation...")

        user_name_formated = format_terminal_text(text=self.user_name, color="green", bold=True)
        ai_name_formated = format_terminal_text(text=self.assistant_name, color="cyan", bold=True)
        system_name_formated = format_terminal_text(text="system", color="yellow", bold=True)
        tool_name_formated = format_terminal_text(text="AI tool", color="magenta", bold=True)
        content_label_formated = format_terminal_text(text="content", color="red", bold=False)
        tool_calls_label_formated = format_terminal_text(text="tool_calls", color="red", bold=False)

        while True:
            user_input = input(f"{user_name_formated}: ")
            match user_input:
                case "exit/":
                    self.logger.info("Exiting conversation...")
                    break
                case "clear/":
                    self.logger.info("Clearing conversation...")
                    self.conversation = [{"role": "system", "content": self.system_prompt}]
                    continue
                case _:
                    reply = self.ask(user_input)
                    print(f"{ai_name_formated}: {reply}")
                    # print(f"{tool_name_formated}: {self.conversation[-1]['tool_calls']}")
