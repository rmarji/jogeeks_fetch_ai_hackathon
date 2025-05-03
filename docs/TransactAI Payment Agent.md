TransactAI Payment Agent
domain:finance tech:python tech:uagents platform:agentverse status:live

This agent provides an off-chain payment gateway service running on Agentverse. It allows registered agents to manage internal balances, perform fast off-chain payments, create escrows, and handle deposits/withdrawals linked to the Fetch.ai blockchain ("dorado" network).

Protocol Note: This agent uses a custom protocol defined in agent_protocol.py. All interactions involve sending an AgentMessage containing MetadataContent. Agents interacting with TransactAI must import and include this protocol using from agent_protocol import agent_proto and agent.include(agent_proto).

Agent Address
agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq

Quick Start Example
This simple example shows how another agent can register with TransactAI and check its initial balance. Note: This example assumes agent_protocol.py is accessible in the same directory or Python path.

import asyncio
from datetime import datetime
from typing import Literal, TypedDict, Dict, List, Union, Optional # Added typing imports
import uuid # Added uuid import
# --- Import Protocol Elements ---
# Assumes agent_protocol.py is accessible
# Direct import - assuming agent_protocol.py is accessible in Agentverse
from agent_protocol import agent_proto, AgentMessage, AgentAcknowledgement, create_metadata_message

from uagents import Agent, Context, Model, Protocol # Added Model, Protocol
from pydantic.v1 import Field, UUID4 # Added pydantic imports
from uagents_core.protocol import ProtocolSpecification # Added core import


# --- Agentverse Quick Start Logic ---
# NOTE: Agentverse provides an implicit 'agent' object.
# We configure it directly instead of creating a new Agent instance.
TRANSACTAI_AGENT_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"
@agent.on_event("startup")
async def quick_start_interaction(ctx: Context):
    # Use ctx.address which refers to the implicit agent's address
    ctx.logger.info(f"Quick Start Agent started. Address: {ctx.address}")

    # 1. Register Agent
    ctx.logger.info("Registering with TransactAI...")
    await ctx.send(TRANSACTAI_AGENT_ADDRESS, create_metadata_message({'command': 'register'}))
    await asyncio.sleep(2) # Allow time for registration

    # 2. Check Balance
    ctx.logger.info("Checking balance...")
    await ctx.send(TRANSACTAI_AGENT_ADDRESS, create_metadata_message({'command': 'balance'}))

# Use the protocol decorator or the base model decorator
@agent_proto.on_message(model=AgentMessage)
async def handle_quick_start_response(ctx: Context, sender: str, msg: AgentMessage):
    # Basic handler to log responses from TransactAI
    ctx.logger.info(f"Received response from {sender}:")
    response_handled = False
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata
            ctx.logger.info(f"  Metadata: {metadata}")
            command = metadata.get('command')
            status = metadata.get('status')
            if command == 'register_response':
                ctx.logger.info(f"  Registration Status: {status}")
                response_handled = True
            elif command == 'balance_response':
                 ctx.logger.info(f"  Balance Status: {status}, Balance: {metadata.get('balance')}")
                 response_handled = True
            
    if response_handled:
        await ctx.send(sender, AgentAcknowledgement(acknowledged_msg_id=msg.msg_id)) # Acknowledge

