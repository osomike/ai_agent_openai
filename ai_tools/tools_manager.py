from utils.logger import Logger
from ai_tools.tools.azure_blob_storage import AzureBlobStorageTool
from ai_tools.tools.local import LocalStorageTool

class ToolsManager:
    def __init__(self, config: dict, logger: Logger = None):
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="ToolsManager")

        # Initialize the tools
        self.azure_blob_tool = AzureBlobStorageTool(config=config)
        self.local_files_tool = LocalStorageTool(config=config)

        self.tools = {
            "list_blob_files": self.azure_blob_tool.list_blob_files,
            "download_blob": self.azure_blob_tool.download_blob,
            "upload_blob": self.azure_blob_tool.upload_blob,
            "list_local_files": self.local_files_tool.list_local_files,}

        self.tools_description = [
            # Azure Blob Storage tools
            {
                "type": "function",
                "function": {
                    "name": "list_blob_files",
                    "description":
                        "List all files in a specified Azure Blob Storage container. If no container is " \
                        "specified, the default container will be used.",
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
                    "description":
                        "Download a blob file from Azure Blob Storage. If no container is specified, the default " \
                        "container will be used.",
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
                    "description":
                        "Upload a file to an Azure Blob Storage. If no container is specified, the default container " \
                        "will be used.",
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
            },
            # Local Storage tools
            {
                "type": "function",
                "function": {
                    "name": "list_local_files",
                    "description":
                        "List local files on a given folder path. If no path is specified, the default path will " \
                        "be used.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "local_folder": {
                                "type": "string",
                                "description": "(Optional) The folder path where the files scan will be performed"
                            }
                        },
                        #"required": ["blob_name"]
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
        """
        Executes a specified tool with the provided arguments.

        Args:
            tool_name (str): The name of the tool to execute. Must be a valid tool name
                             present in the list of available tools.
            arguments (dict): A dictionary of arguments to pass to the tool during execution.

        Returns:
            Any: The result of the tool execution if the tool is found and executed successfully.
            dict: An error dictionary with an error message if the tool is not found.

        Logs:
            - Logs an info message when a tool is successfully executed.
            - Logs an error message if the specified tool is unknown.
        """
        if tool_name in self.list_tools():
            self.logger.info(f"Executing tool: '{tool_name}' with arguments: '{arguments}'")
            return self.get_tool(tool_name)(**arguments)

        self.logger.error(f"Unknown tool: '{tool_name}'")
        return {"error": f"Unknown tool '{tool_name}'"}
