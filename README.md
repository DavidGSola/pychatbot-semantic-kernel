# 🐍 PyChatbot for Semantic Kernel

**PyChatbot for Semantic Kernel** is a sample chatbot integrated with [Semantic Kernel plugins](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/?pivots=programming-language-python). You can easily build your own plugins on top of the chatbot, so you can quickly validate your use case. It also allows you to check in real time how the agent [plans](https://learn.microsoft.com/en-us/semantic-kernel/concepts/planning?pivots=programming-language-python) and executes the tasks based on the available plugins.

This chatbot uses the new experimental [Agent Framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/?pivots=programming-language-python) which is still in development and is subject to change.

<p align="center">
  <img width="600" src="./images/chat.gif">
</p>

## Features

- **Chat interface:** A simple, easy-to-use chat interface for interacting with the chatbot.

- **Speech recognition:** Talk to the agent by using Semantic Kernel audio to text services.

- **Kernel inspector:** See in real time how the Semantic Kernel interacts with your plugins.

<p align="center">
  <img height="200" src="./images/inspector.png">
</p>

## Getting Started

### Prerequisites

- Python Version 3.10 or later
- Pip Version 22 or later

## Installation

1. Clone the repository:

```bash
git clone https://github.com/DavidGSola/pychatbot-semantic-kernel.git
cd pychatbot-semantic-kernel
```

2. Create new virtual environment:

```bash
py -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
py -m pip install -r requirements.txt
```

## Usage

**PyChatbot for Semantic Kernel** comes with a set of basic plugins to showcase it. It is easy to customize for your own use case by defining the instructions for the [Agent](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/chat-completion-agent?pivots=programming-language-python) and new [Plugins](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/?pivots=programming-language-python).

### Configure Semantic Kernel: 

Rename `.env.sample` file to `.env` and add your Azure OpenAI or OpenAI connection details.

### Set the instructions:

Customize your chatbot by editing the instructions for the [Agent](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/chat-completion-agent?pivots=programming-language-python) in the `coffee_assistant.py` file.

```python
self.agent = ChatCompletionAgent(
    service_id='chat_completion',
    kernel=self.kernel,
    name='Assistant',
    instructions="""
        Set here the meta prompt.
    """,
    execution_settings=settings
)
```

### Create your Plugins:

Create new [Plugins](https://learn.microsoft.com/en-us/semantic-kernel/concepts/plugins/?pivots=programming-language-python) for your use case within the `plugins` folder.

Edit the `__init__` method within the `CoffeeAsistant` class to register the new plugins.

```py
# Native plugin
self.kernel.add_plugin(PluginClass(), plugin_name="plugin_name")
# Prompt plugin
self.kernel.add_plugin(parent_directory="./plugins", plugin_name="plugin_name")
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.