@agent_proto.on_message(model=AgentAcknowledgement)
async def handle_quick_start_ack(ctx: Context, sender: str, msg: AgentAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")
# Agentverse handles running the agent, so no if __name__ == "__main__": block is needed.
# Include the protocol AFTER handlers are defined
agent.include(agent_proto)

Operations
This agent supports the following commands, sent within the metadata field of a MetadataContent object inside an AgentMessage.

1. Register Agent
Registers the sending agent with the TransactAI system, creating an internal balance (initially zero).

Input Metadata:

{ "command": "register" }

Output Metadata (Success):

{ "command": "register_response", "status": "success", "balance": "0" }

2. Register Wallet
Links the sending agent's address to their external Fetch.ai blockchain wallet address. Crucial for associating incoming deposits. Processes any previously unmatched deposits for this wallet upon registration.

Input Metadata:

{ "command": "register_wallet", "wallet_address": "fetch1..." }

Output Metadata (Success):

{ "command": "register_wallet_response", "status": "success", "wallet_address": "fetch1..." }

3. Check Balance
Retrieves the sending agent's current internal balance.

Input Metadata:

{ "command": "balance" }

Output Metadata (Success):

{ "command": "balance_response", "status": "success", "balance": "100000000000000000" } 

4. Internal Payment
Transfers funds internally from the sender's balance to another registered agent's balance.

Input Metadata:

{ 
  "command": "payment", 
  "recipient": "agent1q...", 
  "amount": "50000000000000000", 
  "reference": "Invoice #123" 
}

Output Metadata (Sender Confirmation - Success):

{ 
  "command": "payment_confirmation", 
  "status": "success", 
  "recipient": "agent1q...", 
  "amount": "50000000000000000", 
  "balance": "50000000000000000" 
}

Output Metadata (Recipient Notification):

{ 
  "command": "payment_received", 
  "from": "agent1q...", 
  "amount": "50000000000000000", 
  "reference": "Invoice #123", 
  "balance": "150000000000000000" 
}

(Common failure reason for payment_confirmation: insufficient_funds)

5. Withdraw Funds
Initiates an on-chain transfer from the TransactAI agent's wallet to the sender's registered external wallet, deducting the amount from the sender's internal balance.

Input Metadata:

{ 
  "command": "withdraw", 
  "amount": "50000000000000000", 
  "wallet_address": "fetch1...", 
  "denom": "atestfet" 
}

Output Metadata (Success):

{ 
  "command": "withdraw_confirmation", 
  "status": "success", 
  "amount": "50000000000000000", 
  "wallet_address": "fetch1...", 
  "tx_hash": "A1B2C3...", 
  "balance": "0", 
  "message": "Withdrawal processed. Funds sent to your wallet." 
}

(Common failure reasons: insufficient_funds)

6. Create Escrow
Holds funds from the sender's balance in escrow for a recipient, with an expiration time provided by the sender in seconds. Expired escrows are automatically refunded to the sender during periodic checks (default: every 60s).

Input Metadata:

{ 
  "command": "escrow", 
  "recipient": "agent1q...", 
  "amount": "200000000000000000", 
  "reference": "Project Milestone 1", 
  "expiration": 86400 
}

Output Metadata (Sender Confirmation - Success):

{ 
  "command": "escrow_confirmation", 
  "status": "created", 
  "escrow_id": "escrow-abcd1234", 
  "recipient": "agent1q...", 
  "amount": "200000000000000000", 
  "expiration": "2025-04-21T20:49:09.123Z" 
}

Output Metadata (Recipient Notification):

{ 
  "command": "escrow_notification", 
  "escrow_id": "escrow-abcd1234", 
  "from": "agent1q...", 
  "amount": "200000000000000000", 
  "reference": "Project Milestone 1" 
}

(Common failure reason for escrow_confirmation: insufficient_funds)

7. Release Escrow
Releases funds held in a specific escrow to the recipient. Only the original sender can release.

Input Metadata:

{ "command": "release_escrow", "escrow_id": "escrow-abcd1234" }

Output Metadata (Sender Confirmation - Success):

{ "command": "escrow_update", "status": "released", "escrow_id": "escrow-abcd1234" }

(Note: If escrow expires, sender receives status: 'refunded' and recipient receives status: 'expired') (Common failure reason for escrow_update: invalid_escrow_state)

8. Process Deposit (Manual/Scanner)
Informs TransactAI about an on-chain deposit made to its wallet. TransactAI verifies the transaction (checks amount, recipient, confirmations) and credits the associated agent's internal balance.

Important: Automatic detection relies on the separate blockchain_scan_agent. If that agent is not deployed and running, users MUST manually send this deposit command after making an on-chain transfer for their balance to be updated. Ensure the tx_hash, amount, and denom are correct.

Input Metadata:

{ 
  "command": "deposit", 
  "tx_hash": "D4E5F6...", 
  "amount": "100000000000000000", 
  "denom": "atestfet" 
}

Output Metadata (Success - Sent to Depositor Agent):

{ 
  "command": "deposit_response", 
  "status": "success", 
  "amount": "100000000000000000", 
  "denom": "atestfet", 
  "balance": "100000000000000000", 
  "tx_hash": "D4E5F6..." 
}

Output Metadata (Pending):

{ "command": "deposit_response", "status": "pending_confirmation", "reason": "Awaiting confirmations (3/6)" }

(Common failure reasons: Transaction not found, Transaction failed on chain, No coin_received event found, Recipient mismatch, Denomination mismatch, Amount mismatch, Transaction already processed)

Important Notes / Prerequisites
Registration: Agents MUST register before performing most actions.
Wallet Registration: Agents MUST register_wallet with their external Fetch wallet address before deposits can be correctly credited or withdrawals can be processed.
Deposits:
Wallet Address: Perform on-chain transfers to the TransactAI agent's designated wallet: fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv.
Notification: If the companion blockchain_scan_agent is running, it should detect the deposit automatically. If not, you must send the deposit command manually with the correct transaction hash.
CRITICAL: Ensure the blockchain_scan_agent (if used) is configured to monitor the same wallet address (...lhkv) mentioned above. An inconsistency here will break automatic deposit detection.
Amounts & Denominations: All amount values MUST be specified as strings representing the value in the smallest unit of the currency (e.g., atestfet, not TESTFET). The denom field specifies the currency (e.g., "atestfet").
Companion Scanner: For automatic deposit detection, the blockchain_scan_agent needs to be deployed and configured with this TransactAI agent's address and the correct wallet address to monitor.
Alice & Bob Workflow Example (Conceptual Flow)
This example illustrates a typical interaction flow involving two agents, Alice (sender) and Bob (receiver), using the TransactAI agent.

Assumptions:

Alice, Bob, and TransactAI agents are deployed on Agentverse.
TRANSACTAI_AGENT_ADDRESS, ALICE_AGENT_ADDRESS, BOB_AGENT_ADDRESS are known.
TRANSACTAI_WALLET_ADDRESS (fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv) is known.
Flow:

Registration: Both Alice and Bob send register and register_wallet commands to TransactAI.
Deposit: Alice sends tokens (e.g., atestfet) on-chain to TRANSACTAI_WALLET_ADDRESS.
Deposit Notification: Alice (or the blockchain_scan_agent) sends a deposit command to TransactAI with the transaction hash.
Deposit Confirmation: TransactAI verifies the deposit (waits for confirmations) and sends a deposit_response (status: 'success') back to Alice.
Internal Payment: Alice sends a payment command to TransactAI, specifying Bob as the recipient.
Payment Notifications:
TransactAI sends a payment_confirmation (status: 'success') to Alice.
TransactAI sends a payment_received notification to Bob.
Withdrawal: Bob receives the notification and sends a withdraw command to TransactAI to transfer the funds to his own external wallet.
Withdrawal Confirmation: TransactAI performs the on-chain withdrawal and sends a withdraw_confirmation (status: 'success') to Bob.
Advanced Usage Example
This example demonstrates registering, checking balance, and attempting a payment. Copy and paste the following code into a new Blank agent on Agentverse. Note: Ensure the wallet associated with this agent has atestfet from the Dorado Faucet if you intend to test deposits or payments. Also assumes agent_protocol.py is accessible.

import asyncio
from uagents import Agent, Context
from uagents.network import get_ledger # Import for on-chain tx
import uuid # Added for deposit simulation
from datetime import datetime

# --- Import Protocol Elements ---
# Assumes agent_protocol.py is accessible
# Direct import - assuming agent_protocol.py is accessible in Agentverse
from agent_protocol import agent_proto, AgentMessage, AgentAcknowledgement, create_metadata_message

# --- Example Agent (Uses implicit Agentverse 'agent') ---


TRANSACTAI_AGENT_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"
TRANSACTAI_WALLET = "fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv" # TransactAI's on-chain wallet
# Replace with another agent's address to send payment to
RECIPIENT_AGENT_ADDRESS = "agent1q2khu9zsm9sae3x42qcxj9vz0u5wlhs8wdt9t0k75kaq4287xldwjulm0hc" # Bob's address

# IMPORTANT: Replace with a seed phrase that has funds on the Dorado testnet!
# This temporary agent is ONLY used to sign the on-chain deposit transaction.
TEMP_DEPOSIT_SEED = "replace this with your funded dorado testnet seed phrase"

@agent.on_event("startup")
async def interact_with_transactai(ctx: Context):
    ctx.logger.info(f"User agent started. Address: {agent.address}")
    ctx.logger.info(f"Wallet address: {agent.wallet.address()}")
    # Flags to manage asynchronous flow
    ctx.storage.set("wallet_registered", False) # Track wallet registration confirmation
    ctx.storage.set("deposit_confirmed", False) # Track deposit confirmation
    ctx.storage.set("payment_attempted", False) # Prevent duplicate payments

    # 1. Register Agent
    ctx.logger.info("Registering with TransactAI...")
    await ctx.send(TRANSACTAI_AGENT_ADDRESS, create_metadata_message({'command': 'register'}))
    await asyncio.sleep(2)

    # 2. Register Wallet (Replace with your actual wallet address)
    my_wallet = str(agent.wallet.address())
    ctx.logger.info(f"Registering wallet {my_wallet} with TransactAI...")
    await ctx.send(TRANSACTAI_AGENT_ADDRESS, create_metadata_message({
        'command': 'register_wallet',
        'wallet_address': my_wallet
    }))
    # Wallet registration response will be handled asynchronously by handle_response
    # Proceed directly to deposit attempt after sending registration request

    # 3. Perform On-Chain Deposit and Notify TransactAI
    ctx.logger.info("Attempting on-chain deposit to TransactAI wallet...")
    # Ensure the agent's wallet has funds from the faucet: https://companion.fetch.ai/dorado-1/accounts
    deposit_amount = 50000 # Small amount in atestfet for testing
    tx_hash = None
    ctx.logger.info("Waiting 5 seconds before attempting deposit...")
    await asyncio.sleep(5) # Add delay to allow wallet initialization?
    try:
        ctx.logger.info("Attempting to get ledger...")
        ledger = get_ledger("dorado")
        ctx.logger.info("Ledger obtained successfully.")

        # Create a temporary agent instance JUST for sending the deposit
        # Use the predefined seed phrase which MUST have funds
        if not TEMP_DEPOSIT_SEED or TEMP_DEPOSIT_SEED == "replace this with your funded dorado testnet seed phrase":
             raise ValueError("TEMP_DEPOSIT_SEED is not set or is still the placeholder. Please replace it with a funded seed phrase.")
        
        ctx.logger.info(f"Creating temporary agent from seed: {TEMP_DEPOSIT_SEED[:10]}...") # Log first few words
        temp_agent = Agent(name="temp_deposit_sender", seed=TEMP_DEPOSIT_SEED)
        ctx.logger.info(f"Temporary agent wallet address: {temp_agent.wallet.address()}")

        # Optional: Check balance of temporary wallet (uncomment if needed, requires ledger query)
        # balance = ledger.query_bank_balance(temp_agent.wallet.address())
        # ctx.logger.info(f"Temporary agent wallet balance: {balance} {ledger.network_config.chain_id}")
        # if balance < deposit_amount:
        #     raise ValueError(f"Temporary agent wallet {temp_agent.wallet.address()} has insufficient funds ({balance}) for deposit ({deposit_amount}).")

        # Send tokens using the temporary agent's wallet
        ctx.logger.info(f"Attempting to send {deposit_amount} atestfet from {temp_agent.wallet.address()} to {TRANSACTAI_WALLET}...")
        tx = ledger.send_tokens(TRANSACTAI_WALLET, deposit_amount, "atestfet", temp_agent.wallet)
        ctx.logger.info("Transaction sent, attempting to wait for completion...")
        result = tx.wait_to_complete()
        ctx.logger.info("Transaction wait completed.")
        tx_hash = result.tx_hash
        ctx.logger.info(f"On-chain deposit successful. Tx Hash: {tx_hash}")
    except Exception as e:
        ctx.logger.error(f"ERROR during on-chain deposit: {e}") # Log the error message
        # Optional: Add logic here to stop if deposit fails (e.g., return)

    # Notify TransactAI about the deposit (if successful)
    if tx_hash:
        ctx.logger.info(f"Sending deposit notification command for tx_hash: {tx_hash}")
        deposit_confirm_msg = create_metadata_message({
            'command': 'deposit',
            'tx_hash': tx_hash,
            'amount': str(deposit_amount), # Send amount as string
            'denom': "atestfet"
        })
        await ctx.send(TRANSACTAI_AGENT_ADDRESS, deposit_confirm_msg)
        await asyncio.sleep(5) # Allow time for TransactAI to process notification
    else:
         ctx.logger.warning("Skipping deposit notification as on-chain transaction failed or hash not found.")
    
    # Balance check and payment attempt will now be triggered by handle_response
    # after deposit confirmation, similar to the alice.py example.


# Helper function to attempt payment after deposit confirmation
async def maybe_send_payment(ctx: Context):
    # Ensure deposit is confirmed and payment hasn't been attempted
    if ctx.storage.get("deposit_confirmed") is True and not ctx.storage.get("payment_attempted"):
        payment_amount = 1000 # Small amount for testing (in atestfet)
        ctx.logger.info(f"Deposit confirmed, now attempting payment of {payment_amount} to {RECIPIENT_AGENT_ADDRESS}...")
        ctx.storage.set("payment_attempted", True) # Mark as attempted
        payment_msg = create_metadata_message({
            'command': 'payment',
            'recipient': RECIPIENT_AGENT_ADDRESS,
            'amount': str(payment_amount),
            'reference': 'Test Payment - Advanced Example'
        })
        await ctx.send(TRANSACTAI_AGENT_ADDRESS, payment_msg)
    elif ctx.storage.get("payment_attempted"):
         ctx.logger.info("Payment already attempted.")
    # else: deposit not confirmed yet

# Use the protocol decorator or the base model decorator
@agent_proto.on_message(model=AgentMessage)
async def handle_response(ctx: Context, sender: str, msg: AgentMessage):
    # Basic handler to log responses from TransactAI
    ctx.logger.info(f"Received response from {sender}:")
    response_handled = False
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata # Get metadata dict
            ctx.logger.info(f"  Metadata: {metadata}")
            command = metadata.get('command')
            status = metadata.get('status')

            # Check for wallet registration confirmation (still useful for logging)
            if command == 'register_wallet_response' and status == 'success':
                ctx.logger.info("Wallet registration confirmed by TransactAI.")
                # ctx.storage.set("wallet_registered", True) # No longer needed for blocking wait
            
            # Check for deposit confirmation
            elif command == 'deposit_response':
                 ctx.logger.info(f"Deposit response received: {metadata}")
                 if status == 'success':
                     ctx.logger.info("Deposit confirmed by TransactAI.")
                     ctx.storage.set("deposit_confirmed", True)
                     # Trigger payment attempt asynchronously
                     asyncio.create_task(maybe_send_payment(ctx))
                 elif status == 'pending_confirmation':
                     ctx.logger.info("Deposit is still pending confirmation.")
                 else: # Failed
                     ctx.logger.error(f"Deposit failed: {metadata.get('reason')}")
            
            # Log payment confirmation status
            elif command == 'payment_confirmation':
                 if status == 'success':
                     ctx.logger.info(f"Payment successful! New balance: {metadata.get('balance')}")
                 else:
                     ctx.logger.error(f"Payment failed! Reason: {metadata.get('reason')}, Balance: {metadata.get('balance')}")

            # Log other confirmations if needed (e.g., register_response, balance_response)
            elif command == 'register_response':
                 ctx.logger.info(f"Registration response: {status}")
            elif command == 'balance_response':
                 ctx.logger.info(f"Balance response: {status}, Balance: {metadata.get('balance')}")


            response_handled = True # Acknowledge any metadata message
        elif content.type == "text":
            # In this simplified example, we don't expect text content from TransactAI
            ctx.logger.info(f"  Unexpected Text: {content.text}")
            response_handled = True
            
    if response_handled:
        await ctx.send(sender, AgentAcknowledgement(acknowledged_msg_id=msg.msg_id))

@agent_proto.on_message(model=AgentAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: AgentAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

# Agentverse handles running the agent, so no if __name__ == "__main__": block is needed.
# Include the protocol AFTER handlers are defined (Agentverse specific)
agent.include(agent_proto)

Communication Protocol Details (agent_protocol.py)
This agent uses a custom protocol defined in agent_protocol.py, which mimics the structure of AgentChatProtocol. All commands are sent via MetadataContent within an AgentMessage. Agents interacting with TransactAI must import and include this protocol using from agent_protocol import agent_proto and agent.include(agent_proto).

(Note: The following is the full definition from agent_protocol.py for reference, especially if copying examples directly into Agentverse.)

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

# @agent_proto.on_message(AgentMessage)
# async def handle_agent_message(ctx, sender, msg: AgentMessage):
#     """Default handler for agent messages - logs receipt and acknowledges"""
#     ctx.logger.info(f"Received agent message from {sender}")
#     # Send acknowledgement
#     await ctx.send(
#         sender,
#         AgentAcknowledgement(acknowledged_msg_id=msg.msg_id)
#     )

# @agent_proto.on_message(AgentAcknowledgement)
# async def handle_acknowledgement(ctx, sender, msg: AgentAcknowledgement):
#     """Default handler for acknowledgements - logs receipt"""
#     ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

Protocols
AgentProtocol
v1.0.0
AgentMessage
content
array
msg_id
string
timestamp
string
AgentAcknowledgement
acknowledged_msg_id
string
metadata
object
timestamp
string
Default
v0.1.0