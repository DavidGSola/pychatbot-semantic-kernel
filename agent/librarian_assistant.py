import os
from typing import Type

from agent.agent_roles import ROLES
from agent.agent_invokation import AgentInvokation, FunctionInvokation, TextInvokation, InvokationUsage

from plugins.book_repository_plugin import BookRepositoryPlugin

from semantic_kernel import Kernel

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.contents import AudioContent, ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.text_content import TextContent
from semantic_kernel.contents.function_call_content import FunctionCallContent
from semantic_kernel.contents.function_result_content import FunctionResultContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.audio_to_text_client_base import AudioToTextClientBase
from semantic_kernel.connectors.ai.text_to_audio_client_base import TextToAudioClientBase
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings


from semantic_kernel.connectors.ai.open_ai import (
    AzureChatCompletion, 
    OpenAIChatCompletion,
    AzureAudioToText, 
    OpenAIAudioToText,
    AzureTextToAudio, 
    OpenAITextToAudio,
    OpenAITextToAudioExecutionSettings,
)

from semantic_kernel.connectors.ai.ollama import (
    OllamaChatCompletion
)

class LibrarianAssistant:

    def __init__(self):
        llm_service = os.environ['GLOBAL_LLM_SERVICE']

        self.kernel = Kernel()
        settings = self.__init_services()

        self.kernel.add_plugin(BookRepositoryPlugin(), plugin_name="BookRepositoryPlugin")
        self.kernel.add_plugin(parent_directory="./plugins", plugin_name="poem_plugin")
        
        self.agent = ChatCompletionAgent(
            service_id='chat_completion',
            kernel=self.kernel,
            name='LibrarianAssistant',
            instructions="""
                You are a knowledgeable book assistant who helps readers explore and understand literature. You provide thoughtful analysis of themes, characters, and writing styles while avoiding spoilers unless explicitly requested.

                Your responses are concise but insightful, and you're careful to ask clarifying questions when needed to better understand readers' preferences and needs. When uncertain about details, you openly acknowledge limitations and present literary interpretations as possibilities rather than absolutes.
            """,
            execution_settings=settings
        )
        
        self.history = ChatHistory()

    def __init_services(self):
        llm_service = os.environ['GLOBAL_LLM_SERVICE']
        services = {  
            'AzureOpenAI': [  
                ('chat_completion', AzureChatCompletion),  
                ('audio_to_text_service', AzureAudioToText),  
                ('text_to_audio_service', AzureTextToAudio)  
            ],  
            'OpenAI': [  
                ('chat_completion', OpenAIChatCompletion),  
                ('audio_to_text_service', OpenAIAudioToText),  
                ('text_to_audio_service', OpenAITextToAudio)  
            ],  
            'Ollama': [  
                ('chat_completion', OllamaChatCompletion)  
            ]  
        }

        for service_id, service_class in services.get(llm_service, []):  
            self.kernel.add_service(service_class(service_id=service_id))  

        self.chat_service: ChatCompletionClientBase = self.kernel.get_service(service_id='chat_completion')
        
        if llm_service in ['AzureOpenAI', 'OpenAI']:
            self.audio_to_text_service: AudioToTextClientBase = self.kernel.get_service(service_id='audio_to_text_service')
            self.text_to_audio_service: TextToAudioClientBase = self.kernel.get_service(service_id='text_to_audio_service')

        return self.__init_settings()

    def __init_settings(self) -> PromptExecutionSettings:
        support_tool = os.environ.get('OLLAMA_SUPPORT_TOOL', "False") == "True"
        settings = self.kernel.get_prompt_execution_settings_from_service_id(service_id='chat_completion')  
        settings.function_choice_behavior = (  
            FunctionChoiceBehavior.Auto() if support_tool else FunctionChoiceBehavior.NoneInvoke()
        )

        return settings

    async def call(self, user_message: str) -> str:
        self.history.add_message(ChatMessageContent(role=AuthorRole.USER, content=user_message))
        async for response in self.agent.invoke(self.history):
            self.history.add_message(response)
            return str(response)
    
    async def transcript_audio(self, audio_file: str) -> (str):
        if not hasattr(self, 'audio_to_text_service'):
            print('Current LLM provider does not support AudioToText services')
            return ''
        
        user_message = await self.audio_to_text_service.get_text_content(AudioContent.from_audio_file(audio_file))
        return user_message.text
    
    async def generate_audio(self, message: str) -> bytes:
        if not hasattr(self, 'text_to_audio_service'):
            print('Current LLM provider does not support TextToAudio services')
            return None
        
        audio_content = await self.text_to_audio_service.get_audio_content(message, OpenAITextToAudioExecutionSettings(response_format="wav"))
        return audio_content.data

    def agent_invokations(self) -> list[AgentInvokation]:
        invokations = [
            TextInvokation(role=ROLES.SYSTEM, text=self.agent.instructions, usage=None)
        ]

        for message in self.history.messages:
            role = message.role
            usage = self.__get_usage(message)
            
            for item in message.items:
                if isinstance(item, TextContent):
                    invokations.append(TextInvokation(role, item.text, usage))
                elif isinstance(item, FunctionCallContent):
                    invokations.append(FunctionInvokation(role, item.plugin_name, item.function_name, item.arguments, usage))
                elif isinstance(item, FunctionResultContent) and isinstance(invokations[-1], FunctionInvokation):
                    invokations[-1].add_result(item.result)

        return invokations

    def __get_usage(self, message: ChatMessageContent) -> InvokationUsage:
        if 'usage' in message.metadata:
            return InvokationUsage(message.metadata['usage'].prompt_tokens, message.metadata['usage'].completion_tokens)
        else:
            return None
            
    def reset(self) -> None:
        self.history.messages.clear()
