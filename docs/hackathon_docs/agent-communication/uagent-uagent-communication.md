---
id: uagent-uagent-communication
title: uAgent to uAgent Communication
---

# uAgent ↔ uAgent Communication
In the uAgents Framework, agents can be triggered in multiple ways using different types of handlers. These handlers act as decorators, enabling agents to execute specific functions based on predefined conditions. In this section, we will explore two handlers. Below are the available handlers which can be used with uAgents:


    - on_event()
    - on_message()
    - on_rest_get()
    - on_rest_post()

## on_event

Agents can respond to events such as initialization and termination. The startup and shutdown handlers are used by the uAgents library to manage these events, ensuring that specific actions are executed when an agent starts or stops.
### on_event("startup")

```python
@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and my address is {agent.address}.")
    ...
```

### on_event("shutdown")

```python
@agent.on_event("shutdown")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm agent {agent.name} and I am shutting down")
    ...
```

## on_message()

In this section, we will explore the on_message() decorator, which allows us to send messages between microservice agents in a structured way. We will create two microservice agents and enable them to communicate with each other.

Let's create agent1 who will send a message to agent2 on startup.

### uAgent1 Script

Please remember to have the __uagents__ package installed in the terminal in order to create and run uAgents.

```py title='uagent1.py'
from uagents import Agent, Context, Model

# Data model (envolope) which you want to send from one agent to another
class Message(Model):
    message : str
    field : int

my_first_agent = Agent(
    name = 'My First Agent',
    port = 5050,
    endpoint = ['http://localhost:5050/submit']
)

second_agent = 'your_second_agent_address'

@my_first_agent.on_event('startup')
async def startup_handler(ctx : Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address  is {ctx.agent.address}')
    await ctx.send(second_agent, Message(message = 'Hi Second Agent, this is the first agent.'))

if __name__ == "__main__":
    my_first_agent.run()
```

### uAgent2 Script

```py title='uagent2.py'
from uagents import Agent, Context, Model

class Message(Model):
    message : str

my_second_agent = Agent(
    name = 'My Second Agent',
    port = 5051,
    endpoint = ['http://localhost:5051/submit']
)

@my_second_agent.on_event('startup')
async def startup_handler(ctx : Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address  is {ctx.agent.address}')

@my_second_agent.on_message(model = Message)
async def message_handler(ctx: Context, sender : str, msg: Message):
    ctx.logger.info(f'I have received a message from {sender}.')
    ctx.logger.info(f'I have received a message {msg.message}.')

if __name__ == "__main__":
    my_second_agent.run()
```

We need to define the data Model which is `class Message` in both the sender and receiver agents. The receiving agent must include an `on_message` handler that correctly implements this data model. It is crucial to ensure that both agents use the exact same data model for seamless communication.

### Running agents

Now that we have created both agents, let's run them in separate terminals. Agent 2 is on the receiver's end so we have to start agent2 first. Whenever agent1 is started it will send message to agent 2 and it will receive and handle the message.

#### Terminal 1

```
python3 agent2.py
```
#### Terminal 2

```
python3 agent1.py
```

### Expected Output

```
abhi@Fetchs-MacBook-Pro testing % python3 second_agent.py 
INFO:     [My Second Agent]: Starting agent with address: agent1qtgc4vqn4ehh88hct0umnnqeg36m5722hc4e63lwy573kjtqee7qg5afmap
INFO:     [My Second Agent]: My name is My Second Agent and my address  is agent1qtgc4vqn4ehh88hct0umnnqeg36m5722hc4e63lwy573kjtqee7qg5afmap
INFO:     [My Second Agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A5051&address=agent1qtgc4vqn4ehh88hct0umnnqeg36m5722hc4e63lwy573kjtqee7qg5afmap
INFO:     [My Second Agent]: Starting server on http://0.0.0.0:5051 (Press CTRL+C to quit)
INFO:     [My Second Agent]: Registration on Almanac API successful
INFO:     [My Second Agent]: Almanac contract registration is up to date!
INFO:     [My Second Agent]: I have received a message from agent1q0kpqwd5q7akt9utnw540h293zhw063ua90m66rkx5lg98wq4zrjkhmgwd7.
INFO:     [My Second Agent]: I have received a message Hi Second Agent, this is the first agent..
```

