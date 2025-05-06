from utils.logger import Logger
from tools.tools.weather import WeatherTools
from tools.tools.jokes import JokesTool

class ToolsManager:
    def __init__(self, logger: Logger = None):
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="ToolsManager")

        self.tools = {
            "get_weather": WeatherTools().get_weather,
            "get_random_joke": JokesTool().get_random_joke}

        self.tools_description = [
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
                    "name": "get_random_joke",
                    "description": "Get a random joke.",
                    # "parameters": {
                    #     "type": "object",
                    #     "properties": {
                    #         "location": {
                    #             "type": "string",
                    #             "description": "The city or location to get the weather for."
                    #         }
                    #     },
                    #     "required": ["location"]
                    # }
                }
            },
        ]

    def get_tool(self, name):
        """Get a tool by name."""
        return self.tools.get(name)

    def list_tools(self):
        """List all tools."""
        return list(self.tools.keys())

    def execute_tool(self, tool_name, arguments):
        if tool_name in self.list_tools():
            self.logger.info(f"Executing tool: '{tool_name}' with arguments: '{arguments}'")
            return self.get_tool(tool_name)(**arguments)
        else:
            self.logger.error(f"Unknown tool: '{tool_name}'")
            return {"error": f"Unknown tool '{tool_name}'"}