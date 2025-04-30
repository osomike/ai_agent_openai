import yaml
import tiktoken
from openai import AzureOpenAI
from logger import DiPLogger
from utils import format_terminal_text

class AiAgent:
    def __init__(self, name: str = 'AiAgent', config_path: str = 'config/settings.yaml'):
        self.name = name

        self.assistant_name = 'AI Assistant'
        self.user_name = 'Human User'
        self.logger = DiPLogger(logger_name=name)

        self.logger.info(f'Loading config file from \'{config_path}\'...')
        with open(config_path) as f:
            config = yaml.safe_load(f)

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


    def ask(self, user_prompt: str,
                      system_prompt: str = 'You are chat assistant and willing to help to a human user.',
                      temperature: float = 0.5,
                      max_completion_tokens: int = 1000) -> str:
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
        self.logger.info("Adding user message to chat history...")
        self.conversation.append({"role": "user", "content": user_prompt})

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=self.conversation,
            #temperature=temperature,
            max_completion_tokens=max_tokens,
        )

        reply = response.choices[0].message.content
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
        while True:
            
            user_input = input(f"{user_name_formated}: ")
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break

            if user_input.lower() == "reset":
                self.reset_conversation()
                print(f"{self.assistant_name}: Conversation reset.")
                continue

            if user_input.lower() == "count_tokens":
                total_tokens = self.count_tokens()
                print(f"{self.assistant_name}: Total tokens in conversation: {total_tokens}")
                continue

            if user_input.lower() == "show_chat":
                
                print("Chat history:")
                print("-" * 50)
                for message in self.conversation:
                    role = message["role"]
                    content = message["content"]

                    if role == "assistant":
                        print(f"{ai_name_formated}: {content}")
                        print("-" * 50)
                    elif role == "user":
                        print(f"{user_name_formated}: {content}")
                    elif role == "system":
                        print(f"{system_name_formated}: {content}")
                    else:
                        print(f"{role}: {content}")
                continue

            response = self.chat(user_input)
            user_tokens = self.count_tokens(user_input)

            print(f"{ai_name_formated}: {response}")

            assistant_tokens = self.count_tokens(response)
            self.total_token_counter += user_tokens + assistant_tokens
            total_tokens_formatter = format_terminal_text(text=f'Total tokens: {self.total_token_counter}', color="red", bold=True)

            self.logger.info(f"User tokens: {user_tokens} | Assistant tokens: {assistant_tokens} | {total_tokens_formatter}")

if __name__ == "__main__":
    agent = AiAgent()
    agent.start()
