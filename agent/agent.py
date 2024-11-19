from plugins.supermarket import SupermarketPlugin
from agent.agent_record import AgentRecord, AgentToolRecord, AgentTextRecord, UsageRecord

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureAudioToText
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings
)
from semantic_kernel.contents import AudioContent, ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.text_content import TextContent
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent

class Agent:
    def __init__(self):
        self.kernel = Kernel()
        self.kernel.add_service(AzureChatCompletion(
            service_id="default"
        ))
        
        self.kernel.add_service(AzureAudioToText(
            service_id="audio_service"
        ))
        
        self.chat_service:AzureChatCompletion = self.kernel.get_service(type=ChatCompletionClientBase)
        self.audio_to_text_service:AzureAudioToText = self.kernel.get_service(type=AzureAudioToText)

        self.kernel.add_plugin(SupermarketPlugin(), plugin_name="SupermarketPlugin")
        self.kernel.add_plugin(parent_directory="./plugins", plugin_name="shop_plugin")

        self.execute_settings = AzureChatPromptExecutionSettings(tool_choice='auto')
        self.execute_settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={})
        
        self.history = ChatHistory()
        
    def define_agent(self, system_message: str):
        self.history.add_system_message(system_message)
        
    async def call_agent(self, user_message: str) -> (str):
        self.history.add_user_message(user_message)
        
        result = (await self.chat_service.get_chat_message_contents(
            chat_history=self.history,
            settings=self.execute_settings,
            kernel=self.kernel,
            arugments=KernelArguments()
        ))[0]
        
        self.history.add_message(result)
        
        return str(result)
    
    async def transcript_audio(self, audio_file: str) -> (str):
        user_message = await self.audio_to_text_service.get_text_content(AudioContent.from_audio_file(audio_file))
        return user_message.text
    
    def records(self) -> list[AgentRecord]:
        records = []

        for message in self.history.messages:
            role = message.role
            usage = self.__get_usage(message)
            
            for item in message.items:
                if isinstance(item, TextContent):
                    records.append(AgentTextRecord(role, item.text, usage))
                elif isinstance(item, FunctionCallContent):
                    records.append(AgentToolRecord(role, item.plugin_name, item.function_name, item.arguments, usage))
                elif isinstance(item, FunctionResultContent) and isinstance(records[-1], AgentToolRecord):
                    records[-1].add_result(item.result)

        return records

    def __get_usage(self, message: ChatMessageContent) -> UsageRecord:
        if 'usage' in message.metadata:
            return UsageRecord(message.metadata['usage'].prompt_tokens, message.metadata['usage'].completion_tokens)
        else:
            return None
            
    def reset(self) -> None:
        del self.history.messages[1:]