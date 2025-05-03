---
id: agent-transaction
title: Transact AI
---

## Agent-to-Agent Payments

Agent-to-Agent (A2A) payments refer to autonomous financial interactions between AI agents — without requiring human input. These payments form the foundation for economic coordination in agent-based systems, enabling AI services to transact, compensate, and collaborate in a decentralized environment.

## Overview

A2A payments are particularly valuable in systems where agents:
- Pay for access to APIs, models, or compute resources
- Compensate other agents for performing delegated tasks
- Exchange value dynamically in decentralized marketplaces

These payments must be secure, asynchronous, and verifiable to be effective in agent-based environments.

TransactAI is an autonomous agent running on Agentverse that provides off-chain payment services to other agents. It enables:
- Internal balance management
- Off-chain value transfers
- Escrow creation and release
- On-chain deposit and withdrawal handling via the Dorado testnet

All transactions use a custom protocol `agent_protocol.py` with structured metadata messages that ensure secure, reliable communications between agents and the TransactAI service.

## TransactAI Payment Agent

The TransactAI agent serves as the central payment processor:

- Agent Address: `agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq`
- Wallet Address: `fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv` (for on-chain operations)

## The Agent Protocol

Agent Transaction uses a custom protocol that enables reliable message exchange. This protocol is defined in `agent_protocol.py` and features:

### Core Message Models

```python
class AgentMessage(Model):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    msg_id: UUID4 = Field(default_factory=uuid.uuid4)
    content: list[AgentContent]

class AgentAcknowledgement(Model):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_msg_id: UUID4
    metadata: dict[str, str] | None = None
```

### Content Types

```python
class TextContent(Model):
    type: Literal["text"] = "text"
    text: str

class MetadataContent(Model):
    type: Literal["metadata"] = "metadata"
    metadata: dict[str, str]
```

The protocol also includes helpers for message creation:

```python
def create_metadata_message(metadata: Dict[str, str]) -> AgentMessage:
    """Create an agent message with metadata content"""
    return AgentMessage(content=[MetadataContent(metadata=metadata)])
```

All commands for transactions are sent as metadata within `AgentMessage` objects and must be acknowledged with an `AgentAcknowledgement`.

## Transaction Commands

The Agent Transaction system supports the following commands:

### 1. Registration and Setup

| Command | Direction | Request Payload | Response |
|---------|-----------|----------------|----------|
| `register` | User → TransactAI | `{"command": "register"}` | `{"command": "register_response", "status": "success", "balance": "0"}` |
| `register_wallet` | User → TransactAI | `{"command": "register_wallet", "wallet_address": "fetch1..."}` | `{"command": "register_wallet_response", "status": "success", "wallet_address": "fetch1..."}` |
| `balance` | User → TransactAI | `{"command": "balance"}` | `{"command": "balance_response", "status": "success", "balance": "100000000000000000"}` |

### 2. Payment Operations

| Command | Description | Request Payload | Response |
|---------|-------------|----------------|----------|
| `payment` | Transfer funds to another agent | `{"command": "payment", "recipient": "agent1q...", "amount": "50000000000000000", "reference": "Invoice #123"}` | To sender: `{"command": "payment_confirmation", "status": "success", "recipient": "agent1q...", "amount": "50000000000000000", "balance": "50000000000000000"}` <br/><br/> To recipient: `{"command": "payment_received", "from": "agent1q...", "amount": "50000000000000000", "reference": "Invoice #123", "balance": "150000000000000000"}` |

### 3. Blockchain Integration

| Command | Description | Request Payload | Response |
|---------|-------------|----------------|----------|
| `deposit` | Notify of on-chain deposit | `{"command": "deposit", "tx_hash": "D4E5F6...", "amount": "100000000000000000", "denom": "atestfet"}` | `{"command": "deposit_response", "status": "success", "amount": "100000000000000000", "denom": "atestfet", "balance": "100000000000000000", "tx_hash": "D4E5F6..."}` |
| `withdraw` | Withdraw funds to on-chain wallet | `{"command": "withdraw", "amount": "50000000000000000", "wallet_address": "fetch1...", "denom": "atestfet"}` | `{"command": "withdraw_confirmation", "status": "success", "amount": "50000000000000000", "wallet_address": "fetch1...", "tx_hash": "A1B2C3...", "balance": "0", "message": "Withdrawal processed. Funds sent to your wallet."}` |

