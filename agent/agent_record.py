import json
from nicegui import ui
from abc import ABC, abstractmethod

from agent.agent_roles import ROLES

class UsageRecord:
    prompt_tokens: str
    completion_tokens: str
    
    def __init__(self, prompt, completion):
        self.prompt_tokens = prompt
        self.completion_tokens = completion

class AgentRecord(ABC):
    role: str
    usage: UsageRecord
    
    def render_usage(self):
        if self.usage is not None:
            with ui.card().style('background-color: white; padding: 4px'):
                ui.html(f'<strong>Prompt tokens:</strong> {self.usage.prompt_tokens} | <strong>Completion tokens:</strong> {self.usage.completion_tokens}') \
                    .style('font-size: 0.75rem; color: black; font-family: "Courier New", monospace;')
                
    @abstractmethod
    def render(self):
        pass

class AgentToolRecord(AgentRecord):
    plugin_name: str
    function_name: str
    function_result: str
    function_arguments: str
    
    def __init__(self, role: str, plugin_name: str, function_name: str, arguments: str, usage: UsageRecord):
        self.role = role
        self.plugin_name = plugin_name
        self.function_name = function_name
        self.function_arguments = arguments
        self.usage = usage

    def render(self):
        with ui.card().style('background-color: #bf5050'):
            ui.label('ASSISTANT - TOOL').classes('font-bold').style('color: white')
            
            with ui.card().style('background-color: white; padding: 4px'):
                ui.html(self.__content()) \
                    .style('font-size: 0.75rem; color: black; font-family: "Courier New", monospace; white-space: pre-wrap')
            
            self.render_usage()

    def add_result(self, result: str):
        self.function_result = result
    
    def __content(self) -> str:
        return f'<strong>{self.plugin_name}</strong>.{self.function_name}( \
                \n{self.__arguments()} \
                \n) \
                \n=> ({self.function_result})'

    def __arguments(self) -> str:
        data = json.loads(self.function_arguments)
        return '\n'.join([f'\t<i>{key}</i>: <strong>{value}</strong>' for key, value in data.items()])

class AgentTextRecord(AgentRecord):
    text: str

    def __init__(self, role: str, text: str, usage: UsageRecord):
        self.role = role
        self.text = text
        self.usage = usage
            
    def render(self):
        with ui.card().style(f'background-color: {self.__bg_color()}'):
            ui.label(self.__title()).classes('font-bold').style(f'color: {self.__text_color()}')
            ui.label(self.text).style(f'color: {self.__text_color()}')
            self.render_usage()

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