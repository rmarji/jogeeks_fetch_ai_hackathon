---
id: asi-defi-ai-agent
title: DeFi AI Agent Starter Guide
---

# DeFi AI Agent Starter Guide

This guide demonstrates how to create a multi-agent system for DeFi analysis using the uAgents framework and ASI1 Mini. The system helps decide whether to hold or sell a long-term crypto asset based on market data and sentiment analysis.

## Overview


This project showcases how to build a DeFi analysis system using multiple agents:

- **Fear and Greed Index (FGI) Agent**: Fetches and analyzes market sentiment data
- **Coin Info Agent**: Retrieves cryptocurrency market data
- **Main Agent**: Coordinates between agents and makes trading decisions using ASI1 Mini

## Prerequisites

Before running this project, ensure you have:

- Python 3.11 installed
- uAgents library installed:
  ```bash
  pip install uagents
  ```
- Required Python packages:
  ```bash
  pip install requests pydantic python-dotenv
  ```
- API Keys:
  - CoinMarketCap [API key](https://coinmarketcap.com/academy/article/register-for-coinmarketcap-api) for FGI data
  - ASI1 [API key](https://asi1.ai/dashboard/api-keys) for AI analysis


## Project Structure

Your project structure should look like this:

```
defi-ai-agent/
├── .env                    # Environment variables
├── main.py                # Main agent script
└── asi/
    ├── __init__.py       # Empty file to make asi a package
    └── llm.py            # ASI1 LLM implementation
```

:::note
**Note:** `FGI Agent` and `Coin Info Agent` are Hosted on [Agentverse](https://agentverse.ai/).
::: 

## FGI Agent Script

The Fear and Greed Index Agent fetches market sentiment data from CoinMarketCap.

### Script Breakdown (fgi-agent/agent.py)

#### Importing Required Libraries

```python
import os
from uagents import Agent, Context, Model
import requests
from datetime import datetime
from typing import Optional
```

#### Defining Data Models

```python
class FGIRequest(Model):
    limit: Optional[int] = 1

class FearGreedData(Model):
    value: float
    value_classification: str
    timestamp: str

class FGIResponse(Model):
    data: list[FearGreedData]
    status: str
    timestamp: str
```

#### Initializing the FGI Agent

```python
agent = Agent()
```

#### API Integration Function

```python
def get_fear_and_greed_index(limit: int = 1) -> FGIResponse:
    """Fetch Fear and Greed index data from CoinMarketCap API"""
    url = "https://pro-api.coinmarketcap.com/v3/fear-and-greed/historical"
    api_key = CMC_API_KEY
    
    headers = {
        "X-CMC_PRO_API_KEY": api_key
    }
    
    params = {
        "limit": limit
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        raw_data = response.json()
        fear_greed_data = []
        
        for entry in raw_data["data"]:
            data = FearGreedData(
                value=entry["value"],
                value_classification=entry["value_classification"],
                timestamp=entry["timestamp"]
            )
            fear_greed_data.append(data)
        
        return FGIResponse(
            data=fear_greed_data,
            status="success",
            timestamp=datetime.utcnow().isoformat()
        )
    else:
        raise Exception(f"Error fetching data: {response.json()['status']['error_message']}")

async def process_response(ctx: Context, msg: FGIRequest) -> FGIResponse:
    """Process the request and return formatted response"""
    fear_greed_data = get_fear_and_greed_index(msg.limit)
    
    for entry in fear_greed_data.data:
        ctx.logger.info(f"Fear and Greed Index: {entry.value}")
        ctx.logger.info(f"Classification: {entry.value_classification}")
        ctx.logger.info(f"Timestamp: {entry.timestamp}")
    
    return fear_greed_data
```

#### Event Handlers

```python
@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize agent with a test request"""
    ctx.logger.info(f"Hello, I'm a Fear and Greed Index agent and my address is {ctx.agent.address}.")
    dummy_request = FGIRequest(limit=1)
    await process_response(ctx, dummy_request)

@agent.on_message(model=FGIRequest)
async def handle_message(ctx: Context, sender: str, msg: FGIRequest):
    """Handle incoming messages requesting Fear and Greed index data"""
    ctx.logger.info(f"Received message from {sender}: FGIRequest for {msg.limit} entries")
    
    response = await process_response(ctx, msg)
    await ctx.send(sender, response)
    
    return response
```

:::note
**Note:** This is an hosted agent on [Agentverse](https://agentverse.ai/). This is the reason we have not provided `name, seed, endpoint` and `port` to the agent.

**Note:** Store `CMC_API_KEY` in the agent secret of your hosted Agent.
::: 

## Coin Info Agent Script

The Coin Info Agent fetches cryptocurrency market data from CoinGecko.

### Script Breakdown (coin-info-agent/agent.py)

#### Importing Required Libraries

```python
import os
from uagents import Agent, Context, Model
import requests
```

#### Defining Data Models

```python
class CoinRequest(Model):
    coin_id: str

class CoinResponse(Model):
    name: str
    symbol: str
    current_price: float
    market_cap: float
    total_volume: float
    price_change_24h: float
```

#### Initializing the Coin Info Agent

```python
agent = Agent()
```

#### API Integration Function

```python
def get_crypto_info(coin_id: str) -> CoinResponse:
    """Fetch cryptocurrency information from CoinGecko API"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        return CoinResponse(
            name=data['name'],
            symbol=data['symbol'].upper(),
            current_price=data['market_data']['current_price']['usd'],
            market_cap=data['market_data']['market_cap']['usd'],
            total_volume=data['market_data']['total_volume']['usd'],
            price_change_24h=data['market_data']['price_change_percentage_24h']
        )
    else:
        raise Exception(f"Failed to get crypto info: {response.text}")

async def process_response(ctx: Context, msg: CoinRequest) -> CoinResponse:
    """Process the crypto request and return formatted response"""
    crypto_data = get_crypto_info(msg.coin_id)
    ctx.logger.info(f"Crypto data: {crypto_data}")
    return crypto_data


```

#### Event Handlers

```python
@agent.on_event("startup")
async def startup(ctx: Context):
    """Initialize agent with a test request for Bitcoin data"""
    ctx.logger.info(f"Hello, I'm a crypto agent and my address is {ctx.agent.address}.")

@agent.on_message(model=CoinRequest)
async def handle_message(ctx: Context, sender: str, msg: CoinRequest):
    """Handle incoming messages requesting crypto information"""
    ctx.logger.info(f"Received message from {sender}: {msg.coin_id}")
    
    response = await process_response(ctx, msg)
    await ctx.send(sender, response)
    
    return response
```

:::note
**Note:** This is an hosted agent on [Agentverse](https://agentverse.ai/). This is the reason we have not provided `name, seed, endpoint` and `port` to the agent.
::: 

## ASI1 LLM Implementation

Create a new file called `asi/llm.py` with the following code:

```python
import requests
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("ASI1_LLM_API_KEY")

# ASI1-Mini LLM API endpoint
url = "https://api.asi1.ai/v1/chat/completions"

# Define headers for API requests, including authentication
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

def query_llm(query):
    """
    Queries the ASI1-Mini LLM with a given prompt and returns the model's response.

    Parameters:
        query (str): The input question or statement for the language model.

    Returns:
        str: The response from the LLM.
    
    If an error occurs during the request, the function returns the exception object.
    """
    data = {
        "messages": [{"role": "user", "content": query}],  # User input for the chat model
        "conversationId": None,  # No conversation history tracking
        "model": "asi1-mini"  # Specifies the model version to use
    }

    try:
        # Send a POST request to the LLM API with the input query
        with requests.post(url, headers=headers, json=data) as response:
            output = response.json()  # Parse the JSON response

            # Extract and return the generated message content
            return output["choices"][0]["message"]["content"]
    
    except requests.exceptions.RequestException as e:
        # Handle and return any request-related exceptions (e.g., network errors)
        return str(e)
```

Make sure to create the `asi` directory and include an empty `__init__.py` file to make it a Python package.

## Main Agent Script

The Main Agent coordinates between the FGI and Coin Info agents, using ASI1 Mini for decision-making.

### Script Breakdown (main.py)

#### Importing Required Libraries

```python
from uagents import Agent, Context, Model
from typing import Optional
from asi.llm import query_llm
```

#### Agent Configuration and Data Models

```python
# Initialize the agent with a name and mailbox enabled for communication
agent = Agent(name="Sentiment-Based Crypto Sell Alerts Agent", mailbox=True,port = 8001)

# Coin to monitor
COIN_ID = "bitcoin"

# Agentverse agent addresses
COIN_AGENT = "agent1q0005tewegtmkruc9s3v2zz8p45dd68hu38zurgpwjrrj94h8sl5cz0qev5" #Update this with your Coin agent address on Agentverse
FGI_AGENT = "agent1q2eln9t0c70ha0z8uz6q88mrdzsdkxfmk3zmjejecv7skf4844cpvzplp02" #Update this with your FGI agent address on Agentverse

### AGENTVERSE INTERACTION CLASSES ###
# Request model for retrieving coin data
class CoinRequest(Model):
    coin_id: str

# Response model for coin data
class CoinResponse(Model):
    name: str
    symbol: str
    current_price: float
    market_cap: float
    total_volume: float
    price_change_24h: float

# Request model for Fear Greed Index (FGI) data
class FGIRequest(Model):
    limit: Optional[int] = 1

# Model for individual FGI data points
class FearGreedData(Model):
    value: float
    value_classification: str
    timestamp: str

# Response model for FGI data
class FGIResponse(Model):
    data: list[FearGreedData]
    status: str
    timestamp: str

```

#### Event Handlers

```python
@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    """Introduces the agent when it starts running."""
    print(f"Hello! I'm {agent.name} and my address is {agent.address}.")

@agent.on_interval(period=24 * 60 * 60.0)  # Runs every 24 hours
async def check_coin(ctx: Context):
    """Requests market data for the monitored coin once a day."""
    await ctx.send(COIN_AGENT, CoinRequest(coin_id=COIN_ID))

@agent.on_message(model=CoinResponse)
async def handle_coin_response(ctx: Context, sender: str, msg: CoinResponse):
    """Handles incoming coin market data and requests FGI data if the price drop exceeds 10%."""
    global market_data
    market_data = msg
    
    # Check if price has dropped by 10% or more before requesting FGI analysis
    if msg.price_change_24h <= -10.0:
        await ctx.send(FGI_AGENT, FGIRequest())

@agent.on_message(model=FGIResponse)
async def handle_fgi_response(ctx: Context, sender: str, msg: FGIResponse):
    """Analyzes Fear Greed Index data and determines whether to issue a SELL alert."""
    global fgi_analysis
    fgi_analysis = msg
    
    # Construct the AI prompt based on current market and sentiment analysis
    prompt = f'''
    Given the following information, respond with either SELL or HOLD for the coin {COIN_ID}.
    
    Below is analysis on the Fear Greed Index:
    {fgi_analysis}
    
    Below is analysis on the coin:
    {market_data}
    '''
    
    response = query_llm(prompt)  # Query ASI1 Mini for a decision
    
    # Interpret the AI response and print decision
    if "SELL" in response:
        print("SELL")
    else:
        print("HOLD")
```

## Running the System

__1. Start the FGI Agent__

Open a blank agent on AV and write your [script](#coin-info-agent-script) in it. Click on `Start Agent` button.


You should see output similar to:

```
INFO: Hello, I'm a Fear and Greed Index agent and my address is agent1q2eln9t0c70ha0z8uz6q88mrdzsdkxfmk3zmjejecv7skf4844cpvzplp02
```

__2. Start the Coin Info Agent__

Open another blank agent on AV and write your [script](#fgi-agent-script) in it. Click on `Start Agent` button.

You should see output similar to:

```
INFO: Hello, I'm a crypto agent and my address is agent1q0005tewegtmkruc9s3v2zz8p45dd68hu38zurgpwjrrj94h8sl5cz0qev5
```

__3. Start the Main Agent__

Open a terminal window and run:

```bash
python main.py
```

You should see output similar to:

```
Hello! I'm Sentiment-Based Crypto Sell Alerts Agent and my address is agent1qxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

__4. Monitor the System__

The main agent will:
1. Check cryptocurrency prices every 24 hours
2. Request FGI analysis if price drops by 10% or more
3. Use ASI1 Mini to analyze data and make SELL/HOLD recommendations

## Troubleshooting Common Issues

### API Key Issues

If you see API-related errors:

1. Verify your API keys are correctly set in the `.env` files
2. Check API rate limits and quotas
3. Ensure the API services are operational

### Agent Communication Issues

If agents aren't communicating:

1. Verify all agents are running
2. Check agent addresses in `main.py` match the actual addresses
3. Ensure network connectivity

### ASI1 Mini Integration Issues

If AI analysis isn't working:

1. Check ASI1_API_KEY is set correctly
2. Verify ASI1 Mini service status
3. Review prompt formatting in `main.py`

## Benefits of DeFi AI Agent System

- **Automated Monitoring**: 24/7 tracking of cryptocurrency prices
- **Data-Driven Decisions**: Combines market data with sentiment analysis
- **AI-Powered Analysis**: Leverages ASI1 Mini for objective decision-making
- **Scalable Architecture**: Easy to add more data sources and analysis types
- **Real-time Alerts**: Immediate notification of significant market events

## GitHub Repository

For the complete code, visit the [DeFi AI Agent Repository](https://github.com/RoyceBraden/DeFI-Agent-Starter/tree/main).

:::note
**Note:** You can learn more about ASI1 Mini APIs [__here__](https://docs.asi1.ai/docs/) and about uAgents [__here__](../../agent-creation/uagent-creation.mdx).
::: 