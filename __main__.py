import user.users as users
import markdown2
from datetime import datetime

from dotenv import load_dotenv
from typing import List, Tuple
from agent.agent import Agent
from nicegui import ui

agent:Agent = Agent()
messages: List[Tuple[users.User, str, str]] = []

bg_color = '#1B4242'
secondary_color = '#5C8374'
accent_color = '#9EC8B9'

def init_styles():
    ui.colors(primary=bg_color, secondary=secondary_color, accent=accent_color)
    
    ui.page_title('Simple SK Chatbot')
    
    ui.query('.nicegui-content').classes('p-8')
    ui.query('body').style('background-color: #040D12')
    ui.query('#app').style(f'background-color: {bg_color}').classes('max-w-4xl mx-auto')
    
    ui.add_css(r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}')

async def call_agent(input, chat_spinner, plan_spinner):
    text = input.value
    input.value = ""
    
    chat_spinner.visible = plan_spinner.visible = True
    
    add_message('user', text)
    result = await agent.call_agent(text)
    add_message('assistant', result)
    
    chat_spinner.visible = plan_spinner.visible = False

    chat_plan.refresh()

def add_message(user_id: str, text: str) -> None:
    stamp = datetime.now().strftime('%X')
    user = users.find(user_id)
    messages.append((user, text, stamp))
    chat_messages.refresh()
    
def reset_conversation() -> None:
    messages.clear()
    agent.reset()
    
    chat_messages.refresh()
    chat_plan.refresh()

    ui.notify('Conversation cleared')

def show_about() -> None:
    libraries = []
    with open('requirements.txt', 'r', encoding='utf-16') as requirements:
        for line in requirements.readlines():
            if '==' in line:
                lib, version = line.strip().split('==')
                libraries.append(f"{lib}: {version}")

    with ui.dialog() as about_dialog, ui.card():
        ui.label('🐍 PyChatbot for Semantic Kernel').classes('text-semibold text-xl')
        ui.label('\n'.join(libraries)).style('white-space: pre-wrap')

        ui.button('Close', on_click=about_dialog.close)

    about_dialog.open()

@ui.refreshable
def chat_messages(user_id: str) -> None:
    if messages:
        for user, text, stamp in messages:
            bg_color = 'accent' if user.id == user_id else 'secondary'
            ui.chat_message(text=markdown2.markdown(text), stamp=stamp, avatar=user.avatar, sent=user.id == user_id, text_html=True).props(f'bg-color={bg_color}')
    else:
        ui.label('Start messaging with your bot').classes('mx-auto my-36 text-lg text-emerald-300')
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
    
@ui.refreshable
def chat_plan() -> None:
    with ui.column():
        for call in agent.agent_history():
            with ui.card().style(f'background-color: {call.color()}'):
                ui.label(call.title()).classes('font-bold text-gray-800')
                ui.label(call.content()).classes('text-gray-900')
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')

@ui.page('/')
async def main():
    init_styles()
    
    with ui.page_sticky(x_offset=18, y_offset=18).props('position=top-right'):
        with ui.element('q-fab').props(f'icon=settings color=secondary direction=down').classes('self-end'):
            ui.element('q-fab-action').props('icon=restore color=secondary') \
                .on('click', lambda: reset_conversation()).tooltip('Clear conversation')
            ui.element('q-fab-action').props('icon=help color=secondary') \
                .on('click', lambda: show_about()).tooltip('About')

    with ui.tabs().classes('w-full text-emerald-300') as tabs:
        chat = ui.tab('Chat')
        plan = ui.tab('Kernel plan')
    with ui.tab_panels(tabs, value=chat).classes('w-full'):
        with ui.tab_panel(chat).style(f'background-color: {bg_color}'):
            with ui.column().classes('w-full max-w-2x1 mx-auto items-stretch'):
                chat_messages("user")
                chat_spinner = ui.spinner('dots', size='lg', color=accent_color).classes('self-center')
                chat_spinner.visible = False
        with ui.tab_panel(plan).style(f'background-color: {bg_color}'):
            with ui.column().classes('w-full max-w-2x1 mx-auto items-stretch'):
                chat_plan()
                plan_spinner = ui.spinner('dots', size='lg', color=accent_color).classes('self-center')
                plan_spinner.visible = False
        
    with ui.footer().classes('w-full max-w-4xl mx-auto py-6'), ui.column().classes('w-full'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar():
                ui.image('https://api.dicebear.com/9.x/avataaars-neutral/svg?seed=user')
            input = ui.input(placeholder='Type something ...').on('keydown.enter', lambda: call_agent(input, chat_spinner, plan_spinner)).props('rounded outlined input-class=mx-3 bg-color=accent').classes('flex-grow')

    await ui.context.client.connected()
    
if __name__ in {"__main__", "__mp_main__"}:
    load_dotenv()

    users.add('user')
    users.add('assistant')

    agent.define_agent(
    """
        You are a shopping assistant embedded in a chat. You can help the user with receipts and cooking related stuff.
    """)

    ui.run(favicon='🐍')