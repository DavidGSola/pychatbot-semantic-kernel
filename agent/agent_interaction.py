
class AgentInteraction:
    role: str

class ToolInteraction(AgentInteraction):
    plugin_name: str
    function_name: str
    
    def __init__(self, role, plugin_name, function_name):
        self.role = role
        self.plugin_name = plugin_name
        self.function_name = function_name

    def bg_color(self) -> str:
        return '#bf5050'
    
    def text_color(self) -> str:
        return '#ffffff'
            
    def title(self) -> str:
        return 'ASSISTANT - TOOL'
    
    def content(self) -> str:
        return f'{self.plugin_name} - {self.function_name}'

class TextInteraction(AgentInteraction):
    text: str

    def __init__(self, role, text):
        self.role = role
        self.text = text

    def bg_color(self) -> str:
        match str(self.role):
            case 'AuthorRole.SYSTEM':
                return '#902b2d'
            case 'AuthorRole.ASSISTANT':
                return '#d99a9a'
            case 'AuthorRole.USER':
                return '#A0D6B4'
            case _:
                return '#ffffff'

    def text_color(self) -> str:
        match str(self.role):
            case 'AuthorRole.SYSTEM':
                return '#ffffff'
            case _:
                return '#000000'

    def title(self) -> str:
        parts = self.role.split('.')

        if len(parts) > 1:
            return parts[-1].upper()
        else:
            return self.role.upper()
    
    def content(self) -> str:
        return self.text