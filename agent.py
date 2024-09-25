from plugins.supermarket import SupermarketPlugin

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

class Agent:
    def __init__(self):
        self.kernel = Kernel()
        self.kernel.add_service(AzureChatCompletion(
            service_id="default"
        ))
        
        self.chat : AzureChatCompletion = self.kernel.get_service(type=ChatCompletionClientBase)
        
        self.kernel.add_plugin(SupermarketPlugin(), plugin_name="SupermarketPlugin")
        self.kernel.add_plugin(parent_directory="./plugins", plugin_name="shop_plugin")

        self.execute_settings = AzureChatPromptExecutionSettings(tool_choice='auto')
        self.execute_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={})
        
        self.history = ChatHistory()
        
    def define_agent(self, system_message: str):
        self.history.add_system_message(system_message)
        
    async def call_agent(self, user_message: str) -> str:
        self.history.add_user_message(user_message)
        
        result = (await self.chat.get_chat_message_contents(
            chat_history=self.history,
            settings=self.execute_settings,
            kernel=self.kernel,
            arugments=KernelArguments()
        ))[0]
        
        self.history.add_message(result)
        
        return str(result)