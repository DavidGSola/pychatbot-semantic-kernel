import users
import markdown2
from datetime import datetime

from dotenv import load_dotenv
from typing import List, Tuple
from agent import Agent
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

async def call_agent(input, spinner):
    text = input.value
    input.value = ""
    
    spinner.visible = True
    
    add_message('user', text)
    result = await agent.call_agent(text)
    add_message('agent', result)
    
    spinner.visible = False

def add_message(user_id: str, text: str) -> None:
    stamp = datetime.now().strftime('%X')
    user = users.find(user_id)
    messages.append((user, text, stamp))
    chat_messages.refresh()

@ui.refreshable
def chat_messages(user_id: str) -> None:
    if messages:
        for user, text, stamp in messages:
            bg_color = 'accent' if user.id == user_id else 'secondary'
            ui.chat_message(text=markdown2.markdown(text), stamp=stamp, avatar=user.avatar, sent=user.id == user_id, text_html=True).props(f'bg-color={bg_color}')
    else:
        ui.label('Start messaging with your bot').classes('mx-auto my-36 text-lg text-emerald-300')
    ui.run_javascript('window.scrollTo(0, document.body.scrollHeight)')
    
@ui.page('/')
async def main():
    init_styles()
    
    with ui.column().classes('w-full max-w-2x1 mx-auto items-stretch'):
        chat_messages("user")
        spinner = ui.spinner('dots', size='lg', color=accent_color).classes('self-center')
        spinner.visible = False
        
    with ui.footer().classes('w-full max-w-4xl mx-auto py-6'), ui.column().classes('w-full'):
        with ui.row().classes('w-full no-wrap items-center'):
            with ui.avatar():
                ui.image('https://api.dicebear.com/9.x/avataaars-neutral/svg?seed=user')
            input = ui.input(placeholder='Type something ...').on('keydown.enter', lambda: call_agent(input, spinner)).props('rounded outlined input-class=mx-3 bg-color=accent').classes('flex-grow')
    
    await ui.context.client.connected()
    
if __name__ in {"__main__", "__mp_main__"}:
    load_dotenv()

    users.add('user')
    users.add('agent')

    agent.define_agent(
    """
        Set here your system prompt
    """)

    ui.run(favicon='🐍')