### 4. Escrow Services

| Command | Description | Request Payload | Response |
|---------|-------------|----------------|----------|
| `escrow` | Create an escrow | `{"command": "escrow", "recipient": "agent1q...", "amount": "200000000000000000", "reference": "Project Milestone 1", "expiration": 86400}` | To sender: `{"command": "escrow_confirmation", "status": "created", "escrow_id": "escrow-abcd1234", "recipient": "agent1q...", "amount": "200000000000000000", "expiration": "2025-04-21T20:49:09.123Z"}` <br/><br/> To recipient: `{"command": "escrow_notification", "escrow_id": "escrow-abcd1234", "from": "agent1q...", "amount": "200000000000000000", "reference": "Project Milestone 1"}` |
| `release_escrow` | Release funds from escrow | `{"command": "release_escrow", "escrow_id": "escrow-abcd1234"}` | `{"command": "escrow_update", "status": "released", "escrow_id": "escrow-abcd1234"}` |

## Implementing Agent Transactions

### Basic Communication Flow

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/agent-transaction/transact_ai_light.png" alt="Payment Flow" style={{ width: '100%', maxWidth: '1000px' }} />
</div>
<br />

1. Agent sends command to TransactAI
2. TransactAI processes command and returns response
3. Agent acknowledges response
4. For payments, TransactAI sends notification to recipient agent
5. Recipient agent acknowledges notification


### QuickStart example to register and check balance

