from utils.logger import Logger
from tools.tools.weather import WeatherTools
from tools.tools.jokes import JokesTool
from tools.tools.azure_blob_storage import AzureBlobStorageTool

class ToolsManager:
    def __init__(self, config: dict, logger: Logger = None):
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="ToolsManager")

        # Initialize the tools
        self.azure_blob_tool = AzureBlobStorageTool(config=config)

        self.tools = {
            "get_weather": WeatherTools().get_weather,
            "get_random_joke": JokesTool().get_random_joke,
            "list_blob_files": self.azure_blob_tool.list_blob_files,
            "download_blob": self.azure_blob_tool.download_blob,
            "upload_blob": self.azure_blob_tool.upload_blob,}

        self.tools_description = [
            # Weather tools
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
            # Jokes tools
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
            # Azure Blob Storage tools
            {
                "type": "function",
                "function": {
                    "name": "list_blob_files",
                    "description": "List all files in a specified Azure Blob Storage container. If no container is specified, the default container will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        #"required": ["container_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "download_blob",
                    "description": "Download a blob file from Azure Blob Storage. If no container is specified, the default container will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "blob_name": {
                                "type": "string",
                                "description": "The name of the blob file to download."
                            },
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        "required": ["blob_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "upload_blob",
                    "description": "Upload a file to an Azure Blob Storage. If no container is specified, the default container will be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "local_file_path": {
                                "type": "string",
                                "description": "Local file path of file to upload to the Azure Blob Storage container"
                            },
                            "container_name": {
                                "type": "string",
                                "description": "(Optional) The name of the Azure Blob Storage container."
                            }
                        },
                        "required": ["local_file_path"]
                    }
                }
            }
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