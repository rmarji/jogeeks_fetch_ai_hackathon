Introduction
Welcome to the Agentverse platform! This guide will help you get started with creating and deploying autonomous agents using the uAgents framework. Agentverse provides a powerful ecosystem for building, deploying, and managing autonomous agents that can communicate with each other and interact with external services.
What are uAgents?
uAgents (micro-agents) are lightweight, autonomous software entities that can:

Run independently and make decisions
Communicate with other agents using secure messaging
Execute tasks on a schedule
Interact with external APIs and services
Store and retrieve data
Integrate with AI models for enhanced capabilities
Choosing Your Development Path
Agentverse offers multiple paths for agent development, each suited to different needs and use cases. This guide covers four main approaches:

Path
Description
Best For
A: Hosted uAgent
Agents run on the Agentverse platform
Quick start, minimal setup, continuous availability
B: Local uAgent
Agents run on your local machine
Custom environments, local integrations, full control
C: Mailbox uAgent
Local agents with mailbox for async communication
Intermittent operation, offline message handling


Choose the path that best fits your project requirements and development preferences. You can always migrate between paths as your needs evolve.
Path A: Hosted uAgent Creation
For developers wanting the fastest, simplest route to agent creation with minimal setup. Hosted uAgents run on the Agentverse platform, eliminating the need for local infrastructure setup.
When to Choose This Path
You want to get started quickly without setting up a local environment
You need your agent to be continuously available without running your own server
You want to leverage the Agentverse platform's built-in monitoring and management tools
Step-by-Step Guide
Account Creation & Login

Create an account on the Agentverse platform
Log in to your dashboard

Agent Creation

Navigate to Agents tab → + New Agent
Select "Blank Agent" template
Name the agent (e.g., "MyFirstAgent")

Code Implementation

Open the embedded code editor
Implement basic agent code:

from uagents import Agent, Context, Model

# Create agent instance
agent = Agent(
    name="my_first_agent",
    seed="seed_phrase_for_agent" # Used to generate agent addresses
)

# Define startup behavior
@agent.on_event("startup")
async def startup_function(ctx: Context):
    ctx.logger.info(f"Hello, I'm {agent.name} and my address is {agent.address}.")

# Add message handling capabilities
class Message(Model):
    content: str

@agent.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.content}")
    # Respond to the message
    await ctx.send(sender, Message(content=f"Echo: {msg.content}"))

Deployment & Testing
Click "Start" to deploy the agent
View logs in the terminal below
Create a test agent that sends a message to your initial agent to test functionality
Key Features
Interval Tasks: Schedule recurring tasks using the @agent.on_interval decorator:

@agent.on_interval(period=2.0)  # Run every 2 seconds
async def periodic_task(ctx: Context):
    ctx.logger.info("Performing scheduled task...")

Event Handlers: React to agent lifecycle events:

@agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info("Agent is starting up!")

@agent.on_event("shutdown") 
async def on_shutdown(ctx: Context):
    ctx.logger.info("Agent is shutting down!")

Message Models: Define structured data models for communication:

class Telemetry(Model):
    temperature: float
    vibration: float
    
@agent.on_message(model=Telemetry)
async def handle_telemetry(ctx: Context, sender: str, msg: Telemetry):
    ctx.logger.info(f"Received telemetry: Temp={msg.temperature}°C, Vibration={msg.vibration}")
Path B: Local uAgent Creation
For developers preferring local development and greater customization. Local uAgents run on your own machine or server, giving you full control over the environment and execution.
When to Choose This Path
You need more control over your agent's environment
You want to integrate with local services or hardware
You prefer working in your own development environment
You need to use custom libraries or dependencies
Step-by-Step Guide
Environment Setup

Install Python 3.8+ if not already installed
Create a virtual environment:

python -m venv venv

Activate the environment:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate
Install uAgents:

pip install uagents

Project Initialization

Create a project directory:

mkdir my_agent_project && cd my_agent_project

Create a Python file:

touch my_agent.py  # On Unix/Mac
# OR
echo. > my_agent.py  # On Windows

Agent Implementation

Open my_agent.py in your preferred editor
Implement agent code with local configuration:

from uagents import Agent, Context