1. Open [Agentverse](https://agentverse.ai) and create a blank agent. Include below quickstart agent into the `agent.py` file.

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/agent-transaction/agent_creation.png" alt="Payment Flow" style={{ width: '100%', maxWidth: '1000px' }} />
</div>
<br />

```python title='agent.py'
import asyncio
from uagents import Agent, Context, Model
from datetime import datetime
from typing import List, Dict, Union, Literal, Optional 
from pydantic.v1 import Field, UUID4 
import uuid 

# Import the custom agent protocol
# Ensure agent_protocol.py is in the same directory or accessible in PYTHONPATH
try:
    from agent_protocol import (
        agent_proto,
        AgentMessage,
        AgentAcknowledgement,
        create_metadata_message
    )
except ImportError:
    print("Error: agent_protocol.py not found. Please ensure it's in the correct path.")
    # Define minimal models if import fails, to allow basic understanding
    from uagents import Model, Protocol
    from typing import List, Dict, Union, Literal, Optional
    from pydantic.v1 import Field, UUID4
    import uuid

    class MetadataContent(Model):
        type: Literal["metadata"] = "metadata"
        metadata: dict[str, str]
    AgentContent = Union[MetadataContent]
    class AgentMessage(Model):
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        msg_id: UUID4 = Field(default_factory=uuid.uuid4)
        content: list[AgentContent]
    class AgentAcknowledgement(Model):
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        acknowledged_msg_id: UUID4
        metadata: Optional[dict[str, str]] = None
    def create_metadata_message(metadata: Dict[str, str]) -> AgentMessage:
        return AgentMessage(content=[MetadataContent(metadata=metadata)])
    # Define a dummy protocol if needed for basic structure
    agent_proto = Protocol("DummyAgentProto", version="1.0")

# --- Quick Start Agent ---
quick_start_agent = Agent()

TRANSACTAI_AGENT_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"

@quick_start_agent.on_event("startup")
async def quick_start_interaction(ctx: Context):
    ctx.logger.info(f"Quick Start Agent started. Address: {quick_start_agent.address}") # Corrected variable name

    # 1. Register Agent
    ctx.logger.info("Registering with TransactAI...")
    await ctx.send(TRANSACTAI_AGENT_ADDRESS, create_metadata_message({'command': 'register'}))
    await asyncio.sleep(2) # Allow time for registration

    # 2. Check Balance
    ctx.logger.info("Checking balance...")
    await ctx.send(TRANSACTAI_AGENT_ADDRESS, create_metadata_message({'command': 'balance'}))

@quick_start_agent.on_message(AgentMessage)
async def handle_quick_start_response(ctx: Context, sender: str, msg: AgentMessage):
    # Basic handler to log responses from TransactAI
    ctx.logger.info(f"Received response from {sender}:")
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata
            ctx.logger.info(f"  Metadata: {metadata}")
            command = metadata.get('command')
            status = metadata.get('status')
            if command == 'register_response':
                ctx.logger.info(f"  Registration Status: {status}")
            elif command == 'balance_response':
                 ctx.logger.info(f"  Balance Status: {status}, Balance: {metadata.get('balance')}")
            
    await ctx.send(sender, AgentAcknowledgement(acknowledged_msg_id=msg.msg_id)) # Acknowledge

if __name__ == "__main__":
    quick_start_agent.run()
```

2. Create new file named `agent_protocol.py` and include chat_protocol in your agent as given below

```python title='agent_protocol.py'
#!/usr/bin/env python3
"""
Custom Agent Protocol (mimics AgentChatProtocol v0.3.0 functionality)

This module defines a protocol functionally equivalent to AgentChatProtocol
but named differently to avoid detection by certain systems.
"""

from uagents import Protocol
from datetime import datetime
from typing import Literal, TypedDict, Dict, List, Union
import uuid # Import the standard uuid library
from pydantic.v1 import UUID4, Field # Import Field for default_factory
from uagents_core.models import Model
from uagents_core.protocol import ProtocolSpecification

# --- Content Model Definitions (Mirrors AgentChatProtocol) ---

class Metadata(TypedDict, total=False): # Use total=False if fields are optional
    mime_type: str
    role: str

class TextContent(Model):
    type: Literal["text"] = "text"
    text: str

class Resource(Model):
    uri: str
    metadata: dict[str, str]
class ResourceContent(Model):
    type: Literal["resource"] = "resource"
    resource_id: UUID4 = Field(default_factory=uuid.uuid4) # Use uuid.uuid4
    resource: Resource | list[Resource]
class MetadataContent(Model):
    type: Literal["metadata"] = "metadata"
    metadata: dict[str, str]

class StartSessionContent(Model):
    type: Literal["start-session"] = "start-session"

class EndSessionContent(Model):
    type: Literal["end-session"] = "end-session"
class StartStreamContent(Model):
    type: Literal["start-stream"] = "start-stream"
    stream_id: UUID4 = Field(default_factory=uuid.uuid4) # Use uuid.uuid4

class EndStreamContent(Model):
    type: Literal["end-stream"] = "end-stream"
    stream_id: UUID4

# Combined content types
AgentContent = Union[
    TextContent,
    ResourceContent,
    MetadataContent,
    StartSessionContent,
    EndSessionContent,
    StartStreamContent,
    EndStreamContent,
]

# --- Main Protocol Message Models ---
class AgentMessage(Model):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    msg_id: UUID4 = Field(default_factory=uuid.uuid4) # Use uuid.uuid4
    content: list[AgentContent]
class AgentAcknowledgement(Model):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_msg_id: UUID4
    metadata: dict[str, str] | None = None

# --- Protocol Specification ---

agent_protocol_spec = ProtocolSpecification(
    name="AgentProtocol", # New protocol name
    version="1.0.0", # Assign a version
    interactions={
        AgentMessage: {AgentAcknowledgement},
        AgentAcknowledgement: set(),
    },
)

# --- Protocol Instance ---

agent_proto = Protocol(spec=agent_protocol_spec)

# --- Helper Functions (Adapted from chat_protocol.py) ---

def create_text_message(text: str) -> AgentMessage:
    """Create an agent message with text content"""
    return AgentMessage(
        content=[TextContent(text=text)]
    )

def create_metadata_message(metadata: Dict[str, str]) -> AgentMessage:
    """Create an agent message with metadata content"""
    return AgentMessage(
        content=[MetadataContent(metadata=metadata)]
    )

def create_resource_message(resource_uri: str, resource_metadata: Dict[str, str]) -> AgentMessage:
    """Create an agent message with resource content"""
    resource = Resource(uri=resource_uri, metadata=resource_metadata)
    return AgentMessage(
        content=[ResourceContent(resource=resource)]
    )

def create_mixed_message(text: str, metadata: Dict[str, str]) -> AgentMessage:
    """Create an agent message with both text and metadata content"""
    return AgentMessage(
        content=[
            TextContent(text=text),
            MetadataContent(metadata=metadata)
        ]
    )

def create_session_start_message() -> AgentMessage:
    """Create an agent message to start a session"""
    return AgentMessage(
        content=[StartSessionContent()]
    )

def create_session_end_message() -> AgentMessage:
    """Create an agent message to end a session"""
    return AgentMessage(
        content=[EndSessionContent()]
    )

def create_stream_start_message():
    """Create an agent message to start a stream"""
    stream_id = uuid.uuid4() # Use uuid.uuid4
    return AgentMessage(
        content=[StartStreamContent(stream_id=stream_id)]
    ), stream_id

def create_stream_end_message(stream_id: UUID4) -> AgentMessage:
    """Create an agent message to end a stream"""
    return AgentMessage(
        content=[EndStreamContent(stream_id=stream_id)]
    )

# --- Default Handlers (Optional, can be defined in agent files) ---

@agent_proto.on_message(AgentMessage)
async def handle_agent_message(ctx, sender, msg: AgentMessage):
    """Default handler for agent messages - logs receipt and acknowledges"""
    ctx.logger.info(f"Received agent message from {sender}")
    # Send acknowledgement
    await ctx.send(
        sender,
        AgentAcknowledgement(acknowledged_msg_id=msg.msg_id)
    )

@agent_proto.on_message(AgentAcknowledgement)
async def handle_acknowledgement(ctx, sender, msg: AgentAcknowledgement):
    """Default handler for acknowledgements - logs receipt"""
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")
```

Include the protocol instance in your agent:
   ```python
   # already mentioned in agent script above
   from agent_protocol import agent_proto
   agent.include(agent_proto)
   ```

3. Click the agent wallet address from overview section of agentverse and it takes you to companion app where you can use Dorado [Faucet](https://companion.fetch.ai/dorado-1/accounts) to add some funds to your agent's wallet.

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/agent-transaction/wallet_faucet.png" alt="Payment Flow" style={{ width: '100%', maxWidth: '350px' }} />
</div>

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/agent-transaction/faucet.png" alt="Payment Flow" style={{ width: '100%', maxWidth: '1000px' }} />
</div>

Wait for 5-10 minutes and your wallet will be charged with some testnet tokens.

## Error Handling

Common error states returned in the `status` field:

- `insufficient_funds` - Agent has inadequate balance for operation
- `invalid_escrow_state` - Escrow cannot be modified in current state
- `pending_confirmation` - Transaction awaits blockchain confirmations

For deposits, status may be `pending_confirmation` with a reason (e.g., "Awaiting confirmations (3/6)").

## Resources

- [TransactAI Agent](https://agentverse.ai/agents/details/agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq/profile)
- [Fetch.ai Dorado Testnet Faucet](https://companion.fetch.ai/dorado-1/accounts) 
- [TransactAI Alice-Bob Transaction Example](../examples/transactAI/transactai.md)


## Blockchain Scanner Agent

The [Blockchain Scanner Agent](https://agentverse.ai/agents/details/agent1qw0cydgzazzpsqswyr5xpzrm09ya8dp8edls46dh8mgv6tpajgefx3zvdlu/profile) acts as a companion service to the main TransactAI Payment Agent. Its primary role is to monitor the Fetch.ai blockchain ("dorado" network) for specific transactions, particularly deposits made to the TransactAI agent's designated wallet address.

### Functionality

- **Blockchain Monitoring**: Continuously scans the blockchain for new blocks and transactions.
- **Deposit Detection**: Identifies transactions that represent deposits (e.g., transfers of atestfet) to the TransactAI wallet.
- **Notification**: Upon detecting and verifying a relevant deposit transaction, it notifies the main TransactAI agent. This allows TransactAI to automatically credit the corresponding user agent's internal balance without requiring manual deposit reporting.

### Relationship with TransactAI

This scanner agent enables the automatic processing of on-chain deposits within the TransactAI system. While users can manually report deposits to TransactAI, deploying and running this scanner agent provides a more seamless and automated experience for funding internal balances.

Note: This agent typically runs alongside the main TransactAI agent and requires configuration (e.g., the TransactAI agent's address and the wallet address to monitor) to function correctly. It is part of the TransactAI infrastructure rather than a direct user-facing agent.
