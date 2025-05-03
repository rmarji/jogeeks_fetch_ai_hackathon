---
id: langgraph-adapter-example
title: LangGraph Adapter Example
---

# LangGraph Adapter for uAgents

This example demonstrates how to integrate a **LangGraph agent** with the **uAgents ecosystem** using the uAgents Adapter package. LangGraph provides powerful orchestration capabilities for LLM applications through directed graphs.

## Overview

The LangGraph adapter allows you to:

- Wrap LangGraph agents as uAgents for seamless communication
- Enable LangGraph agents to participate in the Agentverse ecosystem
- Leverage advanced orchestration for complex reasoning while maintaining uAgent compatibility

## Example Implementation

```python
import os
import time
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import chat_agent_executor
from langchain_core.messages import HumanMessage

from uagents_adapter.langchain import UAgentRegisterTool, cleanup_uagent

# Load environment variables
load_dotenv()

# Set your API keys - for production, use environment variables instead of hardcoding
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

# Get API token for Agentverse
API_TOKEN = os.environ["AGENTVERSE_API_KEY"]

if not API_TOKEN:
    raise ValueError("Please set AGENTVERSE_API_KEY environment variable")

# Set up tools and LLM
tools = [TavilySearchResults(max_results=3)]
model = ChatOpenAI(temperature=0)

# LangGraph-based executor
app = chat_agent_executor.create_tool_calling_executor(model, tools)

# Wrap LangGraph agent into a function for UAgent
def langgraph_agent_func(query):
    # Handle input if it's a dict with 'input' key
    if isinstance(query, dict) and 'input' in query:
        query = query['input']
    
    messages = {"messages": [HumanMessage(content=query)]}
    final = None
    for output in app.stream(messages):
        final = list(output.values())[0]  # Get latest
    return final["messages"][-1].content if final else "No response"

# Register the LangGraph agent via uAgent
tool = UAgentRegisterTool()
agent_info = tool.invoke(
    {
        "agent_obj": langgraph_agent_func,
        "name": "langgraph_tavily_agent",
        "port": 8080,
        "description": "A LangGraph-based Tavily-powered search agent",
        "api_token": API_TOKEN,
        "mailbox": True
    }
)

print(f"✅ Registered LangGraph agent: {agent_info}")

# Keep the agent alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🛑 Shutting down LangGraph agent...")
    cleanup_uagent("langgraph_tavily_agent")
    print("✅ Agent stopped.")
```

## Key Components

1. **LangGraph Setup**:
   - Creates a tool-calling executor using LangGraph's prebuilt components
   - Configures Tavily search as the tool for retrieving information
   - Uses OpenAI's ChatGPT for LLM capabilities

2. **Function Wrapper**:
   - Wraps the LangGraph app in a function that accepts queries
   - Handles input format conversion
   - Processes streaming output from LangGraph

3. **uAgent Registration**:
   - Uses UAgentRegisterTool to register the LangGraph function as a uAgent
   - Configures a port, description, and mailbox for persistence
   - Generates a unique address for agent communication

## Sample requirements.txt

Here's a sample `requirements.txt` file you can use for this example:

```
uagents==0.22.3
uagents-adapter==0.1.0
langchain-openai==0.3.14
langchain-community==0.3.21
langgraph==0.3.31
dotenv==1.0.1
```

## Interacting with the Agent

You can interact with this LangGraph agent through any uAgent using the chat protocol. Here's a client implementation:

```python
from datetime import datetime
from uuid import uuid4
from uagents import Agent, Protocol, Context

#import the necessary components from the chat protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
# Initialise agent2
agent2 = Agent(name="client_agent",
               port = 8082,
               mailbox=True,
               seed="client agent testing seed"
               )

# Initialize the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)

langgraph_agent_address = "agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t" # Update with your Langgraph Agent's address

# Startup Handler - Print agent details
@agent2.on_event("startup")
async def startup_handler(ctx: Context):
    # Print agent details
    ctx.logger.info(f"My name is {ctx.agent.name} and my address is {ctx.agent.address}")

    # Send initial message to agent2
    initial_message = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text="I want to send query to tavily agent that Give me a list of latest agentic AI trends")]
    )
    await ctx.send(langgraph_agent_address, initial_message)

# Message Handler - Process received messages and send acknowledgements
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    for item in msg.content:
        if isinstance(item, TextContent):
            # Log received message
            ctx.logger.info(f"Received message from {sender}: {item.text}")
            
            # Send acknowledgment
            ack = ChatAcknowledgement(
                timestamp=datetime.utcnow(),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)
            

# Acknowledgement Handler - Process received acknowledgements
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")

# Include the protocol in the agent to enable the chat functionality
# This allows the agent to send/receive messages and handle acknowledgements using the chat protocol
agent2.include(chat_proto, publish_manifest=True)

if __name__ == '__main__':
    agent2.run()
```

