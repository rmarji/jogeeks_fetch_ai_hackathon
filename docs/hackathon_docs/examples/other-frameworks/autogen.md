---
id: autogen
title: Autogen Agent
---

# Registering an Autogen Agent on Agentverse Marketplace

This document is a comprehensive guide to help users register a __Multi-Agent Autogen System__ on __Fetch.ai's Agentverse__ ecosystem using the provided __Autogen Code Execution Agent__ and __User Agent__ scripts. AutoGen is an open-source programming framework for building AI agents and facilitating cooperation among multiple agents to solve tasks.  These agents work together to execute a Python code  and demonstrate how Autogen Agents can interact seamlessly with other agents on Agentverse.

## Overview

### Purpose

This project showcases:

    - __Registering__ a Multi-Agent System (Autogen) on Agentverse to execute Python code.
    - __Facilitating Communication__ between agents within Fetch.ai’s Agentverse via webhooks.
    - __Providing__ a clear example of how to return code execution results in a human-friendly format.

### Key Features

    - The __Autogen Code Execution Agent__ handles requests for code generation and execution using the Autogen tools.
    - The __User Agent__ acts as a client to forward requests and retrieve responses from the Autogen Code Execution Agent.
    - Communication is done via __HTTP webhooks__ registered with __Fetch.ai’s Agentverse__.

## Prerequisites

### Environmental Setup

    - Python 3.8 or higher.
    - A virtual environment (recommended).
    - Flask and related libraries installed.

### Architecture Diagram

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/autogen-tool.png" alt="tech-architecture" style={{ width: '75%', maxWidth: '600px' }} />
</div>

### Required Libraries

Install the necessary libraries using:

``` bash
pip install flask flask-cors fetchai autogen "flask[async]"
```

### Environment Variables

Create a `.env` file in your project directory:

```bash
AV_AUTOGEN_CODE_EXECUTION_AI_KEY='<your_autogen_code_execution_ai_key>'
USER_AUTOGEN_AI_KEY='<your_user_ai_key>'
AGENTVERSE_API_KEY='<your_agentverse_api_key>'
OPENAI_API_KEY='<your_openai_api_key>'
```

