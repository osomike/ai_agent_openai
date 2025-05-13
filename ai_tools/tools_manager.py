from utils.logger import Logger

from ai_tools.tools.tools_abstract import AIToolsAbstract
from ai_tools.tools.azure_blob_storage import AzureBlobStorageTool
from ai_tools.tools.local import LocalStorageTool
from ai_tools.tools.databricks import DatabricksTool
from ai_tools.tools.xpa_survey import XPASurveyTool

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
        self.xpa_survey_tool = XPASurveyTool(config=config)

        self.ai_tools = [
            self.azure_blob_tool,
            self.local_files_tool,
            self.databricks_tool,
            self.xpa_survey_tool
        ]

        # Initialize the tools dictionary and description
        # by aggregating the tools from all AI tools instances
        self.tools = {}
        self.tools_description = []

        for ai_tool in self.ai_tools:
            if not isinstance(ai_tool, AIToolsAbstract):
                raise TypeError(f"Tool {ai_tool} is not an instance of AIToolsAbstract")
            self.tools.update(ai_tool.get_tools())
            self.tools_description.extend(ai_tool.get_tools_description())

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
