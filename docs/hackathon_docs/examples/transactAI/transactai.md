---
id: transactai-example
title: TransactAI Payment Example
---

# TransactAI Payment Example

This example demonstrates how to use TransactAI for agent-to-agent payments on Agentverse with [TransactAI](https://agentverse.ai/agents/details/agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq/profile). The example shows a complete payment flow between two agents: Alice (sender) and Bob (receiver).

## Overview

The example demonstrates the following:

1. Registering agents with TransactAI
2. Linking on-chain wallet addresses
3. Making on-chain deposits to fund the TransactAI account
4. Sending payments between agents
5. Receiving payments
6. Withdrawing funds to on-chain wallets


## Workflow Diagram

<div style={{ textAlign: 'center' }}>
  <img src="/resources/img/agent-transaction/alice_bob_transact.png" alt="Payment Flow" style={{ width: '100%', maxWidth: '1000px' }} />
</div>

1. **Registration Process**: Before using TransactAI, agents must register themselves and their wallet addresses.

2. **Denominations**: All amounts are expressed in "atestfet" (smallest unit), where 1 TESTFET = 10^18 atestfet.

3. **Deposit Process**:
   - Make an on-chain deposit to TransactAI's wallet
   - Notify TransactAI with the transaction hash
   - Wait for TransactAI to confirm the deposit (may require several blockchain confirmations)

4. **Payment Flow**:
   - Sender sends payment command to TransactAI
   - TransactAI updates internal balances
   - TransactAI sends confirmation to sender
   - TransactAI sends notification to recipient

5. **Withdrawal Process**:
   - Send withdrawal request to TransactAI with amount and wallet address
   - TransactAI executes on-chain transaction
   - TransactAI sends confirmation with transaction hash

6. **Acknowledgements**: All messages must be acknowledged to confirm receipt.


## Prerequisites

- [Agnetverse](https://agentverse.ai) account.
- Access to Fetch.ai Dorado testnet.
- Testnet tokens (can be obtained from [Fetch.ai Dorado Faucet](https://companion.fetch.ai/dorado-1/accounts/fetch1n9vnna29c8us5pk9fxqhzltmgpeyn3hl4le28h#Transactions))

## Example Code

### agent_protocol.py

First, we need the custom protocol that enables communication with TransactAI:

```python title='agent_protocol.py'
"""
Custom Agent Protocol for TransactAI

This protocol allows agents to communicate with the TransactAI payment agent
by defining message structures and content types.
"""

from uagents import Protocol
from datetime import datetime
from typing import Literal, TypedDict, Dict, List, Union
import uuid
from pydantic.v1 import UUID4, Field
from uagents_core.models import Model
from uagents_core.protocol import ProtocolSpecification

# --- Content Model Definitions ---

class Metadata(TypedDict, total=False):
    mime_type: str
    role: str

class TextContent(Model):
    type: Literal["text"] = "text"
    text: str

class MetadataContent(Model):
    type: Literal["metadata"] = "metadata"
    metadata: dict[str, str]

# Combined content types
AgentContent = Union[TextContent, MetadataContent]

# --- Main Protocol Message Models ---
class AgentMessage(Model):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    msg_id: UUID4 = Field(default_factory=uuid.uuid4)
    content: list[AgentContent]

class AgentAcknowledgement(Model):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_msg_id: UUID4
    metadata: dict[str, str] | None = None

# --- Protocol Specification ---
agent_protocol_spec = ProtocolSpecification(
    name="AgentProtocol",
    version="1.0.0",
    interactions={
        AgentMessage: {AgentAcknowledgement},
        AgentAcknowledgement: set(),
    },
)

# --- Protocol Instance ---
agent_proto = Protocol(spec=agent_protocol_spec)

# --- Helper Functions ---
def create_metadata_message(metadata: Dict[str, str]) -> AgentMessage:
    """Create an agent message with metadata content"""
    return AgentMessage(
        content=[MetadataContent(metadata=metadata)]
    )

def create_text_message(text: str) -> AgentMessage:
    """Create an agent message with text content"""
    return AgentMessage(
        content=[TextContent(text=text)]
    )
```

### Alice (Sender) Agent

```python title='alice_agent.py'
"""
Alice Agent - Sends payments via TransactAI
"""

import asyncio
from uagents import Agent, Context
from uagents.network import get_ledger
from datetime import datetime

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


# TransactAI agent address (ensure this is correct)
TRANSACTAI_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"
TRANSACTAI_WALLET = "fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv" # TransactAI's on-chain wallet

# Bob's agent address
BOB_ADDRESS = "agent1q2v8ck694z7h6qww90kvv4qafrnvlaquwpeuqtarsyhdmsve4v6k7r0a8l0" # Replace it with your bob's address 

# Alice agent setup
# CRITICAL: Replace this seed phrase with your own secure one for actual use!
alice = Agent()

DEPOSIT_CONFIRMED_FLAG = "deposit_confirmed"
PAYMENT_ATTEMPTED_FLAG = "payment_attempted"

@alice.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Alice started. Address: {alice.address}")
    ctx.logger.info(f"Wallet address: {alice.wallet.address()}")

    # Initialize flags
    ctx.storage.set(DEPOSIT_CONFIRMED_FLAG, False)
    ctx.storage.set(PAYMENT_ATTEMPTED_FLAG, False)

    # 1. Register Agent with TransactAI
    ctx.logger.info("Registering agent with TransactAI...")
    register_msg = create_metadata_message({'command': 'register'})
    await ctx.send(TRANSACTAI_ADDRESS, register_msg)
    await asyncio.sleep(2.0) # Wait for agent registration

    # 2. Register Wallet with TransactAI
    ctx.logger.info("Registering wallet with TransactAI...")
    wallet_address = str(alice.wallet.address()) # Get Alice's wallet address
    register_wallet_msg = create_metadata_message({
        'command': 'register_wallet',
        'wallet_address': wallet_address
    })
    await ctx.send(TRANSACTAI_ADDRESS, register_wallet_msg)
    await asyncio.sleep(5.0) # Wait for wallet registration

    # 3. On-chain deposit to TransactAI wallet
    ctx.logger.info("Sending on-chain deposit to TransactAI wallet...")
    deposit_amount = 100000000000000000 # 0.1 testfet (needs enough for payment)
    tx_hash = None
    try:
        ledger = get_ledger("dorado") # Get ledger instance right before use
        # Ensure wallet has funds from faucet: https://companion.fetch.ai/dorado-1/accounts
        ctx.logger.info(f"Attempting to send {deposit_amount} atestfet to {TRANSACTAI_WALLET}")
        tx = ledger.send_tokens(TRANSACTAI_WALLET, deposit_amount, "atestfet", alice.wallet)
        result = tx.wait_to_complete()
        tx_hash = result.tx_hash
        ctx.logger.info(f"Deposit transaction hash: {tx_hash}")
    except Exception as e:
        ctx.logger.error(f"Error sending on-chain deposit: {e}")
        ctx.logger.error("Ensure Alice's wallet has sufficient 'atestfet' from the faucet.")
        return

    # 4. Send deposit confirmation command to TransactAI
    if tx_hash:
        ctx.logger.info(f"Sending deposit confirmation command for tx_hash: {tx_hash}")
        deposit_confirm_msg = create_metadata_message({
            'command': 'deposit',
            'tx_hash': tx_hash,
            'amount': str(deposit_amount),
            'denom': "atestfet"
        })
        await ctx.send(TRANSACTAI_ADDRESS, deposit_confirm_msg)

        # Wait for deposit confirmation state change
        MAX_WAIT_TIME = 60 # seconds
        WAIT_INTERVAL = 5 # seconds
        time_waited = 0
        deposit_confirmed = False
        while time_waited < MAX_WAIT_TIME:
            if ctx.storage.get(DEPOSIT_CONFIRMED_FLAG) is True:
                deposit_confirmed = True
                ctx.logger.info("Deposit confirmed by TransactAI.")
                break
            ctx.logger.info(f"Waiting for deposit confirmation... ({time_waited}/{MAX_WAIT_TIME}s)")
            await asyncio.sleep(WAIT_INTERVAL)
            time_waited += WAIT_INTERVAL

        if not deposit_confirmed:
            ctx.logger.error("Timed out waiting for deposit confirmation from TransactAI.")
            return # Stop if deposit not confirmed

    else:
        ctx.logger.error("On-chain deposit failed, cannot proceed.")
        return # Stop if deposit failed

    # 5. Send payment to Bob via TransactAI (only if deposit confirmed and payment not already attempted)
    # This part is triggered by handle_transactai_response upon successful deposit confirmation
    # We call maybe_send_payment here just in case the confirmation message arrived *during* the wait loop
    await maybe_send_payment(ctx)


# Handle responses from TransactAI
@agent_proto.on_message(model=AgentMessage)
async def handle_transactai_response(ctx: Context, sender: str, msg: AgentMessage):
    ctx.logger.info(f"Received message from {sender}")
    response_handled = False # Flag to ensure ack is sent even if no specific handler matches
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata
            ctx.logger.info(f"Metadata: {metadata}")
            
            command = metadata.get('command')
            status = metadata.get('status')

            if command == 'register_response':
                 ctx.logger.info(f"Registration response: {status}")
                 response_handled = True
            elif command == 'register_wallet_response':
                 ctx.logger.info(f"Wallet registration response: {status}")
                 response_handled = True
            elif command == 'deposit_response':
                 ctx.logger.info(f"Deposit response received: {metadata}")
                 if status == 'success':
                     ctx.storage.set(DEPOSIT_CONFIRMED_FLAG, True)
                     # If payment hasn't been attempted yet, trigger it now
                     asyncio.create_task(maybe_send_payment(ctx))
                 elif status == 'pending_confirmation':
                     ctx.logger.info("Deposit is still pending confirmation.")
                 else: # Failed
                     ctx.logger.error(f"Deposit failed: {metadata.get('reason')}")
                     # Consider setting a 'deposit_failed' flag if needed
                 response_handled = True
            elif command == 'payment_confirmation':
                 if status == 'success':
                     ctx.logger.info(f"Payment successful! New balance: {metadata.get('balance')}")
                 else:
                     ctx.logger.error(f"Payment failed! Reason: {metadata.get('reason')}, Balance: {metadata.get('balance')}")
                 response_handled = True
            # Handle other responses if needed (e.g., balance_response)
        
        elif content.type == "text":
            ctx.logger.info(f"Text: {content.text}")
            response_handled = True # Acknowledge text messages too

    # Send acknowledgement back to TransactAI if message was processed
    if response_handled:
        await ctx.send(sender, AgentAcknowledgement(
            timestamp=datetime.utcnow(),
            acknowledged_msg_id=msg.msg_id
        ))
    else:
        ctx.logger.warning(f"Received unhandled message content types from {sender}: {[c.type for c in msg.content]}")


# Separate function to attempt payment after deposit confirmation
async def maybe_send_payment(ctx: Context):
    # Ensure deposit is confirmed and payment hasn't been attempted
    if ctx.storage.get(DEPOSIT_CONFIRMED_FLAG) is True and not ctx.storage.get(PAYMENT_ATTEMPTED_FLAG):
        payment_amount = 100000000000000000 # Example amount (0.1 atestfet)
        ctx.logger.info(f"Deposit confirmed, now attempting to pay {payment_amount} to Bob ({BOB_ADDRESS})...")
        ctx.storage.set(PAYMENT_ATTEMPTED_FLAG, True) # Mark as attempted
        payment_msg = create_metadata_message({
            'command': 'payment',
            'recipient': BOB_ADDRESS,
            'amount': str(payment_amount),
            'reference': f"payment-{datetime.utcnow().isoformat()}"
        })
        await ctx.send(TRANSACTAI_ADDRESS, payment_msg)

# Handle acknowledgements (optional)
@agent_proto.on_message(model=AgentAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: AgentAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

# Include the protocol
alice.include(agent_proto)

if __name__ == "__main__":
    print(f"Alice starting. Address: {alice.address}")
    print("Ensure agent_protocol.py is accessible.")
    print("CRITICAL: Replace the example ALICE_SEED in the code if using for anything beyond this demo.")
    alice.run()
```

### Bob (Receiver) Agent

```python title='bob_agent.py'
"""
Bob Agent - Receives payments via TransactAI
"""

import asyncio
from uagents import Agent, Context
from datetime import datetime

# Import the custom agent protocol
from agent_protocol import (
    agent_proto,
    AgentMessage,
    AgentAcknowledgement,
    create_metadata_message
)

# TransactAI agent address (ensure this is correct)
TRANSACTAI_ADDRESS = "agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq"

# Bob agent setup
bob = Agent()

@bob.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Bob started. Address: {bob.address}")
    ctx.logger.info(f"Wallet address: {bob.wallet.address()}")

    # Give agents time to register etc.
    await asyncio.sleep(5.0)

    # 1. Register Agent with TransactAI
    ctx.logger.info("Registering agent with TransactAI...")
    register_msg = create_metadata_message({'command': 'register'})
    await ctx.send(TRANSACTAI_ADDRESS, register_msg)
    await asyncio.sleep(2.0) # Wait briefly

    # 2. Register Wallet with TransactAI
    ctx.logger.info("Registering wallet with TransactAI...")
    wallet_address = str(bob.wallet.address()) # Get Bob's wallet address
    register_wallet_msg = create_metadata_message({
        'command': 'register_wallet',
        'wallet_address': wallet_address
    })
    await ctx.send(TRANSACTAI_ADDRESS, register_wallet_msg)
    await asyncio.sleep(2.0) # Wait briefly

# Handle responses/notifications from TransactAI
@agent_proto.on_message(model=AgentMessage)
async def handle_transactai_message(ctx: Context, sender: str, msg: AgentMessage):
    ctx.logger.info(f"Received message from {sender}")
    for content in msg.content:
        if content.type == "metadata":
            metadata = content.metadata
            ctx.logger.info(f"Metadata: {metadata}")
            
            command = metadata.get('command')
            status = metadata.get('status')

            if command == 'register_response':
                 ctx.logger.info(f"Registration response: {status}")
            elif command == 'payment_received':
                 ctx.logger.info(f"Payment received from {metadata.get('from')}!")
                 amount_received_str = metadata.get('amount')
                 ctx.logger.info(f"Amount: {amount_received_str}, Reference: {metadata.get('reference')}")
                 ctx.logger.info(f"New balance: {metadata.get('balance')}")

                 # Attempt to withdraw the received amount
                 try:
                     amount_to_withdraw = int(amount_received_str)
                     if amount_to_withdraw > 0:
                         ctx.logger.info(f"Attempting to withdraw received amount: {amount_to_withdraw}")
                         withdraw_msg = create_metadata_message({
                             'command': 'withdraw',
                             'amount': str(amount_to_withdraw),
                             'wallet_address': str(bob.wallet.address()), # Bob's own wallet
                             'denom': "atestfet"
                         })
                         # Send withdrawal request asynchronously
                         asyncio.create_task(ctx.send(TRANSACTAI_ADDRESS, withdraw_msg))
                     else:
                         ctx.logger.info("Received payment amount is zero or invalid, not withdrawing.")
                 except (ValueError, TypeError) as e:
                     ctx.logger.error(f"Could not parse amount for withdrawal: {amount_received_str}, Error: {e}")

            elif command == 'withdraw_confirmation':
                 ctx.logger.info(f"Withdrawal confirmation received: {metadata}")
                 if status == 'success':
                     ctx.logger.info(f"Withdrawal successful! Tx: {metadata.get('tx_hash')}, New balance: {metadata.get('balance')}")
                 else:
                     ctx.logger.error(f"Withdrawal failed! Reason: {metadata.get('reason')}")

            # Handle other relevant messages like escrow notifications if needed
        
        elif content.type == "text":
            ctx.logger.info(f"Text: {content.text}")

    # Send acknowledgement back to TransactAI
    await ctx.send(sender, AgentAcknowledgement(
        timestamp=datetime.utcnow(),
        acknowledged_msg_id=msg.msg_id
    ))

# Handle acknowledgements (optional)
@agent_proto.on_message(model=AgentAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: AgentAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message {msg.acknowledged_msg_id}")

# Include the protocol
bob.include(agent_proto)

if __name__ == "__main__":
    print(f"Bob starting. Address: {bob.address}")
    bob.run()
```

## Running the Example

To run this example:

1. Create two agents Alice and Bob on Agentverse. 
2. Create `agent_protocol.py` in both the agents and put in the code from above. 
3. Get some test tokens for the sender's wallet from the [Fetch.ai Dorado Faucet](https://companion.fetch.ai/dorado-1/accounts)
4. Start the receiver agent (bob) first from agentverse.
5. Copy the bob's address and update `RECIPIENT_ADDRESS` in alice's agent.py
6. Start the alice agent as well.

## Expected Output

### Receiver Output (Bob)

```
Receiver agent started. Address: agent1q2v8ck694z7h6qww90kvv4qafrnvlaquwpeuqtarsyhdmsve4v6k7r0a8l0
Wallet address: fetch1ljd6tn7kr27wv0jwn6g63a7x38zj5ltfvwm8dw
Registering with TransactAI...
Registering wallet fetch1ljd6tn7kr27wv0jwn6g63a7x38zj5ltfvwm8dw...
✅ Setup complete - Ready to receive payments
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'register_response', 'status': 'success', 'balance': '0'}
Registration response: success
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'register_wallet_response', 'status': 'success', 'wallet_address': 'fetch1ljd6tn7kr27wv0jwn6g63a7x38zj5ltfvwm8dw'}
Wallet registration response: success
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'payment_received', 'from': 'agent1q2gxyqnwyr85v6ek7rplk09etnqgn4cfllph6gx3gtsuqzzn5p856gway5s', 'amount': '50000000000000000', 'reference': 'Example payment 2025-04-29T13:18:27.441861', 'balance': '5.0E+16'}
💰 Payment received!
  From: agent1q2gxyqnwyr85v6ek7rplk09etnqgn4cfllph6gx3gtsuqzzn5p856gway5s
  Amount: 50000000000000000 atestfet
  Reference: Example payment 2025-04-29T13:18:27.441861
  New balance: 5.0E+16
Withdrawing 50000000000000000 atestfet to fetch1ljd6tn7kr27wv0jwn6g63a7x38zj5ltfvwm8dw...
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'withdraw_confirmation', 'status': 'success', 'amount': '50000000000000000', 'wallet_address': 'fetch1ljd6tn7kr27wv0jwn6g63a7x38zj5ltfvwm8dw', 'tx_hash': 'A44295DCE532825CE257D63C79A63C01180FCC8DEF44258271C5E5FB9AE0F561', 'balance': '0', 'message': 'Withdrawal processed. Funds sent to your wallet.'}
✅ Withdrawal successful!
  Transaction hash: A44295DCE532825CE257D63C79A63C01180FCC8DEF44258271C5E5FB9AE0F561
  New balance: 0
```

### Sender Output

```
Sender agent started. Address: agent1q2gxyqnwyr85v6ek7rplk09etnqgn4cfllph6gx3gtsuqzzn5p856gway5s
Wallet address: fetch1n9vnna29c8us5pk9fxqhzltmgpeyn3hl4le28h
Registering with TransactAI...
Registering wallet fetch1n9vnna29c8us5pk9fxqhzltmgpeyn3hl4le28h...
Making on-chain deposit of 100000000000000000 atestfet...
Attempting to send 100000000000000000 atestfet to fetch1uyxsdlejg7axp4dzmqpq54g0uwde5nv6fflhkv
Deposit transaction hash: AE4A482EFE4215D6A54C63D1F4EE9EFA50437572BDECBD347FAA752BD9B3E0FA
Waiting for deposit confirmation... (0/60s)
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'register_response', 'status': 'success', 'balance': '0'}
Registration response: success
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'register_wallet_response', 'status': 'success', 'wallet_address': 'fetch1n9vnna29c8us5pk9fxqhzltmgpeyn3hl4le28h'}
Wallet registration response: success
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'deposit_response', 'status': 'pending_confirmation', 'reason': 'Awaiting confirmations (2/6)'}
Deposit pending: Awaiting confirmations (2/6)
Waiting for deposit confirmation... (5/60s)
Waiting for deposit confirmation... (10/60s)
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'deposit_response', 'status': 'success', 'amount': '100000000000000000', 'denom': 'atestfet', 'balance': '1.0E+17', 'tx_hash': 'AE4A482EFE4215D6A54C63D1F4EE9EFA50437572BDECBD347FAA752BD9B3E0FA'}
Deposit confirmed! New balance: 1.0E+17
✅ Deposit confirmed!
Sending payment of 50000000000000000 atestfet to agent1q2v8ck694z7h6qww90kvv4qafrnvlaquwpeuqtarsyhdmsve4v6k7r0a8l0...
Received message from agent1qtdvskm3g5ngmvfuqek6shrpjz6ed8jc84s6phmark05z5a8naxawu5jsrq
Metadata: {'command': 'payment_confirmation', 'status': 'success', 'recipient': 'agent1q2v8ck694z7h6qww90kvv4qafrnvlaquwpeuqtarsyhdmsve4v6k7r0a8l0', 'amount': '50000000000000000', 'balance': '5.0E+16'}
Payment successful! New balance: 5.0E+16
```

## Additional Features

In addition to basic payments, TransactAI also supports:

- **Escrow Services**: Hold funds conditionally until released by the sender
- **Balance Queries**: Check your current balance at any time
- **Automated Withdrawals**: Set up automatic withdrawals for received payments

Refer to the complete [TransactAI documentation](../../agent-transaction/transactai.md) for more details on these advanced features. 