---
id: asi1-chat-system
title: ASI1 Chat System
---

# ASI1 Chat System using uAgents Framework To Communicate with HuggingFace

This guide explains how the ASI1 Chat System facilitates real-time communication between autonomous agents and external APIs to process user queries efficiently.

## Overview

This project demonstrates how to create a multi-agent system using the uAgents framework and ASI1 Mini. The system, consisting of a server agent and a client agent, is designed to:

- Enable interactive query handling using the ASI1 API.
- Allow users to send queries about Hugging Face models.
- Process responses through a server-client architecture.
- Demonstrate agent-to-agent communication patterns.

## Prerequisites

Before running this project, ensure you have:

- Python 3.11 installed.
- uAgents library installed. If not already installed, use:
  ```bash
  pip install uagents
  ```
- Requests library installed:
  ```bash
  pip install requests
  ```
- A valid API key for ASI1. Obtain your API Key [here](https://asi1.ai/dashboard/api-keys).
- Environment variable set for your ASI1 API key:
  ```bash
  export ASI1_API_KEY="your_api_key_here"
  ```

## Server Agent Script

The Server Agent is responsible for receiving queries from the Client Agent, processing them using the ASI1 API, and returning the responses.

### Script Breakdown (server.py)

#### Importing Required Libraries

```python
import requests
import os
from uagents import Agent, Context, Model
```

#### Defining Data Models

```python
# Request model
class ASI1Query(Model):
    query: str
    sender_address: str

# Response model
class ASI1Response(Model):
    response: str  # Response from ASI1 API
```

#### Initializing the Server Agent

```python
# Define the main agent
mainAgent = Agent(
    name='asi1_chat_agent',
    port=5068,
    endpoint='http://localhost:5068/submit',
    seed='asi1_chat_seed'
)
```

#### ASI1 API Integration Function

```python
def get_asi1_response(query: str) -> str:
    """
    Sends a query to ASI1 API and returns the response.
    """
    # Get API key from environment variable
    api_key = os.environ.get("ASI1_API_KEY")
    if not api_key:
        return "Error: ASI1_API_KEY environment variable not set"
        
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "asi1-mini",  # Select appropriate ASI1 model
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": query}
        ]
    }

    try:
        response = requests.post("https://api.asi1.ai/v1/chat/completions", json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "ASI1 API returned an empty response."
        else:
            return f"ASI1 API Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"ASI1 API Error: {str(e)}"
```

#### Event Handlers

```python
@mainAgent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'Agent {ctx.agent.name} started at {ctx.agent.address}')

# Handler for receiving query
@mainAgent.on_message(model=ASI1Query)
async def handle_query(ctx: Context, sender: str, msg: ASI1Query):
    ctx.logger.info(f"Received query from {sender}: {msg.query}")

    # Call ASI1 API for the response
    answer = get_asi1_response(msg.query)

    # Respond back with the answer from ASI1
    await ctx.send(sender, ASI1Response(response=answer))
```

#### Running the Server Agent

```python
if __name__ == "__main__":
    mainAgent.run()
```

## Client Agent Script

The Client Agent acts as the user interface, collecting input from the user and sending it to the Server Agent for processing.

### Script Breakdown (client.py)

#### Importing Required Libraries

```python
from uagents import Agent, Context, Model
```

#### Defining Data Models

```python
# Query model to send to the server agent
class ASI1Query(Model):
    query: str
    sender_address: str

# Response model to receive from the server agent
class ASI1Response(Model):
    response: str
```

#### Initializing the Client Agent

```python
# Client agent setup
clientAgent = Agent(
    name='asi1_client_agent',
    port=5070,
    endpoint='http://localhost:5070/submit',
    seed='asi1_client_seed'
)

# Server agent address (update with actual address if needed)
SERVER_AGENT_ADDRESS = "agent1q0usc8uc5hxes4ckr8624ghdxpn0lvxkgex44jtfv32x2r7ymx8sgg8yt2g"  # Replace with the actual address of your server agent
```

#### Event Handlers

```python
@clientAgent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'Client Agent {ctx.agent.name} started at {ctx.agent.address}')

    # Get user input
    user_query = input("Ask something: ")

    # Send the query to the server agent
    await ctx.send(SERVER_AGENT_ADDRESS, ASI1Query(query=user_query, sender_address=ctx.agent.address))
    ctx.logger.info(f"Query sent to server agent: {user_query}")

@clientAgent.on_message(model=ASI1Response)
async def handle_response(ctx: Context, sender: str, msg: ASI1Response):
    ctx.logger.info(f"Response received from {sender}: {msg.response}")
    print(f"Response from ASI1 API: {msg.response}")
```

#### Running the Client Agent

```python
if __name__ == "__main__":
    clientAgent.run()
```

## Running the System

__1. Set Environment Variable for API Key__

Before running the agents, set the ASI1 API key as an environment variable:

```bash
export ASI1_API_KEY="your_api_key_here"
```

__2. Start the Server Agent__

Open a terminal window and run:

```bash
python server.py
```

You should see output similar to:

```
INFO:     [asi1_chat_agent]: Starting agent with address: agent1q0usc8uc5hxes4ckr8624ghdxpn0lvxkgex44jtfv32x2r7ymx8sgg8yt2g
INFO:     [asi1_chat_agent]: Agent asi1_chat_agent started at agent1q0usc8uc5hxes4ckr8624ghdxpn0lvxkgex44jtfv32x2r7ymx8sgg8yt2g
INFO:     [asi1_chat_agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A5068&address=agent1q0usc8uc5hxes4ckr8624ghdxpn0lvxkgex44jtfv32x2r7ymx8sgg8yt2g
INFO:     [asi1_chat_agent]: Starting server on http://0.0.0.0:5068 (Press CTRL+C to quit)
INFO:     [asi1_chat_agent]: Registration on Almanac API successful
INFO:     [asi1_chat_agent]: Almanac contract registration is up to date!
```

__3. Start the Client Agent__

Open a new terminal window and run:

```bash
python client.py
```

You should see output similar to:

```
INFO:     [asi1_client_agent]: Starting agent with address: agent1qdszugnhqtadhg38tgxnzlyards0qpf0mx5x4l4ms3qq9g8fadxfgxv5dfr
INFO:     [asi1_client_agent]: Client Agent asi1_client_agent started at agent1qdszugnhqtadhg38tgxnzlyards0qpf0mx5x4l4ms3qq9g8fadxfgxv5dfr
Ask something: 
```

__4. Interact with the System__

When prompted, enter a query about Hugging Face models, for example:

```
Ask something: Image Classification
```

The client will send this query to the server agent:

```
INFO:     [asi1_client_agent]: Query sent to server agent: Image Classification
INFO:     [asi1_client_agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A5070&address=agent1qdszugnhqtadhg38tgxnzlyards0qpf0mx5x4l4ms3qq9g8fadxfgxv5dfr
INFO:     [asi1_client_agent]: Starting server on http://0.0.0.0:5070 (Press CTRL+C to quit)
INFO:     [asi1_client_agent]: Registration on Almanac API successful
INFO:     [asi1_client_agent]: Almanac contract registration is up to date!
```

__5. View the Response__

The server agent will process the query and send back a response:

```
INFO:     [asi1_chat_agent]: Received query from agent1qdszugnhqtadhg38tgxnzlyards0qpf0mx5x4l4ms3qq9g8fadxfgxv5dfr: Image Classification
```

The client agent will display the response:

```
INFO:     [asi1_client_agent]: Response received from agent1q0usc8uc5hxes4ckr8624ghdxpn0lvxkgex44jtfv32x2r7ymx8sgg8yt2g: It's difficult to give a definitive "top 5" list for most downloaded and highest-rated models on Hugging Face for Image Classification as these metrics change frequently. As of my last knowledge update, these are some of the highly regarded and popular models for image classification you could find on Hugging Face:

1. **ViT (Vision Transformer):** Developed by Google Research, ViT models are known for their strong performance on image classification tasks, leveraging the transformer architecture originally designed for natural language processing. They are often pre-trained on large datasets and then fine-tuned for specific image classifications.

2. **ResNet (Residual Network):** Developed by Microsoft Research, various ResNet architectures (e.g., ResNet50, ResNet101, ResNet152) are widely used. ResNet introduced the concept of skip connections, allowing for the training of very deep networks and achieving excellent performance on image classification.

3. **EfficientNet:** Developed by Google Research, EfficientNet models focus on optimizing accuracy and efficiency. They are known for achieving high performance with relatively fewer parameters compared to other models.

4. **Inception:** Also developed by Google, Inception models (e.g., InceptionV3) utilize inception modules with multiple convolutional filters operating at different scales to capture features at various levels of detail within an image.

5. **MobileNet:** Developed by Google, MobileNet models are designed specifically for mobile and embedded vision applications. They are known for their efficiency and smaller model sizes, allowing for deployment on resource-constrained devices while still maintaining reasonable accuracy for image classification.

Keep in mind that popularity and download counts on Hugging Face are dynamic. I recommend checking the Hugging Face model hub directly for the most up-to-date information on downloads and ratings. You can sort models by different metrics there.
```

## Troubleshooting Common Issues

__API Key Not Found__

If you see the error "ASI1_API_KEY environment variable not set", make sure you've set the environment variable correctly:

```bash
export ASI1_API_KEY="your_api_key_here"
```

__Connection Issues__

If the client agent cannot connect to the server agent:

1. Ensure the server agent is running and note its address.
2. Update the `SERVER_AGENT_ADDRESS` in the client.py script with the correct address.
3. Check that both agents are running on their specified ports (5068 and 5070).

__API Response Errors__

If you receive API errors:

1. Verify your ASI1 API key is valid and has not expired.
2. Check your internet connection.
3. Ensure the ASI1 API service is operational.

## GitHub Repository

For the complete code, visit the [ASI1 Chat System Repository](https://github.com/Atharva-Pore/AP_uAgents/tree/main/asi1_chat_system).

:::note
**Note:** You can learn more about ASI1 Mini APIs [__here__](https://docs.asi1.ai/docs/) and about uAgents [__here__](../../agent-creation/uagent-creation.mdx).
::: 