# Create agent instance with local configuration
agent = Agent(
    name="my_first_agent",
    port=8000,
    endpoint=["http://localhost:8000/submit"],
    publish_agent_details=True,  # Puts your agent on agentverse
    seed="seed_phrase_for_agent"  # Used to generate agent address
)

@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")

if __name__ == "__main__":
    agent.run()

Running & Testing
Run the agent:

python my_agent.py

Note the generated agent address in the logs
Test using a second agent or the Agentverse inspector URL provided in logs
Multi-Agent Communication Example
Create multiple agents that communicate with each other:

Agent 1 (machinery.py):

import random
from uagents import Agent, Context, Model

# Define telemetry model
class Telemetry(Model):
    temperature: float
    vibration: float

# Define response model
class RepairResponse(Model):
    status: str

agent = Agent(
    name="machinery",
    seed="machinery_seed_phrase",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

# Send telemetry data every 20 seconds
@agent.on_interval(period=20.0)
async def send_telemetry(ctx: Context):
    telemetry = Telemetry(
        temperature=random.uniform(20, 100),
        vibration=random.uniform(0, 10)
    )
    # Send to monitor agent (replace with actual address)
    await ctx.send('agent1qvk2ppctpjjj7ev6afdze3raup304pz7sc77sf6fk7h7n4uuexktx3t0der', telemetry)
    ctx.logger.info(f"Sent Telemetry: {telemetry}")

@agent.on_message(model=RepairResponse)
async def handle_repair(ctx: Context, sender: str, msg: RepairResponse):
    ctx.logger.info(f"Received repair info from {sender}: {msg.status}")

if __name__ == "__main__":
    agent.run()

Agent 2 (monitor.py):

from uagents import Agent, Context, Model

# Define telemetry model
class Telemetry(Model):
    temperature: float
    vibration: float

# Define repair request model
class RepairRequest(Model):
    issue: str
    value: float

agent = Agent(
    name="monitor",
    seed="monitor_seed_phrase",
    port=8001,
    endpoint=["http://localhost:8001/submit"]
)

@agent.on_message(model=Telemetry)
async def analyze_telemetry(ctx: Context, sender: str, msg: Telemetry):
    ctx.logger.info(f"Received telemetry from {sender}: {msg}")
    if msg.temperature > 80:
        request = RepairRequest(issue="High Temperature", value=msg.temperature)
        # Send to repairer agent (replace with actual address)
        await ctx.send('agent1qt5k53m7p3qt6kshx46g8jgg4drr8dczrgvkt5xuyl303scclmxuv4556sw', request)
        await ctx.send(sender, request)  # Notify sender
        ctx.logger.info(f"High Temp! Sent repair request: {request}")
    elif msg.vibration > 7:
        request = RepairRequest(issue="High Vibration", value=msg.vibration)
        await ctx.send('agent1qt5k53m7p3qt6kshx46g8jgg4drr8dczrgvkt5xuyl303scclmxuv4556sw', request)
        await ctx.send(sender, request)  # Notify sender
        ctx.logger.info(f"High Vibration! Sent repair request: {request}")
    else:
        ctx.logger.info("Telemetry Normal")

if __name__ == "__main__":
    agent.run()
Path C: Mailbox uAgent Creation
For developers requiring custom libraries while maintaining Agentverse connectivity. Mailbox agents allow for asynchronous communication, enabling agents to receive messages even when they're offline.
When to Choose This Path
Your agent doesn't need to be continuously running
You want to receive messages even when your agent is offline
You need to use custom libraries or local resources
You want to reduce resource usage by running your agent intermittently
Step-by-Step Guide
Local Environment Setup

Follow steps 1-2 from Path B

Mailbox Configuration

Implement agent with mailbox parameter:

from uagents import Agent, Context, Model

# Define a message model
class Message(Model):
    message: str

# Define your unique seed phrase
AGENT_SEED = "your_unique_seed_phrase_here"

# Print the agent's address (needed for mailbox setup)
print(f"Your agent's address is: {Agent(seed=AGENT_SEED).address}")

# After creating a mailbox on agentverse.ai, add your mailbox key
AGENT_MAILBOX_KEY = "your_mailbox_key_here"

agent = Agent(
    name="mailbox_agent",
    seed=AGENT_SEED,
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

@agent.on_message(model=Message, replies={Message})
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(sender, Message(message="Thanks for your message!"))

if __name__ == "__main__":
    agent.run()

Agentverse Connection
Run the agent locally to generate the address
Visit agentverse.ai and log in
Navigate to the Mailroom section
Create a new mailbox using your agent's address
Copy the mailbox key and add it to your agent code
Run your agent again with the mailbox key configured
Creating a Pair of Communicating Mailbox Agents
Alice (alice.py):

from uagents import Agent, Context, Model

class Message(Model):
    message: str

ALICE_SEED = "alice_unique_seed_phrase"

# Print address for mailbox setup
print(f"Your agent's address is: {Agent(seed=ALICE_SEED).address}")

AGENT_MAILBOX_KEY = "alice_mailbox_key_from_agentverse"

agent = Agent(
    name="alice",
    seed=ALICE_SEED,
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

@agent.on_message(model=Message, replies={Message})
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(sender, Message(message="Hello there bob"))

if __name__ == "__main__":
    agent.run()

Bob (bob.py):

from uagents import Agent, Context, Model

class Message(Model):
    message: str

# Alice's address (from running alice.py)
ALICE_ADDRESS = "alice_agent_address_here"
BOB_SEED = "bob_unique_seed_phrase"

# Print address for mailbox setup
print(f"Your agent's address is: {Agent(seed=BOB_SEED).address}")

AGENT_MAILBOX_KEY = "bob_mailbox_key_from_agentverse"

bob = Agent(
    name="bob",
    seed=BOB_SEED,
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

@bob.on_interval(period=2.0)
async def send_message(ctx: Context):
    ctx.logger.info("Sending message to alice")
    await ctx.send(ALICE_ADDRESS, Message(message="Hello there alice"))

@bob.on_message(model=Message, replies=set())
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")

if __name__ == "__main__":
    bob.run()

Common Agent Patterns and Features
Regardless of which path you choose, there are several common patterns and features that you'll likely use in your agent development:
Storage and Persistence
Agents can store data persistently using the built-in storage system:

@agent.on_interval(period=60)
async def store_data(ctx: Context):
    # Store data
    ctx.storage.set("last_run", datetime.now().isoformat())
    ctx.storage.set("counter", ctx.storage.get("counter", 0) + 1)
    
    # Retrieve data
    last_run = ctx.storage.get("last_run")
    counter = ctx.storage.get("counter")
    ctx.logger.info(f"Run count: {counter}, Last run: {last_run}")
Protocols and Message Schemas
Define structured communication protocols using Pydantic models:

from pydantic import BaseModel, Field
from uagents import Model

# Define a protocol with multiple message types
class BookingRequest(Model):
    restaurant_name: str
    date: str
    time: str
    party_size: int
    special_requests: str = ""

class BookingResponse(Model):
    booking_id: str
    status: str
    confirmation_code: str = ""
    message: str

# Handle specific message types
@agent.on_message(model=BookingRequest, replies={BookingResponse})
async def handle_booking(ctx: Context, sender: str, msg: BookingRequest):
    # Process booking request
    booking_id = str(uuid.uuid4())
    # ... booking logic ...
    
    # Send response
    response = BookingResponse(
        booking_id=booking_id,
        status="confirmed",
        confirmation_code="ABC123",
        message=f"Your booking at {msg.restaurant_name} is confirmed"
    )
    await ctx.send(sender, response)
Error Handling
Implement robust error handling in your agents:

@agent.on_message(model=ApiRequest)
async def handle_api_request(ctx: Context, sender: str, msg: ApiRequest):
    try:
        # Attempt API call
        response = await make_api_call(msg.endpoint, msg.params)
        await ctx.send(sender, ApiResponse(data=response, success=True))
    except ConnectionError:
        # Handle connection issues
        ctx.logger.error("Connection failed")
        await ctx.send(sender, ApiResponse(
            success=False, 
            error="Connection to API failed"
        ))
    except Exception as e:
        # Handle unexpected errors
        ctx.logger.error(f"Unexpected error: {str(e)}")
        await ctx.send(sender, ApiResponse(
            success=False,
            error=f"An unexpected error occurred: {str(e)}"
        ))
Troubleshooting
Common Issues and Solutions
Issue
Possible Cause
Solution
Agent not starting
Port conflict
Change the port number in your agent configuration
Communication failure
Incorrect agent address
Double-check the recipient address format
Message not received
Schema mismatch
Ensure both agents use the same message model definition
Mailbox not working
Invalid mailbox key
Verify the mailbox key and format
API integration failing
Authentication issue
Check API keys and credentials
Agent crashes
Unhandled exception
Add try/except blocks around external API calls

Debugging Tips
Enable verbose logging: Set the log level to DEBUG for more detailed output

agent = Agent(name="debug_agent", log_level="DEBUG")

Use the inspector: The Agentverse inspector provides a visual interface for monitoring agent communication

Check agent addresses: Verify that you're using the correct agent addresses for communication

Validate message schemas: Ensure that your message models match between sending and receiving agents

Test incrementally: Start with simple functionality and add complexity gradually
Best Practices
Security
Secure seed phrases: Store seed phrases securely, never hardcode them in your application
Environment variables: Use environment variables for sensitive information like API keys
Message validation: Always validate incoming messages before processing them
Rate limiting: Implement rate limiting for agents that expose public endpoints
Performance
Lightweight handlers: Keep message handlers efficient and fast
Asynchronous operations: Use async/await for I/O-bound operations
Batch processing: Process data in batches when possible
Resource management: Close connections and free resources when they're no longer needed
Architecture
Single responsibility: Each agent should have a clear, focused purpose
Modular design: Break complex functionality into multiple communicating agents
Protocol-first design: Define your message protocols before implementing agent logic
Stateless when possible: Minimize state dependencies for more resilient agents
Next Steps
Now that you've set up your first agent, here are some ways to expand your knowledge and capabilities:

Explore the examples: Check out the example projects in the repository to see more complex agent implementations

Join the community: Connect with other Agentverse developers to share ideas and get help

Integrate with external services: Add capabilities to your agents by connecting them to APIs and services

Deploy to production: Move beyond local development by deploying your agents to cloud environments

Build multi-agent systems: Create networks of specialized agents that work together to solve complex problems

Happy agent building!

Introduction
Welcome to the Agentverse platform! This guide will help you get started with creating and deploying autonomous agents using the uAgents framework. Agentverse provides a powerful ecosystem for building, deploying, and managing autonomous agents that can communicate with each other and interact with external services.
What are uAgents?
uAgents (micro-agents) are lightweight, autonomous software entities that can:

Run independently and make decisions
Communicate with other agents using secure messaging
Execute tasks on a schedule
Interact with external APIs and services
Store and retrieve data
Integrate with AI models for enhanced capabilities
Choosing Your Development Path
Agentverse offers multiple paths for agent development, each suited to different needs and use cases. This guide covers four main approaches:

Path
Description
Best For
A: Hosted uAgent
Agents run on the Agentverse platform
Quick start, minimal setup, continuous availability
B: Local uAgent
Agents run on your local machine
Custom environments, local integrations, full control
C: Mailbox uAgent
Local agents with mailbox for async communication
Intermittent operation, offline message handling


Choose the path that best fits your project requirements and development preferences. You can always migrate between paths as your needs evolve.
Path A: Hosted uAgent Creation
For developers wanting the fastest, simplest route to agent creation with minimal setup. Hosted uAgents run on the Agentverse platform, eliminating the need for local infrastructure setup.
When to Choose This Path
You want to get started quickly without setting up a local environment
You need your agent to be continuously available without running your own server
You want to leverage the Agentverse platform's built-in monitoring and management tools
Step-by-Step Guide
Account Creation & Login

Create an account on the Agentverse platform
Log in to your dashboard

Agent Creation

Navigate to Agents tab → + New Agent
Select "Blank Agent" template
Name the agent (e.g., "MyFirstAgent")

Code Implementation

Open the embedded code editor
Implement basic agent code:

from uagents import Agent, Context, Model

# Create agent instance
agent = Agent(
    name="my_first_agent",
    seed="seed_phrase_for_agent" # Used to generate agent addresses
)

# Define startup behavior
@agent.on_event("startup")
async def startup_function(ctx: Context):
    ctx.logger.info(f"Hello, I'm {agent.name} and my address is {agent.address}.")

# Add message handling capabilities
class Message(Model):
    content: str

@agent.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.content}")
    # Respond to the message
    await ctx.send(sender, Message(content=f"Echo: {msg.content}"))

Deployment & Testing
Click "Start" to deploy the agent
View logs in the terminal below
Create a test agent that sends a message to your initial agent to test functionality
Key Features
Interval Tasks: Schedule recurring tasks using the @agent.on_interval decorator:

@agent.on_interval(period=2.0)  # Run every 2 seconds
async def periodic_task(ctx: Context):
    ctx.logger.info("Performing scheduled task...")

Event Handlers: React to agent lifecycle events:

@agent.on_event("startup")
async def on_startup(ctx: Context):
    ctx.logger.info("Agent is starting up!")

@agent.on_event("shutdown") 
async def on_shutdown(ctx: Context):
    ctx.logger.info("Agent is shutting down!")

Message Models: Define structured data models for communication:

class Telemetry(Model):
    temperature: float
    vibration: float
    
@agent.on_message(model=Telemetry)
async def handle_telemetry(ctx: Context, sender: str, msg: Telemetry):
    ctx.logger.info(f"Received telemetry: Temp={msg.temperature}°C, Vibration={msg.vibration}")
Path B: Local uAgent Creation
For developers preferring local development and greater customization. Local uAgents run on your own machine or server, giving you full control over the environment and execution.
When to Choose This Path
You need more control over your agent's environment
You want to integrate with local services or hardware
You prefer working in your own development environment
You need to use custom libraries or dependencies
Step-by-Step Guide
Environment Setup

Install Python 3.8+ if not already installed
Create a virtual environment:

python -m venv venv

Activate the environment:
Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate
Install uAgents:

pip install uagents

Project Initialization

Create a project directory:

mkdir my_agent_project && cd my_agent_project

Create a Python file:

touch my_agent.py  # On Unix/Mac
# OR
echo. > my_agent.py  # On Windows

Agent Implementation

Open my_agent.py in your preferred editor
Implement agent code with local configuration:

from uagents import Agent, Context

# Create agent instance with local configuration
agent = Agent(
    name="my_first_agent",
    port=8000,
    endpoint=["http://localhost:8000/submit"],
    publish_agent_details=True,  # Puts your agent on agentverse
    seed="seed_phrase_for_agent"  # Used to generate agent address
)

@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")

if __name__ == "__main__":
    agent.run()

Running & Testing
Run the agent:

python my_agent.py

Note the generated agent address in the logs
Test using a second agent or the Agentverse inspector URL provided in logs
Multi-Agent Communication Example
Create multiple agents that communicate with each other:

Agent 1 (machinery.py):

import random
from uagents import Agent, Context, Model

# Define telemetry model
class Telemetry(Model):
    temperature: float
    vibration: float

# Define response model
class RepairResponse(Model):
    status: str

agent = Agent(
    name="machinery",
    seed="machinery_seed_phrase",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

# Send telemetry data every 20 seconds
@agent.on_interval(period=20.0)
async def send_telemetry(ctx: Context):
    telemetry = Telemetry(
        temperature=random.uniform(20, 100),
        vibration=random.uniform(0, 10)
    )
    # Send to monitor agent (replace with actual address)
    await ctx.send('agent1qvk2ppctpjjj7ev6afdze3raup304pz7sc77sf6fk7h7n4uuexktx3t0der', telemetry)
    ctx.logger.info(f"Sent Telemetry: {telemetry}")

@agent.on_message(model=RepairResponse)
async def handle_repair(ctx: Context, sender: str, msg: RepairResponse):
    ctx.logger.info(f"Received repair info from {sender}: {msg.status}")

if __name__ == "__main__":
    agent.run()

Agent 2 (monitor.py):

from uagents import Agent, Context, Model

# Define telemetry model
class Telemetry(Model):
    temperature: float
    vibration: float

# Define repair request model
class RepairRequest(Model):
    issue: str
    value: float

agent = Agent(
    name="monitor",
    seed="monitor_seed_phrase",
    port=8001,
    endpoint=["http://localhost:8001/submit"]
)

@agent.on_message(model=Telemetry)
async def analyze_telemetry(ctx: Context, sender: str, msg: Telemetry):
    ctx.logger.info(f"Received telemetry from {sender}: {msg}")
    if msg.temperature > 80:
        request = RepairRequest(issue="High Temperature", value=msg.temperature)
        # Send to repairer agent (replace with actual address)
        await ctx.send('agent1qt5k53m7p3qt6kshx46g8jgg4drr8dczrgvkt5xuyl303scclmxuv4556sw', request)
        await ctx.send(sender, request)  # Notify sender
        ctx.logger.info(f"High Temp! Sent repair request: {request}")
    elif msg.vibration > 7:
        request = RepairRequest(issue="High Vibration", value=msg.vibration)
        await ctx.send('agent1qt5k53m7p3qt6kshx46g8jgg4drr8dczrgvkt5xuyl303scclmxuv4556sw', request)
        await ctx.send(sender, request)  # Notify sender
        ctx.logger.info(f"High Vibration! Sent repair request: {request}")
    else:
        ctx.logger.info("Telemetry Normal")

if __name__ == "__main__":
    agent.run()
Path C: Mailbox uAgent Creation
For developers requiring custom libraries while maintaining Agentverse connectivity. Mailbox agents allow for asynchronous communication, enabling agents to receive messages even when they're offline.
When to Choose This Path
Your agent doesn't need to be continuously running
You want to receive messages even when your agent is offline
You need to use custom libraries or local resources
You want to reduce resource usage by running your agent intermittently
Step-by-Step Guide
Local Environment Setup

Follow steps 1-2 from Path B

Mailbox Configuration

Implement agent with mailbox parameter:

from uagents import Agent, Context, Model

# Define a message model
class Message(Model):
    message: str

# Define your unique seed phrase
AGENT_SEED = "your_unique_seed_phrase_here"

# Print the agent's address (needed for mailbox setup)
print(f"Your agent's address is: {Agent(seed=AGENT_SEED).address}")

# After creating a mailbox on agentverse.ai, add your mailbox key
AGENT_MAILBOX_KEY = "your_mailbox_key_here"

agent = Agent(
    name="mailbox_agent",
    seed=AGENT_SEED,
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

@agent.on_message(model=Message, replies={Message})
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(sender, Message(message="Thanks for your message!"))

if __name__ == "__main__":
    agent.run()

Agentverse Connection
Run the agent locally to generate the address
Visit agentverse.ai and log in
Navigate to the Mailroom section
Create a new mailbox using your agent's address
Copy the mailbox key and add it to your agent code
Run your agent again with the mailbox key configured
Creating a Pair of Communicating Mailbox Agents
Alice (alice.py):

from uagents import Agent, Context, Model

class Message(Model):
    message: str

ALICE_SEED = "alice_unique_seed_phrase"

# Print address for mailbox setup
print(f"Your agent's address is: {Agent(seed=ALICE_SEED).address}")

AGENT_MAILBOX_KEY = "alice_mailbox_key_from_agentverse"

agent = Agent(
    name="alice",
    seed=ALICE_SEED,
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

@agent.on_message(model=Message, replies={Message})
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(sender, Message(message="Hello there bob"))

if __name__ == "__main__":
    agent.run()

Bob (bob.py):

from uagents import Agent, Context, Model

class Message(Model):
    message: str

# Alice's address (from running alice.py)
ALICE_ADDRESS = "alice_agent_address_here"
BOB_SEED = "bob_unique_seed_phrase"

# Print address for mailbox setup
print(f"Your agent's address is: {Agent(seed=BOB_SEED).address}")

AGENT_MAILBOX_KEY = "bob_mailbox_key_from_agentverse"

bob = Agent(
    name="bob",
    seed=BOB_SEED,
    mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

@bob.on_interval(period=2.0)
async def send_message(ctx: Context):
    ctx.logger.info("Sending message to alice")
    await ctx.send(ALICE_ADDRESS, Message(message="Hello there alice"))

@bob.on_message(model=Message, replies=set())
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")

if __name__ == "__main__":
    bob.run()

Common Agent Patterns and Features
Regardless of which path you choose, there are several common patterns and features that you'll likely use in your agent development:
Storage and Persistence
Agents can store data persistently using the built-in storage system:

@agent.on_interval(period=60)
async def store_data(ctx: Context):
    # Store data
    ctx.storage.set("last_run", datetime.now().isoformat())
    ctx.storage.set("counter", ctx.storage.get("counter", 0) + 1)
    
    # Retrieve data
    last_run = ctx.storage.get("last_run")
    counter = ctx.storage.get("counter")
    ctx.logger.info(f"Run count: {counter}, Last run: {last_run}")
Protocols and Message Schemas
Define structured communication protocols using Pydantic models:

from pydantic import BaseModel, Field
from uagents import Model

# Define a protocol with multiple message types
class BookingRequest(Model):
    restaurant_name: str
    date: str
    time: str
    party_size: int
    special_requests: str = ""

class BookingResponse(Model):
    booking_id: str
    status: str
    confirmation_code: str = ""
    message: str

# Handle specific message types
@agent.on_message(model=BookingRequest, replies={BookingResponse})
async def handle_booking(ctx: Context, sender: str, msg: BookingRequest):
    # Process booking request
    booking_id = str(uuid.uuid4())
    # ... booking logic ...
    
    # Send response
    response = BookingResponse(
        booking_id=booking_id,
        status="confirmed",
        confirmation_code="ABC123",
        message=f"Your booking at {msg.restaurant_name} is confirmed"
    )
    await ctx.send(sender, response)
Error Handling
Implement robust error handling in your agents:

@agent.on_message(model=ApiRequest)
async def handle_api_request(ctx: Context, sender: str, msg: ApiRequest):
    try:
        # Attempt API call
        response = await make_api_call(msg.endpoint, msg.params)
        await ctx.send(sender, ApiResponse(data=response, success=True))
    except ConnectionError:
        # Handle connection issues
        ctx.logger.error("Connection failed")
        await ctx.send(sender, ApiResponse(
            success=False, 
            error="Connection to API failed"
        ))
    except Exception as e:
        # Handle unexpected errors
        ctx.logger.error(f"Unexpected error: {str(e)}")
        await ctx.send(sender, ApiResponse(
            success=False,
            error=f"An unexpected error occurred: {str(e)}"
        ))
Troubleshooting
Common Issues and Solutions
Issue
Possible Cause
Solution
Agent not starting
Port conflict
Change the port number in your agent configuration
Communication failure
Incorrect agent address
Double-check the recipient address format
Message not received
Schema mismatch
Ensure both agents use the same message model definition
Mailbox not working
Invalid mailbox key
Verify the mailbox key and format
API integration failing
Authentication issue
Check API keys and credentials
Agent crashes
Unhandled exception
Add try/except blocks around external API calls

Debugging Tips
Enable verbose logging: Set the log level to DEBUG for more detailed output

agent = Agent(name="debug_agent", log_level="DEBUG")

Use the inspector: The Agentverse inspector provides a visual interface for monitoring agent communication

Check agent addresses: Verify that you're using the correct agent addresses for communication

Validate message schemas: Ensure that your message models match between sending and receiving agents

Test incrementally: Start with simple functionality and add complexity gradually
Best Practices
Security
Secure seed phrases: Store seed phrases securely, never hardcode them in your application
Environment variables: Use environment variables for sensitive information like API keys
Message validation: Always validate incoming messages before processing them
Rate limiting: Implement rate limiting for agents that expose public endpoints
Performance
Lightweight handlers: Keep message handlers efficient and fast
Asynchronous operations: Use async/await for I/O-bound operations
Batch processing: Process data in batches when possible
Resource management: Close connections and free resources when they're no longer needed
Architecture
Single responsibility: Each agent should have a clear, focused purpose
Modular design: Break complex functionality into multiple communicating agents
Protocol-first design: Define your message protocols before implementing agent logic
Stateless when possible: Minimize state dependencies for more resilient agents
Next Steps
Now that you've set up your first agent, here are some ways to expand your knowledge and capabilities:

Explore the examples: Check out the example projects in the repository to see more complex agent implementations

Join the community: Connect with other Agentverse developers to share ideas and get help

Integrate with external services: Add capabilities to your agents by connecting them to APIs and services

Deploy to production: Move beyond local development by deploying your agents to cloud environments

Build multi-agent systems: Create networks of specialized agents that work together to solve complex problems

Happy agent building!

