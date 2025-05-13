class AIToolsAbstract:
    def __init__(self):

        self._tools = {}
        self._tools_description = []

    def get_tools(self):
        """
        Returns the tools available in the AI tools manager.
        """
        return self._tools

    def get_tools_description(self):
        """
        Returns the description of the AI tools.
        """
        return self._tools_description
