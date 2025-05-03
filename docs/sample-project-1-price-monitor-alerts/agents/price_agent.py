import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.experimental.quota import QuotaProtocol, RateLimit

from protocols.price_data import PriceData, PriceRequest, PriceResponse, PriceUpdate

# Load environment variables
load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("PRICE_AGENT_SEED", "price-agent-seed")
AGENT_PORT = int(os.getenv("PRICE_AGENT_PORT", "8001"))
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"
UPDATE_INTERVAL = int(os.getenv("PRICE_UPDATE_INTERVAL", "300"))  # Default: 5 minutes

# API configuration
# Using free CoinGecko API (no API key required)
DEFAULT_CRYPTOCURRENCIES = os.getenv("DEFAULT_CRYPTOCURRENCIES", "BTC,ETH,SOL,AVAX,DOT").split(",")

# Create the agent
price_agent = Agent(
    name="price-agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

# Create a protocol with rate limiting
price_protocol = QuotaProtocol(
    storage_reference=price_agent.storage,
    name="Price-Data-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=1, max_requests=10),
)


async def fetch_crypto_prices(symbols: List[str]) -> Dict[str, PriceData]:
    """
    Fetch cryptocurrency prices from CoinGecko API.
    
    Args:
        symbols: List of cryptocurrency symbols to fetch prices for
        
    Returns:
        Dictionary mapping symbols to PriceData objects
    """
    # Map symbols to CoinGecko IDs
    symbol_to_id = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "AVAX": "avalanche-2",
        "DOT": "polkadot",
        "FET": "fetch-ai",
        "ADA": "cardano"
    }
    
    # Get CoinGecko IDs for the symbols
    coin_ids = [symbol_to_id.get(s, s.lower()) for s in symbols]
    
    # Join coin IDs with commas for API request
    symbols_str = ",".join(coin_ids)
    
    # CoinGecko API endpoint
    url = f"https://api.coingecko.com/api/v3/simple/price"
    
    # Parameters for the API request
    params = {
        "ids": symbols_str,
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
    }
    
    try:
        # Make the API request using free CoinGecko API
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        data = response.json()
        
        # Create PriceData objects for each symbol
        result = {}
        for symbol, coin_id in zip(symbols, coin_ids):
            if coin_id in data:
                coin_data = data[coin_id]
                result[symbol] = PriceData(
                    symbol=symbol,
                    price=coin_data["usd"],
                    timestamp=datetime.utcnow().isoformat(),
                    volume_24h=coin_data.get("usd_24h_vol"),
                    percent_change_24h=coin_data.get("usd_24h_change"),
                    market_cap=coin_data.get("usd_market_cap"),
                )
        
        return result
    
    except requests.exceptions.RequestException as e:
        # Use print for logging outside of a context
        print(f"Error fetching prices: {e}")
        return {}


@price_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the price agent on startup.
    """
    ctx.logger.info(f"Price Agent started with address: {price_agent.address}")
    ctx.logger.info(f"Monitoring cryptocurrencies: {', '.join(DEFAULT_CRYPTOCURRENCIES)}")
    
    # Initialize storage for historical data if it doesn't exist
    if not ctx.storage.get("historical_data"):
        ctx.storage.set("historical_data", {})
    
    # Initialize storage for subscribed agents if it doesn't exist
    if not ctx.storage.get("subscribed_agents"):
        ctx.storage.set("subscribed_agents", [])


@price_agent.on_interval(period=UPDATE_INTERVAL)
async def update_prices(ctx: Context):
    """
    Fetch and broadcast updated cryptocurrency prices at regular intervals.
    """
    # Get the list of cryptocurrencies to monitor
    monitored_cryptos = ctx.storage.get("monitored_cryptos")
    if monitored_cryptos is None:
        monitored_cryptos = DEFAULT_CRYPTOCURRENCIES
    
    ctx.logger.info(f"Fetching prices for: {', '.join(monitored_cryptos)}")
    
    # Fetch the latest prices
    prices = await fetch_crypto_prices(monitored_cryptos)
    
    if not prices:
        ctx.logger.error("Failed to fetch prices")
        return
    
    # Log the fetched prices
    for symbol, price_data in prices.items():
        ctx.logger.info(f"{symbol}: ${price_data.price:.2f} ({price_data.percent_change_24h:+.2f}% 24h)")
    
    # Update historical data
    historical_data = ctx.storage.get("historical_data")
    if historical_data is None:
        historical_data = {}
    timestamp = datetime.utcnow().isoformat()
    
    for symbol, price_data in prices.items():
        if symbol not in historical_data:
            historical_data[symbol] = []
        
        # Add the new price data to the historical data
        historical_data[symbol].append({
            "price": price_data.price,
            "timestamp": timestamp,
            "volume_24h": price_data.volume_24h,
            "percent_change_24h": price_data.percent_change_24h,
        })
        
        # Keep only the last 100 data points to avoid excessive storage
        if len(historical_data[symbol]) > 100:
            historical_data[symbol] = historical_data[symbol][-100:]
    
    # Save the updated historical data
    ctx.storage.set("historical_data", historical_data)
    
    # Create a price response for all prices
    response = PriceResponse.create(prices=prices, source="CoinGecko")
    
    # Store the latest prices
    ctx.storage.set("latest_prices", response.dict())
    
    # Always send updates to the analysis agent
    analysis_agent_address = os.getenv("ANALYSIS_AGENT_ADDRESS")
    if analysis_agent_address:
        ctx.logger.info(f"Sending price update to analysis agent at {analysis_agent_address}")
        await ctx.send(analysis_agent_address, response)
    
    # Broadcast individual price updates to subscribed agents
    subscribed_agents = ctx.storage.get("subscribed_agents")
    if subscribed_agents is None:
        subscribed_agents = []
    
    for agent_address in subscribed_agents:
        for symbol, price_data in prices.items():
            await ctx.send(agent_address, PriceUpdate(data=price_data))


@price_protocol.on_message(model=PriceRequest, replies={PriceResponse})
async def handle_price_request(ctx: Context, sender: str, msg: PriceRequest):
    """
    Handle requests for cryptocurrency price data.
    """
    ctx.logger.info(f"Received price request from {sender} for: {', '.join(msg.symbols)}")
    
    # Check if we have the latest prices in storage
    latest_prices_dict = ctx.storage.get("latest_prices")
    
    if latest_prices_dict:
        # Convert the stored dictionary back to a PriceResponse object
        latest_prices = PriceResponse(**latest_prices_dict)
        
        # Filter the prices to include only the requested symbols
        filtered_prices = {
            symbol: price_data
            for symbol, price_data in latest_prices.prices.items()
            if symbol in msg.symbols
        }
        
        # If we have all the requested prices, send them immediately
        if len(filtered_prices) == len(msg.symbols):
            response = PriceResponse(
                prices=filtered_prices,
                source=latest_prices.source,
                timestamp=latest_prices.timestamp
            )
            await ctx.send(sender, response)
            return
    
    # If we don't have the latest prices or they don't include all requested symbols,
    # fetch them from the API
    prices = await fetch_crypto_prices(msg.symbols)
    
    if prices:
        response = PriceResponse.create(prices=prices, source="CoinGecko")
        await ctx.send(sender, response)
    else:
        # If we couldn't fetch the prices, send an empty response
        await ctx.send(sender, PriceResponse.create(prices={}, source="Error"))


# Include the protocol in the agent
price_agent.include(price_protocol, publish_manifest=True)


if __name__ == "__main__":
    price_agent.run()
