import yaml
import openai
from openai import AzureOpenAI
from logger import DiPLogger

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

    def reset_conversation(self):
        self.logger.info("Resetting conversation history...")
        self.conversation = [{"role": "system", "content": self.system_prompt}]

    def start(self):
        self.logger.info("Starting conversation...")
        print(f"{self.assistant_name}: {self.system_prompt}")
        while True:
            user_input = input(f"{self.user_name}: ")
            if user_input.lower() == "exit":
                print("Exiting chat...")
                break

            if user_input.lower() == "reset":
                self.reset_conversation()
                print(f"{self.assistant_name}: Conversation reset.")
                continue

            response = self.chat(user_input)
            print(f"{self.assistant_name}: {response}")
if __name__ == "__main__":
    agent = AiAgent()
    agent.start()
