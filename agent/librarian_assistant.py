from plugins.book_repository_plugin import BookRepositoryPlugin
from agent.agent_record import AgentRecord, AgentToolRecord, AgentTextRecord, UsageRecord

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureAudioToText
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings
)
from semantic_kernel.agents import ChatCompletionAgent

from semantic_kernel.contents import AudioContent, ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.text_content import TextContent
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.contents.utils.author_role import AuthorRole

class CoffeeAssistant:
    def __init__(self):
        self.kernel = Kernel()
        self.kernel.add_service(AzureChatCompletion(
            service_id='chat_completion'
        ))
        
        self.kernel.add_service(AzureAudioToText(
            service_id='audio_service'
        ))
        
        self.chat_service:AzureChatCompletion = self.kernel.get_service(type=AzureChatCompletion)
        self.audio_to_text_service:AzureAudioToText = self.kernel.get_service(type=AzureAudioToText)

        self.kernel.add_plugin(BookRepositoryPlugin(), plugin_name="BookRepositoryPlugin")
        self.kernel.add_plugin(parent_directory="./plugins", plugin_name="poem_plugin")

        settings = AzureChatPromptExecutionSettings(tool_choice='auto')
        settings.function_choice_behavior = FunctionChoiceBehavior.Auto(filters={})
        
        self.agent = ChatCompletionAgent(
            service_id='chat_completion',
            kernel=self.kernel,
            name='CoffeeAssistant',
            instructions="""
                You are a knowledgeable book assistant who helps readers explore and understand literature. You provide thoughtful analysis of themes, characters, and writing styles while avoiding spoilers unless explicitly requested.

                Your responses are concise but insightful, and you're careful to ask clarifying questions when needed to better understand readers' preferences and needs. When uncertain about details, you openly acknowledge limitations and present literary interpretations as possibilities rather than absolutes.
            """,
            execution_settings=settings
        )
        
        self.history = ChatHistory()
        
    async def call(self, user_message: str) -> str:
        self.history.add_message(ChatMessageContent(role=AuthorRole.USER, content=user_message))
        async for response in self.agent.invoke(self.history):
            self.history.add_message(response)
            return str(response)
    
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
            return UsageRecord(0, 0)
            
    def reset(self) -> None:
        self.history.messages.clear()