```
abhi@Fetchs-MacBook-Pro testing % python3 first_agent.py
INFO:     [My First Agent]: Starting agent with address: agent1q0kpqwd5q7akt9utnw540h293zhw063ua90m66rkx5lg98wq4zrjkhmgwd7
INFO:     [My First Agent]: My name is My First Agent and my address  is agent1q0kpqwd5q7akt9utnw540h293zhw063ua90m66rkx5lg98wq4zrjkhmgwd7
INFO:     [My First Agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A5050&address=agent1q0kpqwd5q7akt9utnw540h293zhw063ua90m66rkx5lg98wq4zrjkhmgwd7
INFO:     [My First Agent]: Starting server on http://0.0.0.0:5050 (Press CTRL+C to quit)
INFO:     [My First Agent]: Registration on Almanac API successful
INFO:     [My First Agent]: Almanac contract registration is up to date!
```

## REST Endpoints

The uAgents Framework allows you to add custom REST endpoints to your agents using two decorators: `on_rest_get()` and `on_rest_post()`. This feature is available at the agent level only and cannot be added to uAgents Protocols.

### Adding REST Endpoints

The usage is similar to message handlers, but with some key differences:

1. You define a custom endpoint in string format (e.g., "/my_rest_endpoint")
2. For POST endpoints, you need a Request Model (inheriting from uagents.models)
3. You need a Response Model for both GET and POST endpoints
4. You must explicitly return a value to the REST client (either as Dict[str, Any] or as the Model itself)

### Example Implementation

Here's a complete example showing both GET and POST endpoints:

```python
import time
from typing import Any, Dict
from uagents import Agent, Context, Model

# Define your models
class Request(Model):
    text: str

class Response(Model):
    timestamp: int
    text: str
    agent_address: str

# Create your agent
agent = Agent(name="Rest API")

# GET endpoint example
@agent.on_rest_get("/rest/get", Response)
async def handle_get(ctx: Context) -> Dict[str, Any]:
    ctx.logger.info("Received GET request")
    return {
        "timestamp": int(time.time()),
        "text": "Hello from the GET handler!",
        "agent_address": ctx.agent.address,
    }

# POST endpoint example
@agent.on_rest_post("/rest/post", Request, Response)
async def handle_post(ctx: Context, req: Request) -> Response:
    ctx.logger.info("Received POST request")
    return Response(
        text=f"Received: {req.text}",
        agent_address=ctx.agent.address,
        timestamp=int(time.time()),
    )

if __name__ == "__main__":
    agent.run()
```

### Using the REST Endpoints