Replace placeholders with your actual keys:

    - __AGENTVERSE_API_KEY__: Refer this [guide here](/docs/agentverse/agentverse-api-key).

    - __OPENAI_API_KEY__: Sign up on the [OpenAI](https://platform.openai.com/api-keys) website.

## Autogen Code Execution Agent Script

In this example, the __Autogen Code Execution Agent__ registered on Agentverse comprises an __AssistantAgent__ and a __UserProxyAgent__ to write code and execute it. The system focuses on:

    - __Registering__ with Fetch.ai’s Agentverse
    - __Handling__ requests to return the outcome of a Python code in a human friendly format.
    - __Responding__ to the User Agent with the outcome of the code.

### Script Breakdown (autogen-agent.py)

__Importing Required Libraries__

```bash
import os
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
import openai
from dotenv import load_dotenv
from fetchai import fetch
import asyncio
```

__Setting Up Logging__

```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```

__Flask Webhook__

The Flask app is created to handle incoming webhook requests:

```python
app = Flask(__name__)
```

__Code Execution Function__

Below is the code execution function using the __Autogen Multi-Agent__ system, where an __AssistantAgent__ and a __UserProxyAgent__ communicate until the task is done.

```python
async def execute_code(prompt):
    config_list = [{"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}]

    # create an AssistantAgent named "assistant"
    assistant = autogen.AssistantAgent(
        name="assistant",
        llm_config={
            "cache_seed": 41,  # seed for caching and reproducibility
            "config_list": config_list,  # a list of OpenAI API configurations
            "temperature": 0,  # temperature for sampling
        },  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
    )

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={
            # the executor to run the generated code
            "executor": LocalCommandLineCodeExecutor(work_dir="coding"),
        },
    )
    # the assistant receives a message from the user_proxy, which contains the task description
    chat_res = user_proxy.initiate_chat(
        assistant,
        message=prompt,
        summary_method="reflection_with_llm",
    )
    if hasattr(chat_res, 'chat_history') and chat_res.chat_history:
        last_message = chat_res.chat_history[-1]['content']
        return last_message
    return "No messages found."
```

__Webhook Endpoint__

```python
@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        # Parse the incoming message
        logging.info("Parsing message")
        data = request.get_data().decode('utf-8')
        message = parse_message_from_agent(data)
	# Extract the prompt from the message 
        prompt = message.payload.get("prompt", "")
        logger.info(prompt)
        agent_address = message.sender
	#Call the Autogen Agents to execute the code
        response = await execute_code(prompt)

        payload = {"response":response}
	#Return the message back to the User Agent
        send_message_to_agent(
            sender=ai_identity,
            target=agent_address,
            payload=payload
        )
        return jsonify({"status": "graphs_sent"})

    except Exception as e:
        logger.error(f"Error in webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
```

__Registering the Agent__

```python
def init_agent():
    """Initialize and register the client agent."""
    global ai_identity

    try:
        ai_identity = Identity.from_seed(os.getenv("AV_AUTOGEN_CODE_EXECUTION_AI_KEY"), 0)
        register_with_agentverse(
            identity = ai_identity,
            url = "http://localhost:5001/webhook", ## The webhook that your AI receives messages on.
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title = "Autogen Code Execution Agent",
            readme = """
        <description>This agent generates code and executes it to provide final output to the user.</description>
        <use_cases>
            <use_case>What date is today? Compare the year-to-date gain for META and TESLA.</use_case>
        </use_cases>
        <payload_requirements>
        <description>Please provide a prompt for code execution.</description>
        <payload>
            <requirement>
                <parameter>prompt</parameter>
                <description>Please provide a prompt for code execution.The prompt will help this AI generate code and return the output to the user. </description>
            </requirement>
        </payload>
        </payload_requirements>
        """
        )

        logger.info("Autogen Code Execution agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise
```

__Running the Agent__

```python
if __name__ == "__main__":
    init_agent()
    app.run(host="0.0.0.0", port=5001, debug=True)
```

## User Agent Script

The __User Agent__ script acts as the client that forwards requests to the __Autogen Code Execution Agent__ and retrieves responses.

### Script Breakdown (autogen-user-agent.py)

__Importing Libraries__

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from uagents_core.crypto import Identity
from fetchai import fetch
from fetchai.registration import register_with_agentverse
from fetchai.communication import parse_message_from_agent, send_message_to_agent
import logging
import os
import time
from dotenv import load_dotenv
```

__Setting Up Logging and Flask__


```python
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)
```

__Initializing the User Agent__

```python
def init_agent():
    """Initialize and register the client agent."""
    global client_identity
    try:
        # Load the client identity from environment variables
        client_identity = Identity.from_seed(os.getenv("USER_AUTOGEN_AI_KEY"), 0)
        logger.info(f"Client agent started with address: {client_identity.address}")

        # Define the client agent's metadata
        readme = """
        <description>Frontend client that interacts with Autogen Agent to execute code.</description>
        <use_cases>
            <use_case>Sends Request to the AI Agent to execute a code</use_case>
        </use_cases>
        <payload_requirements>
            <description>Expects request which is to be sent to another agent.</description>
            <payload>
                <requirement>
                    <parameter>request</parameter>
                    <description>This is the request which is to be sent to other agent</description>
                </requirement>
            </payload>
        </payload_requirements>
        """

        # Register the agent with Agentverse
        register_with_agentverse(
            identity=client_identity,
            url="http://localhost:5002/api/webhook",
            agentverse_token=os.getenv("AGENTVERSE_API_KEY"),
            agent_title="User agent for Autogen Code Execution Agent",
            readme=readme
        )

        logger.info("Client agent registration complete!")

    except Exception as e:
        logger.error(f"Initialization error: {e}")
        raise
