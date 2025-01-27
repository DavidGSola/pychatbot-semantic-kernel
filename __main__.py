import os
import markdown2

import user.users as users

from helpers import get_libraries, swap_visibility
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Tuple
from agent.librarian_assistant import LibrarianAssistant
from audio.audio_player import AudioPlayer
from audio.audio_recorder import AudioRecorder
from nicegui import ui

assistant:LibrarianAssistant = LibrarianAssistant()
recorder:AudioRecorder = AudioRecorder()
messages: List[Tuple[users.User, str, str]] = []
spinners = []
config = {
    'audio': False
}

bg_color = '#1B4242'
secondary_color = '#d99a9a'
accent_color = '#A0D6B4'

def init_styles():
    ui.colors(primary=bg_color, secondary=secondary_color, accent=accent_color)
    
    ui.page_title('Simple SK Chatbot')
    
    ui.query('.nicegui-content').classes('p-8')
    ui.query('body').style('background-color: #040D12')
    ui.query('#app').style(f'background-color: {bg_color}').classes('max-w-4xl mx-auto')
    
    with open('styles.css', 'r', encoding='utf-8') as styles:
        ui.add_css(styles.read())

async def call_assistant_from_input(input):
    text = input.value
    input.value = ""

    await call_assistant(text)

async def call_assistant(text: str):    
    swap_visibility(spinners)    
    
    add_message('user', text)
    response = await assistant.call(text)
    add_message('assistant', response)
    
    if config['audio']:
        await reproduce_as_audio(response)
    
    swap_visibility(spinners)

    chat_inspector.refresh()

def add_message(user_id: str, text: str) -> None:
    stamp = datetime.now().strftime('%X')
    user = users.find(user_id)
    messages.append((user, text, stamp))
    chat_messages.refresh()
    
def reset_conversation() -> None:
    messages.clear()
    assistant.reset()
    
    chat_messages.refresh()
    chat_inspector.refresh()

    ui.notify('Conversation cleared')

def show_about() -> None:
    llm_service = os.environ['GLOBAL_LLM_SERVICE']

    with ui.dialog() as about_dialog, ui.card():
        ui.label('🐍 PyChatbot for Semantic Kernel').classes('text-semibold text-xl')
        ui.label('\n'.join(get_libraries())).style('white-space: pre-wrap')
        ui.label(f'\nPowered by {llm_service}')

        ui.button('Close', on_click=about_dialog.close)

    about_dialog.open()

def move_to_last_message():
    ui.run_javascript('''
        const allMatchedElements = document.getElementsByClassName('tab-content');
        const moduleContent = allMatchedElements[0] //first matched element
        moduleContent.scrollTop = moduleContent.scrollHeight;
    ''')

@ui.refreshable
def chat_messages(user_id: str) -> None:
    if messages:
        for user, text, stamp in messages:
            bg_color = 'accent' if user.id == user_id else 'secondary'
            ui.chat_message(text=markdown2.markdown(text), stamp=stamp, avatar=user.avatar, sent=user.id == user_id, text_html=True).props(f'bg-color={bg_color}')
    else:
        ui.label('Start messaging with your bot').classes('mx-auto my-36 text-lg text-emerald-300')
    
    move_to_last_message()
    
@ui.refreshable
def chat_inspector() -> None:
    with ui.column():
        [invokation.render() for invokation in assistant.agent_invokations()]

    move_to_last_message()

def tabs():
    with ui.tabs().classes('w-full text-emerald-300') as tabs:
        chat = ui.tab('Chat')
        inspector = ui.tab('Inspector')
    with ui.tab_panels(tabs, value=chat).classes('w-full'):
        with ui.tab_panel(chat).classes('tab-content').style(f'background-color: {bg_color}'):
            with ui.column().classes('w-full max-w-2x1 mx-auto items-stretch'):
                chat_messages("user")
                spinner()
        with ui.tab_panel(inspector).classes('tab-content').style(f'background-color: {bg_color}'):
            with ui.column().classes('w-full max-w-2x1 mx-auto items-stretch'):
                chat_inspector()
                spinner()

def start_recording(button: ui.button):
    button.text = "Recording"
    recorder.start_recording()

async def stop_recording(button: ui.button):
    button.text = ""
    recorder.stop_recording()
    transcription = await assistant.transcript_audio(recorder.output_filepath)

    if transcription == '':
        show_toast('Current LLM provider does not support AudioToText services')
    else:        
        await call_assistant(transcription)
        
    recorder.remove_output_file()

async def reproduce_as_audio(text: str):
    player = AudioPlayer()
    audio = await assistant.generate_audio(text)

    if audio == None:
        show_toast('Current LLM provider does not support TextToAudio services')
    else:
        player.play_wav_from_bytes(audio)

def show_toast(text: str):
    ui.notify(text, close_button='OK')

def footer():
    with ui.footer().classes('w-full max-w-4xl mx-auto py-6'), ui.column().classes('w-full'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar():
                ui.image('https://api.dicebear.com/9.x/avataaars-neutral/svg?seed=user')
            input = ui.input(placeholder='Type something ...').on('keydown.enter', lambda: call_assistant_from_input(input)).props('rounded outlined input-class=mx-3 bg-color=accent').classes('flex-grow')
            button = ui.button().props('icon=mic color=accent text-color=primary').classes('rounded-full')
            button.on('mousedown', lambda: start_recording(button))
            button.on('mouseup', lambda: stop_recording(button))

def spinner():
    chat_spinner = ui.spinner('dots', size='lg', color=accent_color).classes('self-center')
    chat_spinner.visible = False
    spinners.append(chat_spinner)

def switch_audio():
    config['audio'] = not config['audio']
    settings.refresh()

@ui.refreshable
def settings() -> None:
    audio_enabled = config['audio']
    audio_icon = 'volume_up' if audio_enabled else 'volume_off'
    audio_text = 'On' if audio_enabled else 'Off'

    with ui.page_sticky(x_offset=18, y_offset=18).props('position=top-right'):
        with ui.row().classes('flex flex-col gap-1'):
            ui.button(audio_text).props(f'icon={audio_icon} color=secondary').classes('w-32') \
                .on('click', lambda: switch_audio()).tooltip(audio_text)
            ui.button('Reset').props('icon=restore color=secondary').classes('w-32')  \
                .on('click', lambda: reset_conversation()).tooltip('Clear conversation')
            ui.button('About').props('icon=help color=secondary').classes('w-32')  \
                .on('click', lambda: show_about())
                
@ui.page('/')
async def main():
    init_styles()
    
    tabs()
    footer()
    settings()

    await ui.context.client.connected()
    
if __name__ in {"__main__", "__mp_main__"}:
    load_dotenv(override=True)

    users.add('user')
    users.add('assistant')

    ui.run(favicon='🐍')