To interact with these endpoints, ensure:
1. You use the correct REST method ("GET" or "POST")
2. You address the agent endpoint together with its route (http://localhost:8000/custom_route)

#### Running the Example

1. Start the agent:
```bash
python agent.py
```

2. Query the POST endpoint:
```bash
curl -d '{"text": "test"}' -H "Content-Type: application/json" -X POST http://localhost:8000/rest/post
```

Example POST response:
```json
{
    "timestamp": 1709312457,
    "text": "Received: test",
    "agent_address": "agent1qv3h4tkmvqz8jn8hs7q7y9rg8yh6jzfz7yf3xm2x2z7y8q9w2j5q9n8h6j"
}
```

3. Query the GET endpoint:

```bash
curl http://localhost:8000/rest/get
```
Example GET response:
```json
{
    "timestamp": 1709312460,
    "text": "Hello from the GET handler!",
    "agent_address": "agent1qv3h4tkmvqz8jn8hs7q7y9rg8yh6jzfz7yf3xm2x2z7y8q9w2j5q9n8h6j"
}
```

The REST endpoints provide a convenient way to integrate your uAgents with web services and other HTTP-based systems.


## Agent Communication Methods

The uAgents framework provides two primary methods for agents to communicate with each other: `ctx.send` and `ctx.send_and_receive`. Each serves different communication patterns.

### 1. Using ctx.send (Asynchronous Communication)

The `ctx.send` method allows for simple one-way communication between agents. This is useful when an agent needs to notify another agent without requiring an immediate response.

#### Example using ctx.send

```python
from uagents import Agent, Bureau, Context, Model

class Message(Model):
    text: str

alice = Agent(name="alice", seed="alice recovery phrase")
bob = Agent(name="bob", seed="bob recovery phrase")

@alice.on_interval(period=2.0)
async def send_message(ctx: Context):
    msg = f"Hello there {bob.name} my name is {alice.name}."
    await ctx.send(bob.address, Message(text=msg))

@bob.on_message(model=Message)
async def message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.text}")

bureau = Bureau()
bureau.add(alice)
bureau.add(bob)

if __name__ == "__main__":
    bureau.run()
```

When running this example, Alice will send a message to Bob every 2 seconds, and Bob will log the received message.

### 2. Using ctx.send_and_receive (Synchronous Communication)

The `ctx.send_and_receive` method allows for request-response style communication between agents. This is useful when an agent needs to make a request and wait for a response before proceeding.

Available from uAgents version 0.21.1 onwards, this method returns both the response and a status indicator.

#### Example using ctx.send_and_receive

```python
from uagents import Agent, Bureau, Context, Model

class Message(Model):
    message: str

alice = Agent(name="alice")
bob = Agent(name="bob")
clyde = Agent(name="clyde")

@alice.on_interval(period=5.0)
async def send_message(ctx: Context):
    msg = Message(message="Hey Bob, how's Clyde?")
    reply, status = await ctx.send_and_receive(bob.address, msg, response_type=Message)
    if isinstance(reply, Message):
        ctx.logger.info(f"Received awaited response from bob: {reply.message}")
    else:
        ctx.logger.info(f"Failed to receive response from bob: {status}")

@bob.on_message(model=Message)
async def handle_message_and_reply(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message: {msg.message}")
    new_msg = Message(message="How are you, Clyde?")
    reply, status = await ctx.send_and_receive(
        clyde.address, new_msg, response_type=Message
    )
    if isinstance(reply, Message):
        ctx.logger.info(f"Received awaited response from clyde: {reply.message}")
        await ctx.send(sender, Message(message="Clyde is doing alright!"))
    else:
        ctx.logger.info(f"Failed to receive response from clyde: {status}")

@clyde.on_message(model=Message)
async def handle_message(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(sender, Message(message="I'm doing alright!"))

bureau = Bureau([alice, bob, clyde])

if __name__ == "__main__":
    bureau.run()
```

#### Expected Output

When running this example, you'll see a chain of communication:

1. Alice asks Bob about Clyde's status
2. Bob asks Clyde about his status
3. Clyde responds to Bob
4. Bob responds to Alice

The console output will look similar to:

```
INFO: [alice]: Sending message to agent1qxxx...
INFO: [bob]: Received message: Hey Bob, how's Clyde?
INFO: [bob]: Sending message to agent1qyyy...
INFO: [clyde]: Received message from agent1qxxx: How are you, Clyde?
INFO: [clyde]: Sending message to agent1qxxx...
INFO: [bob]: Received awaited response from clyde: I'm doing alright!
INFO: [bob]: Sending message to agent1qzzz...
INFO: [alice]: Received awaited response from bob: Clyde is doing alright!
```

### Key Differences

| Feature | ctx.send | ctx.send_and_receive |
|---------|----------|----------------------|
| Communication Pattern | One-way (fire and forget) | Request-response |
| Waiting for Response | No | Yes |
| Return Value | None | Tuple of (response, status) |
| Use Case | Notifications, broadcasts | Queries, confirmations, multi-step workflows |

Choose the appropriate method based on your agents' communication requirements:
- Use `ctx.send` for simple notifications or information updates
- Use `ctx.send_and_receive` when you need a response to continue processing