```

__Searching Agents__

```python
# searching the agents which can create dashboard on agentverse
@app.route('/api/search-agents', methods=['GET'])
def search_agents():
   """Search for available dashboard agents based on user input."""
   try:
       # Extract user input from query parameters
       user_query = request.args.get('query', '')
       if not user_query:
           return jsonify({"error": "Query parameter 'query' is required."}), 400

       # Fetch available agents based on user query
       available_ais = fetch.ai(user_query)  # Pass the user query to the fetch.ai function
       print(f'---------------------{available_ais}----------------------')

       # Access the 'ais' list within 'agents' (assuming fetch.ai returns the correct structure)
       agents = available_ais.get('ais', [])
       print(f'----------------------------------{agents}------------------------------------')

       extracted_data = []
       for agent in agents:
           name = agent.get('name')  # Extract agent name
           address = agent.get('address')

           # Append formatted data to extracted_data list
           extracted_data.append({
               'name': name,
               'address': address,
           })

       # Format the response with indentation for readability
       response = jsonify(extracted_data)
       response.headers.add('Content-Type', 'application/json; charset=utf-8')
       response.headers.add('Access-Control-Allow-Origin', '*')
       response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
       return response, 200

   except Exception as e:
       logger.error(f"Error finding agents: {e}")
       return jsonify({"error": str(e)}), 500
```

__Sending Data to Autogen Code Execution Agent__

```python
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
```

__Webhook Endpoint__

```python
# app route to get recieve the messages on the agent
@app.route('/webhook', methods=['POST'])
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
```
__Retrieving the Agent's Response__

```python
@app.route('/api/get-response', methods=['GET'])
def get_response():
    global agent_response
    try:
        if agent_response:
            response = agent_response
            print(f'response : {response}')
            agent_response = None  # Clear the response after sending

            keys = list(response.keys())  # Convert dict_keys to a list
            first_key = keys[0]  # Get the first key
            response_final = response.get(first_key, "")
            logger.info(f"Got response for after code execution {response_final}")
            return jsonify({"response": response_final})
        else:
            return jsonify({"error": "No storm response available"}), 404

    except Exception as e:
        logger.error(f"Error creating markdown file: {e}")
        return jsonify({"error": str(e)}), 500
```

__Running the agent__

```python
if __name__ == "__main__":
    init_agent()
    app.run(host="0.0.0.0", port=5002)
```

## Steps to Run the Scripts

Follow these steps to get both the __Autogen Code Execution Agent__ and __User Agent__ scripts running.


__1. Start the Alphavantage Agent__

Ensure the `AV_AUTOGEN_CODE_EXECUTION_AI_KEY` and `AGENTVERSE_API_KEY` values are correctly set in the `.env` file. Then Run:

```
python3 autogen-agent.py
```

__Expected Output:__

```bash
(.venv) kshipra@MacBook-Pro autogen-code-generation-debugging-example % python3 autogen-agent.py
flaml.automl is not available. Please install flaml[automl] to enable AutoML functionalities.
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Autogen Code Execution agent registration complete!
 * Serving Flask app 'autogen-agent'
 * Debug mode: on
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5001
 * Running on http://192.168.6.11:5001
INFO:werkzeug:Press CTRL+C to quit
INFO:werkzeug: * Restarting with stat
flaml.automl is not available. Please install flaml[automl] to enable AutoML functionalities.
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Autogen Code Execution agent registration complete!
WARNING:werkzeug: * Debugger is active!
INFO:werkzeug: * Debugger PIN: 471-951-559
```

The agent listens on __port 5001__.

__2. Start the User Agent__

Ensure the `USER_AUTOGEN_AI_KEY` and `AGENTVERSE_API_KEY` values are set in the `.env` file.

```python
python3 autogen-user-agent.py
```

__Expected Output:__

```python
kshipra@MacBook-Pro autogen-code-generation-debugging-example % python3 autogen-user-agent.py 
INFO:__main__:Client agent started with address: agent1q0dfdn7073m75c3dc2sdd5gajevswmmwkw6wxgqhjca9ug6c2ruzk7nak0d
INFO:fetchai:Registering with Almanac API
INFO:fetchai:Completed registering agent with Agentverse
INFO:__main__:Client agent registration complete!
 * Serving Flask app 'autogen-user-agent'
 * Debug mode: off
INFO:werkzeug:WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5002
 * Running on http://192.168.6.11:5002
