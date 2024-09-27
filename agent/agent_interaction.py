
class AgentInteraction:
    role: str

class ToolInteraction(AgentInteraction):
    plugin_name: str
    function_name: str
    
    def __init__(self, role, plugin_name, function_name):
        self.role = role
        self.plugin_name = plugin_name
        self.function_name = function_name

    def title(self) -> str:
        return 'AuthorRole.ASSISTANT (Tool call)'
    
    def content(self) -> str:
        return f'{self.plugin_name} - {self.function_name}'

class TextInteraction(AgentInteraction):
    text: str

    def __init__(self, role, text):
        self.role = role
        self.text = text

    def title(self) -> str:
        return f'{self.role}:'
    
    def content(self) -> str:
        return self.text