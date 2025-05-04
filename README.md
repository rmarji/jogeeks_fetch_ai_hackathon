# n8n Chat Agent

## Overview

The n8n Chat Agent provides a conversational bridge between Fetch.ai's agent ecosystem and automation workflows. It enables agents to trigger n8n workflows through natural language, creating a critical link between agent intelligence and real-world actions.

This agent implements the ASI-1 Chat Protocol to provide a seamless interface for triggering complex automation workflows in n8n, Zapier, Make.com, and Active Pieces from natural language requests, dramatically expanding what Fetch.ai agents can accomplish.

**Agent Address:**  
`agent1q...` (Replace with your actual agent address once deployed)

---

## Quick Start Example

This example demonstrates how another agent can interact with the n8n Chat Agent to trigger a workflow:

```python
import asyncio
from datetime import datetime
from uuid import uuid4

from uagents import Agent, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    StartSessionContent,
    chat_protocol_spec,
)

# Configuration
N8N_AGENT_ADDRESS = "agent1q..." # Replace with your n8n Chat Agent address

# Create a test client agent
client_agent = Agent(
    name="test_client",
    seed="test_client_seed_phrase",
)

# Chat protocol for the client
chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages from the n8n agent"""
    # Send acknowledgement
    await ctx.send(
        sender,
        ChatAcknowledgement(timestamp=datetime.utcnow(), acknowledged_msg_id=msg.msg_id),
    )
    
    # Process message
    for item in msg.content:
        if hasattr(item, "text"):
            print(f"\nReceived response from agent: {item.text}")

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements from the n8n agent"""
    print(f"Message acknowledged: {msg.acknowledged_msg_id}")

# Function to send a message to the n8n agent
async def send_message(ctx: Context, message_text: str):
    """Send a chat message to the n8n agent"""
    # Create the chat message
    message = ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=uuid4(),
        content=[
            StartSessionContent(type="start-session"),
            TextContent(type="text", text=message_text)
        ]
    )
    
    # Send the message
    print(f"\nSending message: '{message_text}'")
    await ctx.send(N8N_AGENT_ADDRESS, message)

# Include the chat protocol
client_agent.include(chat_proto)

@client_agent.on_event("startup")
async def on_startup(ctx: Context):
    """Start interaction on agent startup"""
    print(f"Test client started with address: {client_agent.address}")
    
    # Example: Send a request to create a trading signal
    await send_message(ctx, "Send a crypto trading signal for BTC/USDT, Buy at $75,200 with stop-loss at $73,500")

if __name__ == "__main__":
    client_agent.run()
```

---

## Features

- **Chat Protocol Integration:** Fully compatible with ASI-1 Chat Protocol
- **Universal Workflow Support:** Connects to multiple workflow platforms:
  - n8n (300+ integrations)
  - Zapier (5,000+ app connections)
  - Make.com (1,000+ app integrations)
  - Active Pieces (Expanding integration library)
- **Response Handling:** Processes workflow results and formats them as chat messages
- **Rate Limiting:** Prevents abuse through configurable request quotas
- **Error Recovery:** Robust error handling and reporting
- **Health Monitoring:** Built-in health check functionality

---

## Use Cases

- **Trading Signals:** Create and send cryptocurrency trading signals to Telegram channels through natural language commands.
- **Customer Support:** Trigger customer support workflows, create tickets, and check status through conversational interfaces.
- **Content Creation:** Generate and publish content to multiple platforms with simple requests.
- **Data Analysis:** Request and receive custom reports and analytics through natural language.

---

## Technical Architecture

The agent implements a multi-layer architecture that connects agent intelligence to action:

1. **Language Understanding:** Process natural language requests through the Chat Protocol
2. **Platform Routing:** Select optimal workflow platform for the request
3. **Parameter Extraction:** Identify required workflow inputs
4. **Execution Management:** Trigger workflows and monitor status
5. **Response Formatting:** Convert results to conversational format

---

## TransactAI Integration

The n8n Chat Agent can be seamlessly integrated with TransactAI to enable a monetization layer for workflow execution, creating a sustainable economy around automation.

### Monetization Options

**Pay-per-Execution Model:**
- Users pay a small fee for each workflow execution
- Workflow creators receive a share of execution fees
- Complex workflows command premium prices

**Implementation Approach:**
- Add a payment command before workflow execution
- Validate payment success before triggering the workflow
- Refund mechanism for failed executions

### Example TransactAI Flow

1. User Agent → n8n Chat Agent: "Execute workflow X"
2. n8n Chat Agent → User Agent: "Execution requires 5 tokens. Proceed?"
3. User Agent → TransactAI: Payment of 5 tokens to n8n Chat Agent
4. TransactAI → n8n Chat Agent: Payment confirmation
5. n8n Chat Agent → Workflow Platform: Execute workflow
6. n8n Chat Agent → User Agent: Execution results

#### Code Integration Example

To integrate TransactAI with the n8n Chat Agent, add payment validation to the workflow execution process:

```python
# Sample code for handling payments via TransactAI before workflow execution
async def process_workflow_with_payment(ctx: Context, sender: str, workflow_id: str, payload: dict):
    # Define execution cost based on workflow complexity
    execution_cost = get_workflow_cost(workflow_id)
    
    # Request payment approval
    await ctx.send(
        sender,
        create_text_chat(f"Execution of this workflow requires {execution_cost} tokens. Reply 'confirm' to proceed.")
    )
    
    # Payment processing happens in another handler after user confirms
    # Store the pending request in context for when payment is confirmed
    ctx.storage.set(f"pending_execution_{sender}", {
        "workflow_id": workflow_id,
        "payload": payload,
        "execution_cost": execution_cost
    })

# When payment is confirmed through TransactAI:
async def on_payment_received(ctx: Context, sender: str, amount: str):
    # Retrieve pending execution
    pending = ctx.storage.get(f"pending_execution_{sender}")
    
    if pending and int(amount) >= pending["execution_cost"]:
        # Execute the workflow now that payment is confirmed
        result = await call_webhook(pending["workflow_id"], pending["payload"])
        # Return results to user
        await ctx.send(sender, create_text_chat(result))
    else:
        # Payment insufficient or no pending execution
        await ctx.send(sender, create_text_chat("Payment validation failed or no pending execution found."))
```

---

## Setup Instructions

**Prerequisites:**
- Python 3.8+
- uAgents library
- Access to workflow platforms (n8n, Zapier, etc.)

**Configuration:**
- Set up your workflow platform webhooks
- Configure webhook URLs in the agent
- Set authentication tokens if required

**Deployment:**
- Deploy on Agentverse for continuous availability
- Or run locally for development and testing

---

## Future Roadmap

- Multi-platform Integration: Expand support to additional workflow platforms
- Workflow Discovery: Allow agents to discover available workflows
- Contextual Memory: Remember context across conversation sessions
- TransactAI Marketplace: Full integration with workflow monetization
- Agent-to-Agent Delegation: Enable workflows that involve multiple specialized agents

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License.

---

## Protocols

### AgentChatProtocol v0.3.0

- **ChatMessage**
  - `content`: array
  - `msg_id`: string
  - `timestamp`: string
- **ChatAcknowledgement**
  - `acknowledged_msg_id`: string
  - `metadata`: object
  - `timestamp`: string

### HealthProtocol v0.1.0

- **HealthCheck**
- **AgentHealth**
  - `agent_name`: string
  - `status`: object

---