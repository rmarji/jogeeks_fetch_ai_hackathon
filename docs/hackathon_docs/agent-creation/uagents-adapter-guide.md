---
id: uagents-adapter-guide
title: uAgents Adapters
---

# uAgents Adapters: Connecting AI Framework Ecosystems

uAgents Adapters provide a bridge between the uAgents ecosystem and various agentic frameworks, enabling seamless communication between different AI agent architectures.

## Why Use Adapters?

AI development landscapes often involve multiple frameworks and technologies, each with their own strengths:

- **LangChain**: Powerful for composing LLMs with tools and chains
- **LangGraph**: Excellent for complex orchestration and stateful workflows
- **CrewAI**: Specialized for multi-agent collaborative systems

The uAgents Adapter package allows you to leverage these specialized frameworks while still benefiting from the uAgents ecosystem for communication, discovery, and deployment.

## Available Adapters

The uAgents Adapter package currently supports several major AI frameworks:

### 1. LangChain Adapter

Connect LangChain agents, chains, and tools to the uAgents ecosystem.

```python
from uagents_adapter.langchain import UAgentRegisterTool

# Register a LangChain agent as a uAgent
tool = UAgentRegisterTool()
agent_info = tool.invoke({
    "agent_obj": langchain_agent,
    "name": "my_langchain_agent",
    "port": 8000,
    "description": "A LangChain agent powered by GPT-4",
    "api_token": AGENTVERSE_API_KEY
})
```

### 2. LangGraph Adapter

Integrate LangGraph's powerful orchestration with uAgents.

```python
from uagents_adapter.langgraph import UAgentRegisterTool

# Wrap LangGraph agent function for uAgent integration
def langgraph_agent_func(query):
    # Process with LangGraph
    result = langgraph_app.invoke(query)
    return result

# Register the LangGraph function as a uAgent
tool = UAgentRegisterTool()
agent_info = tool.invoke({
    "agent_obj": langgraph_agent_func,
    "name": "my_langgraph_agent",
    "port": 8080,
    "description": "A LangGraph orchestration agent",
    "api_token": AGENTVERSE_API_KEY
})
```

### 3. CrewAI Adapter

Expose CrewAI's collaborative agent teams as uAgents.

```python
from uagents_adapter.crewai import UAgentRegisterTool

# Create a function to handle CrewAI operations
def crew_handler(query):
    # Process with CrewAI
    result = my_crew.kickoff(inputs={"query": query})
    return result

# Register the CrewAI function as a uAgent
tool = UAgentRegisterTool()
agent_info = tool.invoke({
    "agent_obj": crew_handler,
    "name": "my_crew_agent",
    "port": 8081,
    "description": "A CrewAI team of specialized agents",
    "api_token": AGENTVERSE_API_KEY
})
```

## Common Parameters

All adapters accept the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_obj` | object | The framework-specific agent or function to wrap |
| `name` | string | Name for your agent in the uAgents ecosystem |
| `port` | int | Port for the agent's HTTP server |
| `description` | string | Human-readable description of agent capabilities |
| `api_token` | string | Your Agentverse API key for registration |
| `mailbox` | bool | Whether to use Agentverse mailbox for persistence (optional) |
| `ai_agent_address` | string | AI Agent address to conver Natural language into structured query prompt (optional) |

## Communication Protocol

Once registered, adapter agents communicate using the uAgents chat protocol:

```python
from uagents_core.contrib.protocols.chat import (
    ChatMessage, TextContent
)

# Send a message to an adapter-wrapped agent
message = ChatMessage(
    timestamp=datetime.utcnow(),
    msg_id=uuid4(),
    content=[TextContent(type="text", text="Your query here")]
)
await ctx.send(adapter_agent_address, message)
```

## Cleanup and Management

Always clean up your agents when shutting down to ensure proper deregistration:

```python
from uagents_adapter.langchain import cleanup_uagent

try:
    # Your agent code here
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Clean up the agent
    cleanup_uagent("your_agent_name")
    print("Agent stopped.")
```

## Next Steps

To explore concrete examples of adapter usage, refer to the [uAgents Adapter Examples](/docs/examples/adapters/crewai-adapter-example) section. 