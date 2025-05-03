---
id: bnb-chain-agents
title: BNB Chain Agents
---


# BNB Chain Agents

This guide demonstrates how to create and use AI agents for interacting with the BNB Chain using uAgents. We'll build a system of three agents that work together to send transactions, validate them, and monitor wallet activity.

## Overview

The system consists of three main agents:

1. **Transaction Sender Agent (Agent1)**: Handles BNB transfer requests and initiates transactions
2. **Transaction Validator Agent (Agent2)**: Verifies transaction status using BscScan API
3. **Wallet Monitor Agent**: Monitors specified wallet addresses for any transaction activity

## Prerequisites

Before getting started, you'll need:

- Python 3.11 or higher
- A BNB Testnet account with some test BNB
- [BscScan API Key](https://docs.bscscan.com/getting-started/viewing-api-usage-statistics)
- Basic understanding of Web3 and blockchain concepts

## Architecture Diagram
 
 <div style={{ textAlign: 'center' }}>
   <img src="/resources/img/id-images/BNBChain-light.png" alt="comparison" style={{ width: '100%', maxWidth: '1000px' }} />
 </div>

## Installation

1. Create a new directory and set up your virtual environment:

```bash
mkdir bnb-chain-agents
cd bnb-chain-agents
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

2. Install the required packages:

```bash
pip install uagents web3 python-dotenv requests
```

3. Create a `.env` file with your credentials:

```env
USER_WALLET=your_wallet_address
USER_KEY=your_private_key
BSCSCAN_API_KEY=your_bscscan_api_key
```

## Implementation

### 1. Transaction Sender Agent (agent1.py)

This agent handles BNB transfer requests and communicates with the validator agent:

```python
from uagents import Agent, Context, Model
from web3 import Web3
from web3.middleware import geth_poa_middleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

agent_user = Agent(
    name='User BNB Agent to make transactions',
    port=8000,
    endpoint=['http://localhost:8000/submit']
)

class RequestTransfer(Model):
    to_address: str
    amount: float
    agent_to_address: str

class RequestDetails(Model):
    tx_hash: str

class ResponseTransfer(Model):
    response: str

# Connect to BNB Chain Testnet
provider_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
web3 = Web3(Web3.HTTPProvider(provider_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

@agent_user.on_rest_post("/send/bnb", RequestTransfer, ResponseTransfer)
async def handle_post(ctx: Context, req: RequestTransfer) -> ResponseTransfer:
    try:
        # Get wallet credentials
        user_wallet = os.getenv("USER_WALLET")
        user_key = os.getenv("USER_KEY")
        
        # Prepare transaction
        to_address = web3.to_checksum_address(req.to_address)
        nonce = web3.eth.get_transaction_count(user_wallet)
        
        tx = {
            'to': to_address,
            'value': web3.to_wei(req.amount, 'ether'),
            'gas': 21000,
            'gasPrice': web3.eth.gas_price,
            'nonce': nonce,
            'chainId': 97  # BNB Testnet
        }

        # Sign and send transaction
        signed_tx = web3.eth.account.sign_transaction(tx, user_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Send to validator agent
        message, status = await ctx.send_and_receive(
            req.agent_to_address,
            RequestDetails(tx_hash=web3.to_hex(tx_hash)),
            response_type=ResponseTransfer
        )
        
        return ResponseTransfer(response=message.response)
    
    except Exception as e:
        return ResponseTransfer(response=f"Transaction Failed: {str(e)}")

if __name__ == "__main__":
    agent_user.run()
```

### 2. Transaction Validator Agent (agent2.py)

This agent verifies transaction status using the BscScan API:

```python
from uagents import Agent, Context, Model
from web3 import Web3
import os
from dotenv import load_dotenv
import asyncio
import requests

agent_dummy = Agent(
    name='Dummy BNB Agent to make transactions',
    port=8001,
    endpoint=['http://localhost:8001/submit']
)

load_dotenv()
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")

class RequestDetails(Model):
    tx_hash: str

class ResponseTransfer(Model):
    response: str

async def get_transaction_status(tx_hash: str) -> dict:
    base_url = "https://api.bscscan.com/api"
    params = {
        "module": "transaction",
        "action": "getstatus",
        "txhash": tx_hash,
        "apikey": BSCSCAN_API_KEY
    }
    
    response = await asyncio.to_thread(requests.get, base_url, params=params)
    return response.json() if response.status_code == 200 else {"error": f"HTTP error {response.status_code}"}

@agent_dummy.on_message(model=RequestDetails, replies={ResponseTransfer})
async def startup_handler(ctx: Context, sender: str, msg: RequestDetails):
    tx_status = await get_transaction_status(msg.tx_hash)
    
    if "error" in tx_status:
        reply = f"API Error: {tx_status['error']}"
    else:
        if tx_status.get("status") == "1" and tx_status.get("message") == "OK":
            if tx_status["result"].get("isError") == "0":
                reply = f"Successful transfer confirmed by receiver.✅ tx_hash: {msg.tx_hash}"
            else:
                err_desc = tx_status["result"].get("errDescription", "Unknown error")
                reply = f"Transfer rejected: {err_desc}"
        else:
            reply = "Transfer status unknown or API response error."

    await ctx.send(sender, ResponseTransfer(response=reply))

if __name__ == "__main__":
    agent_dummy.run()
```

### 3. Wallet Monitor Agent (monitor_wallet.py)

This agent monitors wallet activity in real-time:

```python
from uagents import Agent, Context
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
import os
from dotenv import load_dotenv

load_dotenv()
user_wallet = os.getenv("USER_WALLET")

monitor_agent = Agent(
    name='Monitor BNB Agent to monitor address',
    port=8003,
    endpoint=['http://localhost:8003/submit']
)

# Connect to BNB Chain Testnet
provider_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
web3 = Web3(Web3.HTTPProvider(provider_url))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

monitored_address = web3.to_checksum_address(user_wallet)
last_scanned_block = web3.eth.block_number

@monitor_agent.on_interval(period=10)
async def monitor_handler(ctx: Context):
    global last_scanned_block

    try:
        current_block = web3.eth.block_number
        if current_block <= last_scanned_block:
            return

        for block_num in range(last_scanned_block + 1, current_block + 1):
            block = web3.eth.get_block(block_num, full_transactions=True)
            for tx in block['transactions']:
                tx_from = tx['from']
                tx_to = tx['to']
                
                if (tx_from and tx_from.lower() == monitored_address.lower()) or \
                   (tx_to and tx_to.lower() == monitored_address.lower()):
                    details = {
                        "blockNumber": block_num,
                        "hash": tx['hash'].hex(),
                        "from": tx_from,
                        "to": tx_to if tx_to else "Contract Creation",
                        "value": str(web3.from_wei(tx['value'], 'ether')) + " BNB"
                    }
                    ctx.logger.info(f"Recorded transaction: {json.dumps(details, indent=2)}")

        last_scanned_block = current_block

    except Exception as e:
        ctx.logger.error(f"Error during monitoring: {e}")

if __name__ == "__main__":
    monitor_agent.run()
```

## Usage

1. Start all three agents in separate terminal windows:

```bash
# Terminal 1
python agent1.py

# Terminal 2
python agent2.py

# Terminal 3
python monitor_wallet.py
```

2. Send a BNB transfer request using curl:

```bash
curl -d '{
    "to_address": "RECIPIENT_ADDRESS",
    "amount": 0.01,
    "agent_to_address": "AGENT2_ADDRESS"
}' \
-H "Content-Type: application/json" \
-X POST http://localhost:8000/send/bnb
```

Replace `RECIPIENT_ADDRESS` with the destination wallet address and `AGENT2_ADDRESS` with the address of your validator agent.

## System Flow

1. The Transaction Sender Agent receives a transfer request via HTTP POST
2. It creates and signs the transaction using the private key
3. The transaction is sent to the BNB Chain Testnet
4. The transaction hash is forwarded to the Validator Agent
5. The Validator Agent checks the transaction status using BscScan API
6. The Wallet Monitor Agent continuously scans for new transactions
7. All agents log their activities and transaction details

## Best Practices

1. **Security**:
   - Never commit your `.env` file or expose private keys
   - Use environment variables for sensitive data
   - Validate input data before processing

2. **Error Handling**:
   - Implement proper error handling for API calls
   - Log errors and transaction details
   - Provide meaningful error messages

3. **Monitoring**:
   - Use the monitoring agent to track transactions
   - Implement alerts for suspicious activities
   - Keep logs for auditing purposes

## Conclusion

This example demonstrates how to create a system of AI agents that interact with the BNB Chain. The agents work together to handle transactions, validate them, and monitor wallet activity. This system can be extended to include more complex functionality like smart contract interactions, automated trading, or blockchain analytics. 