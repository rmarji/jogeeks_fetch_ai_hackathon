---
id: sdk-uagent-communication
title: AI Agent to uAgent Communication
---

# uAgent ↔ AI Agent Communication Using Fetch.ai SDK and uAgents

This guide demonstrates how to enable communication between a Microservice Agent created using the uagents framework and an AI Agent created using the Fetch.ai SDK. 


### uAgent Script (uagent.py)

Please remember to have the __uagents__ and the __fetchai__ package installed in the terminal in order to create and run the agents.

This uAgent will receive a message from the AI Agent and send a response back.

```py title='uagent.py'
from uagents import Agent, Context, Model

# Define the request model the uAgent will handle
class Request(Model):
    message: str

# Define the response model the uAgent will send back
class Response(Model):
    response: str

# Initialize the uAgent
uagent = Agent(
    name="Sample uAgent",
    port=8000,
    endpoint=["http://localhost:8000/submit"]
)

# Handle incoming messages with the Request model
@uagent.on_message(model=Request)
async def message_handler(ctx: Context, sender: str, msg: Request):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")

    # Generate a response message
    response = Response(response=f'Hello, AI Agent! I received your message:{msg.message}')
    
    # Send the response back to the AI Agent
    await ctx.send(sender, response)

if __name__ == "__main__":
    uagent.run()
```

### Explanation
- __Agent Initialization__: The uAgent listens on port 8000 for incoming messages.
- __Message Handling__: When a message matching the `Request` model is received, the agent logs it and responds with a predefined message using the `Response` model.

## Setting Up the AI Agent

The AI Agent will send messages to the uAgent and handle the response received from the uAgent.

### AI Agent Script (ai_agent.py)

```py title='ai_agent.py'
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from fetchai.communication import send_message_to_agent, parse_message_from_agent
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

client_identity = None
agent_response = None

class Request(Model):
    message: str

# Load environment variables from .env file
load_dotenv()

def init_client():
    """Initialize and register the client agent."""
    global client_identity
    try:
        # Load the client identity from environment variables
        client_identity = Identity.from_seed("Sample AI AGENT SEED PHRASE for communication", 0)
        logger.info(f"Client agent started with address: {client_identity.address}")

        readme = """
        ![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
        domain:domain-of-your-agent

        <description>This Agent can send a message to a uAgent and receive a message from a uAgent in string format.</description>
        <use_cases>
        <use_case>Send and receive messages with another uAgent.</use_case>
        </use_cases>
        <payload_requirements>
            <description>This agent can only send and receive messages in text format.</description>
            <payload>
                <requirement>
                    <parameter>message</parameter>
                    <description>The agent sends and receives messages in text format.</description>
                </requirement>
            </payload>
        </payload_requirements>
        """

        # Register the agent with Agentverse
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5002/api/webhook",
            agentverse_token = os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Sample AI Agent communication"
            readme=readme
        )

        logger.info("Client agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise


@app.route('/request', methods=['POST'])
def send_data():
    """Send payload to the selected agent based on provided address."""
    global agent_response
    agent_response = None

    try:
        # Parse the request payload
        data = request.json
        payload = data.get('payload')  # Extract the payload dictionary

        uagent_address = "agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6" #run the uagent.py copy the address and paste here
        
        # Build the Data Model digest for the Request model to ensure message format consistency between the uAgent and AI Agent
        model_digest = Model.build_schema_digest(Request)

        # Send the payload to the specified agent
        send_message_to_agent(
            client_identity,  # Frontend client identity
            uagent_address,  # Agent address where we have to send the data
            payload,  # Payload containing the data
            model_digest=model_digest
        )

        return jsonify({"status": "request_sent", "payload": payload})

    except Exception as e:
        logger.error(f"Error sending data to agent: {e}")
        return jsonify({"error": str(e)}), 500



# app route to get recieve the messages on the agent
@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages from the dashboard agent."""
    global agent_response
    try:
        # Parse the incoming webhook message
        data = request.get_data().decode("utf-8")
        logger.info("Received response")
        message = parse_message_from_agent(data)
        agent_response = message.payload
        logger.info(f"Processed response: {agent_response}")
        return jsonify({"status": "success"})
    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    load_dotenv()
    init_client()
    app.run(host="0.0.0.0", port=5002)
```

### Explanation

- __Data Model__: The Request and Response models define the structure of messages exchanged between the AI Agent and the uAgent. A correctly defined data model is essential for sending a message to the uAgent from an SDK-based AI Agent.
- __Schema Validation__: The model digest ensures that messages conform to the expected schema before transmission, preventing format mismatches.
- __Sending Data__: The AI Agent sends a message to the uAgent using the /request endpoint.
- __Handling Response__: The AI Agent listens for responses using the /api/webhook endpoint.

## Environment Variables

Create a .env file and add the following environment variables:

```bash
AGENTVERSE_API_KEY="YOUR_AGENTVERSE_API_KEY"
AGENT_SECRET_KEY="YOUR_SECRET_KEY_FOR_AI_AGENT"
```

Replace the placeholders with your actual API keys and agent secrets. Refer to this [guide](../agentverse/agentverse-api-key) to get your Agentverse API Key.



## Testing the Communication

### Step 1: Running the uAgent

Start the uAgent by running the following command in your terminal:

