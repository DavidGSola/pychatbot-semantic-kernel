import json
from nicegui import ui
from abc import ABC, abstractmethod

from agent.agent_roles import ROLES

class AgentRecord(ABC):
    role: str
    
    @abstractmethod
    def render(self):
        pass

class AgentToolRecord(AgentRecord):
    plugin_name: str
    function_name: str
    function_result: str
    function_arguments: str
    
    def __init__(self, role, plugin_name, function_name, arguments):
        self.role = role
        self.plugin_name = plugin_name
        self.function_name = function_name
        self.function_arguments = arguments

    def render(self):
        with ui.card().style('background-color: #bf5050'):
            ui.label('ASSISTANT - TOOL').classes('font-bold').style('color: white')
            ui.label(self.__content()).style('color: white; white-space: pre-wrap')

    def add_result(self, result: str):
        self.function_result = result
    
    def __content(self) -> str:
        return f'{self.plugin_name}.{self.function_name}( \
                \n{self.__arguments()} \
                \n) \
                \n=> ({self.function_result})'

    def __arguments(self) -> str:
        data = json.loads(self.function_arguments)
        return '\n'.join([f'\t{key}: {value}' for key, value in data.items()])

class AgentTextRecord(AgentRecord):
    text: str

    def __init__(self, role, text):
        self.role = role
        self.text = text
            
    def render(self):
        with ui.card().style(f'background-color: {self.__bg_color()}'):
            ui.label(self.__title()).classes('font-bold').style(f'color: {self.__text_color()}')
            ui.label(self.text).style(f'color: {self.__text_color()}')

    def __bg_color(self) -> str:
        match str(self.role):
            case ROLES.SYSTEM:
                return '#902b2d'
            case ROLES.ASSISTANT:
                return '#d99a9a'
            case ROLES.USER:
                return '#A0D6B4'
            case _:
                return 'white'

    def __text_color(self) -> str:
        match str(self.role):
            case ROLES.SYSTEM:
                return 'white'
            case _:
                return 'black'

    def __title(self) -> str:
        parts = self.role.split('.')

        if len(parts) > 1:
            return parts[-1].upper()
        else:
            return self.role.upper()