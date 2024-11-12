
class AgentInteraction:
    role: str

class ToolInteraction(AgentInteraction):
    plugin_name: str
    function_name: str
    
    def __init__(self, role, plugin_name, function_name):
        self.role = role
        self.plugin_name = plugin_name
        self.function_name = function_name

    def color(self) -> str:
        return '#5AA9E6'
            
    def title(self) -> str:
        return 'ASSISTANT - TOOL'
    
    def content(self) -> str:
        return f'{self.plugin_name} - {self.function_name}'

class TextInteraction(AgentInteraction):
    text: str

    def __init__(self, role, text):
        self.role = role
        self.text = text

    def color(self) -> str:
        match str(self.role):
            case 'AuthorRole.SYSTEM':
                return '#4B8F8C'
            case 'AuthorRole.USER':
                return '#A0D6B4'
            case 'AuthorRole.ASSISTANT':
                return '#82B8E6'
            case _:
                return '#ffffff'

    def title(self) -> str:
        parts = self.role.split('.')

        if len(parts) > 1:
            return parts[-1].upper()
        else:
            return self.role.upper()
    
    def content(self) -> str:
        return self.text