```bash
python uagent.py
```
#### uAgent Logs
```bash
(venv) abhi@Fetchs-MacBook-Pro ILAgents % python3 uagent.py
INFO:     [Sample uAgent]: Starting agent with address: agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
INFO:     [Sample uAgent]: My name is Sample uAgent and my address is agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
INFO:     [Sample uAgent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8000&address=agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
INFO:     [Sample uAgent]: Starting server on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     [uagents.registration]: Registration on Almanac API successful
INFO:     [uagents.registration]: Registering on almanac contract...
INFO:     [uagents.registration]: Registering on almanac contract...complete
```
#### Copy the uAgent Address
Look for the uAgent address in the logs, which appears in this format:
```bash
agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
```
Copy this uAgent address and paste it into the AI Agent script at the following line:
```bash
uagent_address="PASTE YOUR UAGENT ADDRESS HERE"
```

### Step 2: Running the AI Agent
Start the AI Agent by running the following command in your terminal:

```bash
python ai_agent.py
```

#### AI Agent Logs
```bash
(venv) abhi@Fetchs-MacBook-Pro ILAgents % python3 ai_agent.py
INFO:__main__:Client agent started with address: agent1qw7u5sw63a88kmcn5j5kxf7q326u5hgmppvy2vpxlh3re6y0yp8253ec7xl
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Client agent registration complete!
 * Serving Flask app 'ai_agent'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5002
 * Running on http://172.20.10.2:5002
INFO:werkzeug:Press CTRL+C to quit

```

### Step 3: Sending a message from Agent2 to Agent1

We will use the following curl command to send a message from the AI Agent to the uAgent:

```bash
curl -X POST http://localhost:5002/request \
-H "Content-Type: application/json" \
-d '{
  "payload": {"message": "Hello uAgent!"}
}'
```

#### Expected Logs on the uAgent Terminal

```bash
(venv) abhi@Fetchs-MacBook-Pro ILAgents % python3 uagent.py
INFO:     [Sample uAgent]: Starting agent with address: agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
INFO:     [Sample uAgent]: My name is Sample uAgent and my address is agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
INFO:     [Sample uAgent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8000&address=agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6
INFO:     [Sample uAgent]: Starting server on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     [uagents.registration]: Registration on Almanac API successful
INFO:     [uagents.registration]: Registering on almanac contract...
INFO:     [uagents.registration]: Registering on almanac contract...complete
INFO:     [Sample uAgent]: Received message from agent1qw7u5sw63a88kmcn5j5kxf7q326u5hgmppvy2vpxlh3re6y0yp8253ec7xl: Hello uAgent!
```

#### Expected Logs on the AI Agent Terminal

```bash
(venv) abhi@Fetchs-MacBook-Pro ILAgents % python3 ai_agent.py
INFO:__main__:Client agent started with address: agent1qw7u5sw63a88kmcn5j5kxf7q326u5hgmppvy2vpxlh3re6y0yp8253ec7xl
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Client agent registration complete!
 * Serving Flask app 'ai_agent'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5002
 * Running on http://172.20.10.2:5002
INFO:werkzeug:Press CTRL+C to quit
{"version":1,"sender":"agent1qw7u5sw63a88kmcn5j5kxf7q326u5hgmppvy2vpxlh3re6y0yp8253ec7xl","target":"agent1qgd54rrq8ex4uhdxe6qg0sklz7h7dkacdk9rz4ec0l304wghw88sg35rfk6","session":"c28d03fd-ad42-4c09-80b8-2bb8df9d7c3e","schema_digest":"model:14d760ab9a6127711e530c0f1bd84d5caa48c6bc6566ca489581d6918e6dff85","protocol_digest":"proto:a03398ea81d7aaaf67e72940937676eae0d019f8e1d8b5efbadfef9fd2e98bb2","payload":"eyJtZXNzYWdlIjoiaGV5In0=","expires":null,"nonce":null,"signature":"sig14ukfdrc98924wvx66xa2c32pk2wqyn69cepkvcpwahlygv3tc2t8hrzfkuzc9earscpnasdt8txpu99cyw24gmyspfdhqkxsn7a3lnq60mpaq"}
INFO:fetchai:Got response looking up agent endpoint
http://localhost:8000/submit
INFO:fetchai:Sent message to agent
INFO:werkzeug:127.0.0.1 - - [30/Jan/2025 14:21:58] "POST /request HTTP/1.1" 200 -
INFO:__main__:Received response
INFO:__main__:Processed response: {'response': 'Hello, AI Agent! I received your message: Hello uAgent!'}
INFO:werkzeug:127.0.0.1 - - [30/Jan/2025 14:21:58] "POST /api/webhook HTTP/1.1" 200 -
```


## Explanation of Communication Flow

- The AI Agent sends a message using the __send_message_to_agent__ function.
- The uAgent receives the message via the __@uagent.on_message__ handler.
- The uAgent processes the message and responds using __await ctx.send()__.
- The AI Agent receives the response through the __/api/webhook__ endpoint.

## Key Takeaways

- The __uAgent__ handles structured messages using Fetch.ai’s uAgents framework.
- The __AI Agent__ utilizes Fetch.ai’s SDK for message transmission and parsing.
- Communication between the two agents follows a request-response pattern using their respective handlers.


This setup can be extended to build more complex agent interactions involving dynamic data exchange, service orchestration, and autonomous decision-making.