## Why Use LangGraph with uAgents?

LangGraph offers several advantages when combined with uAgents:

- **Advanced Orchestration**: Create complex reasoning flows using directed graphs
- **State Management**: Handle complex multi-turn conversations with state persistence
- **Tool Integration**: Easily connect to external services and APIs
- **Debugging Capabilities**: Inspect and debug agent reasoning processes

By wrapping LangGraph with the uAgents adapter, you get the best of both worlds: sophisticated LLM orchestration with the decentralized communication capabilities of uAgents.

## Getting Started

1. Clone the [uAgents Adapter Examples repository](https://github.com/fetchai/uagents-adapter-examples)

2. Install required packages:
   ```bash
   pip install uagents>=0.22.3 uagents-adapter>=0.1.0 langchain-openai>=0.3.14 langchain-community>=0.3.21 langgraph>=0.3.31  dotenv>=0.9.9
   ```

   Or use the provided requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```
   OPENAI_API_KEY=your_openai_key
   TAVILY_API_KEY=your_tavily_key  
   AGENTVERSE_API_KEY=your_agentverse_key
   ```

4. Run the LangGraph agent:
   ```bash
   python langgraph_adapter.py
   ```

5. In a separate terminal, run the client agent:
   ```bash
   python client_agent.py
   ```



## Expected Outputs

When running the examples, you should expect to see outputs similar to these:

### LangGraph Agent

When running the LangGraph agent:

```
(venv) Fetchs-MacBook-Pro test examples % python3 langgraph_tavily.py 
INFO:     [langgraph_tavily_agent]: Starting agent with address: agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t
INFO:     [langgraph_tavily_agent]: Agent 'langgraph_tavily_agent' started with address: agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t
INFO:     [langgraph_tavily_agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8080&address=agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t
INFO:     [langgraph_tavily_agent]: Starting server on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     [langgraph_tavily_agent]: Starting mailbox client for https://agentverse.ai
INFO:     [langgraph_tavily_agent]: Mailbox access token acquired
INFO:     [langgraph_tavily_agent]: Received structured output response from agent1qtlpfshtlcxekgrfcpmv7m9zpajuwu7d5jfyachvpa4u3dkt6k0uwwp2lct: Hello, Tavily Agent. Could you please provide a list of the latest trends in agentic AI? I am interested in understanding how agent-based artificial intelligence is evolving and what innovations or developments stand out in this field. Thank you!
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
✅ Registered LangGraph agent: Created uAgent 'langgraph_tavily_agent' with address agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t on port 8080
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:     [langgraph_tavily_agent]: Got a message from agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [langgraph_tavily_agent]: Got a text message from agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49: I want to send query to tavily agent that Give me a list of latest agentic AI trends
INFO:     [langgraph_tavily_agent]: Sending structured output prompt to {'title': 'QueryMessage', 'type': 'object', 'properties': {'query': {'title': 'Query', 'type': 'string'}}, 'required': ['query']}
INFO:     [langgraph_tavily_agent]: Sent structured output prompt to agent1qtlpfshtlcxekgrfcpmv7m9zpajuwu7d5jfyachvpa4u3dkt6k0uwwp2lct
INFO:     [langgraph_tavily_agent]: Got an acknowledgement from agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49 for 451f41aa-be41-471f-bddc-276caffb7d94
Connecting agent 'langgraph_tavily_agent' to Agentverse...
INFO:     [mailbox]: Successfully registered as mailbox agent in Agentverse
Successfully connected agent 'langgraph_tavily_agent' to Agentverse
Updating agent 'langgraph_tavily_agent' README on Agentverse...
Successfully updated agent 'langgraph_tavily_agent' README on Agentverse
INFO:     [langgraph_tavily_agent]: Received structured output response from agent1qtlpfshtlcxekgrfcpmv7m9zpajuwu7d5jfyachvpa4u3dkt6k0uwwp2lct: Subject: Request for Information on Latest Agentic AI Trends

Hi Tavily Agent,

I hope this message finds you well. I am reaching out to inquire about the latest trends in agentic AI technology. As this area is rapidly evolving, I am keen to stay updated on the most recent developments and innovations.

Could you please provide me with a comprehensive list of the latest trends in agentic AI? I'm particularly interested in understanding how these trends might impact various industries and potential future applications.

Thank you for your assistance. I look forward to your response.
---
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
```

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/adapters/langgraph.png" alt="langgraph-adapter" style={{ width: '100%', maxWidth: '1000px' }} />
</div>

### Client Agent

When running the client agent:

```
(venv) Fetchs-MacBook-Pro test examples % python3 client_agent.py
INFO:     [client_agent]: Starting agent with address: agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [client_agent]: My name is client_agent and my address is agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [client_agent]: Agent inspector available at https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8082&address=agent1qwwng5d939vyaa6d2trnllyltgrndtfd6z44h8ey8a56hf4dcatsytgzm49
INFO:     [client_agent]: Starting server on http://0.0.0.0:8082 (Press CTRL+C to quit)
INFO:     [client_agent]: Starting mailbox client for https://agentverse.ai
INFO:     [uagents.registration]: Registration on Almanac API successful
INFO:     [uagents.registration]: Almanac contract registration is up to date!
INFO:     [client_agent]: Manifest published successfully: AgentChatProtocol
INFO:     [client_agent]: Mailbox access token acquired
INFO:     [client_agent]: Received message from agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t: Here are some of the latest trends in agentic AI:

1. **The Next Frontier: The Rise of Agentic AI - Adams Street Partners**
   - **Link:** [The Next Frontier: The Rise of Agentic AI - Adams Street Partners](https://www.adamsstreetpartners.com/insights/the-next-frontier-the-rise-of-agentic-ai/)
   - **Summary:** Several converging trends have set the stage for agentic AI, including advances in Large Language Models, improved reasoning, planning, and multistep processes.

2. **7 Agentic AI Trends To Watch for 2025 - ServiceNow**
   - **Link:** [7 Agentic AI Trends To Watch for 2025 - ServiceNow](https://www.servicenow.com/products/ai-agents/agentic-ai-trends.html)
   - **Summary:** Explore the latest agentic AI trends shaping the future of work, from hyperautomation to decision intelligence, and how it can transform businesses.

3. **Agentic AI: Three themes to watch for 2025 - Constellation Research**
   - **Link:** [Agentic AI: Three themes to watch for 2025 - Constellation Research](https://www.constellationr.com/blog-news/insights/agentic-ai-three-themes-watch-2025)
   - **Summary:** This article discusses three themes to watch in agentic AI for 2025, including horizontal approaches vs. platform-specific strategies and the proliferation of agentic AI launches by various vendors.

These sources provide insights into the evolving landscape of agentic AI and the key trends that are shaping the future of this field.
INFO:     [client_agent]: Received acknowledgement from agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t for message: 1cdda4bd-4597-42a9-b6f1-13c6ca67a0ea
INFO:     [client_agent]: Received message from agent1q0zyxrneyaury3f5c7aj67hfa5w65cykzplxkst5f5mnyf4y3em3kplxn4t: ### Latest Trends in Agentic AI Technology:

1. **[7 Agentic AI Trends To Watch for 2025 - ServiceNow](https://www.servicenow.com/products/ai-agents/agentic-ai-trends.html)**
   - Explore the latest agentic AI trends shaping the future of work, from hyperautomation to decision intelligence, and how it can transform your business.

2. **[Agentic AI: Three themes to watch for 2025 - Constellation Research](https://www.constellationr.com/blog-news/insights/agentic-ai-three-themes-watch-2025)**
   - Three themes to watch in agentic AI, including horizontal approaches vs. platform-specific trends and the proliferation of agentic AI platforms across various vendors.

3. **[The Top Customer Service Trends and Technologies for 2025](https://www.destinationcrm.com/Articles/Editorial/Magazine-Features/The-Top-Customer-Service-Trends-and-Technologies-for-2025-Agentic-AI-Is-Poised-to-Remake-Self-Service-168751.aspx)**
   - Agentic AI is poised to remake self-service in customer service, with predictions that by 2030, 50% of service requests will be initiated by machine customers powered by agentic AI systems.

4. **[Future Trends in Agentic AI Development: What's Next for Intelligent Automation](https://www.imbrace.co/future-trends-in-agentic-ai-development-whats-next-for-intelligent-automation/)**
   - Trends include providing clear insights into decision-making, ensuring alignment with ethical guidelines, expanded applications across industries like logistics and healthcare, and the integration of Explainable AI (XAI).

5. **[5 Reasons Why Agentic AI Will Transform Industries by 2030](https://hyperight.com/5-reasons-why-agentic-ai-will-transform-industries-by-2030/)**
   - Agentic AI is expected to enhance productivity and efficiency, reshape industries by 2030, and be incorporated into 33% of enterprise software applications by 2028.

6. **[Agentic AI Trends - What to expect in the near future - Atera](https://www.atera.com/blog/agentic-ai-trends/)**
   - Agentic AI is set to revolutionize customer service, with researchers predicting a significant impact on customer service operations.

These trends highlight the advancements and potential impacts of agentic AI technology across various industries and applications.
```

Try different queries to see how the LangGraph agent processes them and returns search-enhanced responses through the uAgents ecosystem! 