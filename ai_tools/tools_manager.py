from utils.logger import Logger
from ai_tools.tools.azure_blob_storage import AzureBlobStorageTool
from ai_tools.tools.local import LocalStorageTool
from ai_tools.tools.databricks import DatabricksTool
class ToolsManager:
    def __init__(self, config: dict, logger: Logger = None):
        if logger:
            self.logger = logger
        else:
            self.logger = Logger(logger_name="ToolsManager")

        # Initialize the tools
        self.azure_blob_tool = AzureBlobStorageTool(config=config)
        self.local_files_tool = LocalStorageTool(config=config)
        self.databricks_tool = DatabricksTool(config=config)

        self.tools = {
            "list_blob_files": self.azure_blob_tool.list_blob_files,
            "download_blob": self.azure_blob_tool.download_blob,
            "upload_blob": self.azure_blob_tool.upload_blob,
            "delete_blob": self.azure_blob_tool.delete_blob,
            "list_local_files": self.local_files_tool.list_local_files,
            "delete_local_file": self.local_files_tool.delete_local_file,
            "run_databricks_job": self.databricks_tool.run_databricks_job,
            }

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
            {
                "type": "function",
                "function": {
                    "name": "delete_blob",
                    "description":
                        "Delete a blob file from Azure Blob Storage. If no container is specified, the default " \
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
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_local_file",
                    "description":
                        "Delete a local file given its full path.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "The full file path of the local file to delete"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            # Databricks tools
            {
                "type": "function",
                "function": {
                    "name": "run_databricks_job",
                    "description":
                        "Trigger a job inside databricks",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "notebook_path": {
                                "type": "string",
                                "description":
                                    "(Optional) The path of the notebook to trigger. If no path is " \
                                    " specified, the default container will be used."
                            }
                        },
                        #"required": ["notebook_path"]
                    }
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
