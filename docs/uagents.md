uAgents: AI Agent Framework
Official Website GitHub Repo stars Twitter Follow Ruff Tests PyPI - Python Version

uAgents is a library developed by Fetch.ai that allows for creating autonomous AI agents in Python. With simple and expressive decorators, you can have an agent that performs various tasks on a schedule or takes action on various events.

🚀 Features
🤖 Easy creation and management: Create any type of agent you can think of and implement it in code.
🔗 Connected: On startup, each agent automatically joins the fast-growing network of uAgents by registering on the Almanac, a smart contract deployed on the Fetch.ai blockchain.
🔒 Secure: uAgent messages and wallets are cryptographically secured, so their identities and assets are protected.
⚡ Quickstart
Installation
Get started with uAgents by installing it for Python 3.10 to 3.13:

pip install uagents
Running a Demo
Creating an Agent
Build your first uAgent using the following script:

from uagents import Agent, Context
alice = Agent(name="alice", seed="alice recovery phrase")
Include a seed parameter when creating an agent to set fixed addresses, or leave it out to generate a new random address each time.

Giving it a task
Give it a simple task, such as a greeting:

@alice.on_interval(period=2.0)
async def say_hello(ctx: Context):
    ctx.logger.info(f'hello, my name is {ctx.agent.name}')

if __name__ == "__main__":
    alice.run()
Running the Agent
So far, your code should look like this:

from uagents import Agent, Context

alice = Agent(name="alice", seed="alice recovery phrase")

@alice.on_interval(period=2.0)
async def say_hello(ctx: Context):
    ctx.logger.info(f'hello, my name is {ctx.agent.name}')

if __name__ == "__main__":
    alice.run()
Run it using:

python agent.py
You should see the results in your terminal.

📖 Documentation
Please see the official documentation for full setup instructions and advanced features.

👋 Introduction
💻 Installation
Tutorials
🤖 Create an agent
🛣️ Agent Communication
🍽️ Restaurant Booking Demo
Key Concepts:
📍Addresses
💾 Storage
📝 Interval Tasks
🌐 Agent Broadcast
⚙️ Almanac Contracts
🌱 Examples and Integrations
The uAgent-Examples repository contains several examples of how to create and run various types of agents as well as more intricate integrations. This is the official place for internal and community open source applications built on uAgents.

Python Library
Go to the python folder for details on the Python uAgents library.

uAgents Core
The uagents-core folder contains core definitions and functionalities to build 'agent' like software which can interact and integrate with Fetch.ai ecosystem and agent marketplace.

✨ Contributing
All contributions are welcome! Remember, contribution includes not only code, but any help with docs or issues raised by other developers. See our contribution guidelines for more details.

📄 Development Guidelines
Read our development guidelines to learn some useful tips related to development.

❓ Issues, Questions, and Discussions
We use GitHub Issues for tracking requests and bugs, and GitHub Discussions for general questions and discussion.

🛡 Disclaimer
This project, uAgents, is provided "as-is" without any warranty, express or implied. By using this software, you agree to assume all risks associated with its use, including but not limited to unexpected behavior, data loss, or any other issues that may arise. The developers and contributors of this project do not accept any responsibility or liability for any losses, damages, or other consequences that may occur as a result of using this software.

