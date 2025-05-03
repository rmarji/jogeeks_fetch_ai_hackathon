---
id: sdk-sdk-communication
title: AI Agent to AI Agent Communication
---
# AI Agent ↔ AI Agent Communication

In this guide, we will create two AI agents using the fetchai SDK and then see how to send and handle requests received by these agents.
You can find all our supporting code files in our dedicated [github repo](https://github.com/fetchai/fetchai).

## AI Agent creation

Let's start by creating an AI Agent using the [fetchai SDK](https://github.com/fetchai/fetchai).

Please remember to have the __fetchai__ package installed in the terminal in order to create and run the agents.


### Creating our first agent to receive the message

Create a new Python script:

```bash
touch my_first_sdk_agent.py
```

Open `my_first_sdk_agent.py` in your text editor and add the following code which helps you register your agent and handle messages:

```py title="my_first_sdk_agent.py"
from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from fetchai import fetch
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

# Initialising client identity to get registered on agentverse
client_identity = None 

# Function to register agent
def init_client():
    """Initialize and register the client agent."""
    global client_identity
    try:
        # Load the agent secret key from environment variables
        client_identity = Identity.from_seed(os.getenv("AGENT_SECRET_KEY_1"), 0)
        logger.info(f"Client agent started with address: {client_identity.address}")

        readme = """
            ![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
            domain:domain-of-your-agent

            <description>This Agent can only receive a message from another agent in string format.</description>
            <use_cases>
                <use_case>To receive a message from another agent.</use_case>
            </use_cases>
            <payload_requirements>
            <description>This agent only requires a message in the text format.</description>
            <payload>
                <requirement>
                    <parameter>message</parameter>
                    <description>The agent can receive any kind of message.</description>
                </requirement>
            </payload>
            </payload_requirements>
        """
        

        # Register the agent with Agentverse
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5002/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Quickstart Agent 1",
            readme=readme
        )

        logger.info("Quickstart agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise

# app route to recieve the messages from other agents
@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages"""
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
    load_dotenv()       # Load environment variables
    init_client()       #Register your agent on Agentverse
    app.run(host="0.0.0.0", port=5002)      
```
Save the `.env` file with your `AGENTVERSE_KEY` and `AGENT_SECRET_KEY_1`, get your `AGENTVERSE_KEY` by referring to this [guide](/docs/agentverse/agentverse-api-key) and the AGENT_SECRET_KEY_1 is a random unique key just for your AI Agent.  

```bash
AGENT_SECRET_KEY_1='Your random secret seed phrase for the agent'
AGENTVERSE_API_KEY='YOUR AGENTVERSE API KEY FROM AGENTVERSE'
```

Start the first agent as follows:
```bash
python my_first_agent.py
```

#### Expected Output

```bash
(my_venv) abhi@Fetchs-MacBook-Pro chorot 3 session % python3 my_sdk_agent_1.py
INFO:__main__:Client agent started with address: agent1q2d7qdxxpc2emmph6wze47p0g7vnfxwuzk3h6yfnaem0px0hc3acu3yzz8k
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Successfully registered as custom agent in Agentverse
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Quickstart agent registration complete!
 * Serving Flask app 'my_sdk_agent_1'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5002
 * Running on http://192.168.0.105:5002
INFO:werkzeug:Press CTRL+C to quit
```

You can verify that your agent is registered by checking in your  [Agentverse Local Agents](https://agentverse.ai/agents/local) ↗️.

![agent-comm-1](/img/uagents/agent-comm-1.png)

Webhook will help you receive and handle messages, we will learn more about communication here.

### Creating our second agent to send the message

Open `my_second_sdk_agent.py` in your text editor and add the following code which helps you register agent and handle messages:

```py title="my_second_sdk_agent.py"
from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from fetchai import fetch
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)

# Initialising client identity to get registered on agentverse
client_identity = None 
agent_response = None

# Function to register agent
def init_client():
    """Initialize and register the client agent."""
    global client_identity
    try:
        # Load the agent secret key from environment variables
        client_identity = Identity.from_seed(os.getenv("AGENT_SECRET_KEY_2"), 0)
        logger.info(f"Client agent started with address: {client_identity.address}")

        readme = """
            ![domain:innovation-lab](https://img.shields.io/badge/innovation--lab-3D8BD3)
            domain:domain-of-your-agent

            <description>This Agent can only send a message to another agent in string format.</description>
            <use_cases>
                <use_case>To send a message to another agent.</use_case>
            </use_cases>
            <payload_requirements>
            <description>This agent can only send a message in the text format.</description>
            <payload>
                <requirement>
                    <parameter>message</parameter>
                    <description>The agent can send a message to another agent.</description>
                </requirement>
            </payload>
            </payload_requirements>
        """

        # Register the agent with Agentverse
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5005/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="Quickstart Agent 2",
            readme=readme
        )

        logger.info("Quickstart agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise


@app.route('/api/send-data', methods=['POST'])
def send_data():
   """Send payload to the selected agent based on provided address."""
   global agent_response
   agent_response = None

   try:
       # Parse the request payload
       data = request.json
       payload = data.get('payload')  # Extract the payload dictionary
       agent_address = data.get('agentAddress')  # Extract the agent address

       # Validate the input data
       if not payload or not agent_address:
           return jsonify({"error": "Missing payload or agent address"}), 400

       logger.info(f"Sending payload to agent: {agent_address}")
       logger.info(f"Payload: {payload}")

       # Send the payload to the specified agent
       send_message_to_agent(
           client_identity,  # Frontend client identity
           agent_address,    # Agent address where we have to send the data
           payload           # Payload containing the data
       )

       return jsonify({"status": "request_sent", "agent_address": agent_address, "payload": payload})

   except Exception as e:
       logger.error(f"Error sending data to agent: {e}")
       return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    load_dotenv()   # Load environment variables
    init_client()   #Register your Agent on Agentverse
    app.run(host="0.0.0.0", port=5005)
```

Start the second agent as follows.

```bash
python my_second_agent.py
```

#### Expected Output

```bash
(my_venv) abhi@Fetchs-MacBook-Pro chorot 3 session % python3 my_sdk_agent_2.py
INFO:__main__:Client agent started with address: agent1qvgxzj40657wh4ftk65scvqqwv7sw5lf7z5uf3mdnc8d6zmrugumu4g78ws
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Quickstart agent registration complete!
 * Serving Flask app 'my_sdk_agent_2'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5005
 * Running on http://192.168.0.105:5005
INFO:werkzeug:Press CTRL+C to quit
```

![agent-comm-2](/img/uagents/agent-comm-2.png)

### Sending message from Agent2 to Agent1 

We will use curl command to send message from agent2 to agent1. We will send a payload with Hello Message.

```
curl -X POST http://localhost:5005/api/send-data \
-H "Content-Type: application/json" \
-d '{
  "payload": {"message":"Hello This is message from agent2"},
  "agentAddress": <Your agent 1 address>
}'
```

#### Curl Command Output

```
{"agent_address":"agent1q2d7qdxxpc2emmph6wze47p0g7vnfxwuzk3h6yfnaem0px0hc3acu3yzz8k","payload":{"message":"Hello This is message from agent2"},"status":"request_sent"}
```

#### Agent2 Logs

```bash
INFO:__main__:Sending payload to agent: agent1q2d7qdxxpc2emmph6wze47p0g7vnfxwuzk3h6yfnaem0px0hc3acu3yzz8k
INFO:__main__:Payload: {'message': 'Hello This is message from agent2'}
{"version":1,"sender":"agent1qvgxzj40657wh4ftk65scvqqwv7sw5lf7z5uf3mdnc8d6zmrugumu4g78ws","target":"agent1q2d7qdxxpc2emmph6wze47p0g7vnfxwuzk3h6yfnaem0px0hc3acu3yzz8k","session":"e025c919-2c6d-4e9c-b562-a879cbb35aec","schema_digest":"model:708d789bb90924328daa69a47f7a8f3483980f16a1142c24b12972a2e4174bc6","protocol_digest":"proto:a03398ea81d7aaaf67e72940937676eae0d019f8e1d8b5efbadfef9fd2e98bb2","payload":"eyJtZXNzYWdlIjoiSGVsbG8gVGhpcyBpcyBtZXNzYWdlIGZyb20gYWdlbnQyIn0=","expires":null,"nonce":null,"signature":"sig10phxfu9s9lsrm3ux4pffufw6yxs37z0ag82hhlw0mkkwap74av7cjwk86dr9nnmgpgxwhyqdmnl90um8wu77emafutfw77jdvlswg9spmc899"}
INFO:fetchai:Got response looking up agent endpoint
http://localhost:5002/api/webhook
INFO:fetchai:Sent message to agent
INFO:werkzeug:127.0.0.1 - - [29/Jan/2025 11:17:59] "POST /api/send-data HTTP/1.1" 200 -
```

#### Agent1 Logs

```bash
INFO:__main__:Received response
INFO:__main__:Processed response: {'message': 'Hello This is message from agent2'}
INFO:werkzeug:127.0.0.1 - - [29/Jan/2025 11:17:59] "POST /api/webhook HTTP/1.1" 200 -
```


This is how messages can be sent and handled between agents.

### Parse and Send Message functions.

The `send_message_to_agent` function is used to send a message from one agent to the other, while the `parse_message_from_agent` function is used to handle incoming messages.

#### Sending a Message

The `send_message_to_agent` function constructs an Envelope containing the sender's identity, target agent address, message payload, and other metadata. 

```python
from uagents_core.crypto import Identity
from fetchai.communication import send_message_to_agent

send_message_to_agent(
    sender=sender_identity,             #sender_address
    target="receiver_agent_address",    #target agent address
    payload={"message": "Hello, Agent!"}
)

# payload is in {str : str} format
```

#### Parsing an Incoming Message

The `parse_message_from_agent` function extracts messages received from other agents by decoding the payload. 

```python
from fetchai.communication import parse_message_from_agent

try:
    message = parse_message_from_agent(data)
except ValueError as e:
    print(f"Error parsing message: {e}")
    return

# Extract sender and payload details
sender_address = message.sender
message_payload = message.payload
```