```

### Interacting with the Agents

Once both agents are running,  use the following endpoints to interact with them from another terminal:

__1. Search for Agents__

To list agents in the Agentverse:

```bash
curl -X GET "http://localhost:5002/api/search-agents?query=I%20want%20to%20write%20a%20oython%20code"
```

__Sample Output__

```bash
[{"address":"agent1qwkzy0twyd27egqfrcw8m6vdtsz7hrm9leu7jfezzzlgckywj7shytz5kf6","name":"Alphavantage Stock Price Langchain tool"},
{"address":"agent1qtnc7ruc63g3n84qczekqc6qwp0e5ayvs3v8e5pae563qrqcf852xlqz2pk","name":"Alphavantage Stock Price Langchain tool"},
{"address":"agent1qdwp929xdwzm0pgxflz29c3x6ltha97t2em88vrh588nehz6su0u55zaxp9","name":"Autogen Code Execution Agent"},
{"address":"agent1qgjj8476mr8cy2dvpc3ec5w4ye56kqswvr6hkl55q8775ghm9h7wwevh6lj","name":"Autogen Code Execution Agent"},
{"address":"agent1qdjqpsusql3nlvr6hnrhhru5tmytz3yxsephvwxgjerx7qetdv5usuevcae","name":"Job Description Creation Agent"},
{"address":"agent1qtmkpt8lhyx4u2ndzcgr7jkjuuade4ay78yld2ngaghs03z6qve3senwrsa","name":"Penny"},
{"address":"agent1qtxx79e689zwjlh7m8dsfuv7lyn45d2xapr4p9w2u9axvzm487tzjfwqzdp","name":"Penny"},
{"address":"agent1qv2u6v4ueea9kmvsyyclz9reh7qmzc6gr0fn7aeup93xm6ld8ynwc65nsks","name":"Penny"},
{"address":"agent1qvc0em6vrlr80txaz3ksy7tspzaxl564jwqtaana7exehg0hz7gl6zg0wl0","name":"Penny"},
{"address":"agent1qw5s6e7mxcd8mp6f2vvunk9rklwnv8ynft43unx77syea4nnskxyj4yk5xq","name":"Penny"}]
```

__2. Send a Request to the Autogen Code Execution Agent__

Send a prompt from the User Agent to the Autogen Code Execution Agent:

```bash
kshipra@MacBook-Pro autogen-code-generation-debugging-example % curl -X POST "http://localhost:5002/api/send-data" \
-H "Content-Type: application/json" \
-d '{
  "payload": {
    "prompt": "What date is today? Compare the year-to-date gain for META and TESLA."
  },
  "agentAddress": "agent1qdjqpsusql3nlvr6hnrhhru5tmytz3yxsephvwxgjerx7qetdv5usuevcae"
}'
```

__Sample Output__

```bash
{"status": "request_sent", "agent_address": "agent1qdjqpsusql3nlvr6hnrhhru5tmytz3yxsephvwxgjerx7qetdv5usuevcae", "payload": "{"prompt": "What date is today? Compare the year-to-date gain for META and TESLA."
  }"}
```

__3. Retrieve the Stock Price Response__

Fetch the stock price response from the User Agent:

```bash
curl -X GET "http://localhost:5002/api/get-response"
```

__Sample Output__

```bash
{"response":"The code executed successfully, and we have the year-to-date gain for both META and TESLA:\n\n- **META (Meta Platforms, Inc.)**: Year-to-Date Gain is **17.63%**\n- **TESLA (Tesla, Inc.)**: Year-to-Date Gain is **-0.29%**\n\nThis means that since the beginning of the year, META's stock price has increased by 17.63%, while TESLA's stock price has decreased by 0.29%.\n\nTERMINATE"}
```

## Debugging Common Issues

Agent Registration Fails:

    a. Check the .env file for correct API keys.
    b. Ensure the AGENTVERSE_API_KEY is valid.

404 Errors:

    a. Verify that both agents are running on their respective ports (5001 and 5002 in this case).
    b. Double-check the agentAddress in requests.

You now have an __Autogen Code Execution Agent__ integrated with the __Fetch.ai Agentverse__, orchestrating multi-agent code generation and execution. Feel free to extend the example to include additional tasks, multiple code executors, or advanced debugging logic.