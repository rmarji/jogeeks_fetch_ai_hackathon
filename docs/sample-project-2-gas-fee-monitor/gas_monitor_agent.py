import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.experimental.quota import QuotaProtocol, RateLimit

from models import (
    GasLevel,
    GasPriceData,
    GasPriceNotification,
    GasPriceThresholds,
    SetThresholdsRequest,
    SetThresholdsResponse,
    GetGasPriceRequest,
    GetGasPriceResponse,
    GetHistoricalDataRequest,
    GetHistoricalDataResponse
)

# Load environment variables
load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("AGENT_SEED", "gas-monitor-agent-seed")
AGENT_PORT = int(os.getenv("AGENT_PORT", "8000"))
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", "60"))  # Default: 1 minute

# Gas price thresholds (in Gwei)
LOW_THRESHOLD = float(os.getenv("LOW_THRESHOLD", "20"))
MEDIUM_THRESHOLD = float(os.getenv("MEDIUM_THRESHOLD", "50"))
HIGH_THRESHOLD = float(os.getenv("HIGH_THRESHOLD", "100"))

# Notification settings
ENABLE_NOTIFICATIONS = os.getenv("ENABLE_NOTIFICATIONS", "true").lower() == "true"

# API Keys
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
INFURA_API_KEY = os.getenv("INFURA_API_KEY", "")
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "")

# Create the agent
gas_monitor_agent = Agent(
    name="gas-monitor-agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

# Create a protocol with rate limiting
gas_monitor_protocol = QuotaProtocol(
    storage_reference=gas_monitor_agent.storage,
    name="Gas-Monitor-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=1, max_requests=10),
)


async def fetch_gas_prices_etherscan() -> Optional[GasPriceData]:
    """
    Fetch Ethereum gas prices from Etherscan API.
    
    Returns:
        GasPriceData object or None if the request fails
    """
    if not ETHERSCAN_API_KEY:
        gas_monitor_agent.logger.warning("Etherscan API key not configured")
        return None
    
    url = f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data["status"] == "1" and data["message"] == "OK":
            result = data["result"]
            
            return GasPriceData.create(
                safe_price=float(result["SafeGasPrice"]),
                propose_price=float(result["ProposeGasPrice"]),
                fast_price=float(result["FastGasPrice"]),
                source="Etherscan"
            )
        else:
            gas_monitor_agent.logger.error(f"Etherscan API error: {data['message']}")
            return None
    
    except requests.exceptions.RequestException as e:
        gas_monitor_agent.logger.error(f"Error fetching gas prices from Etherscan: {e}")
        return None


async def fetch_gas_prices() -> Optional[GasPriceData]:
    """
    Fetch Ethereum gas prices from the configured API.
    Currently only supports Etherscan, but can be extended to support other APIs.
    
    Returns:
        GasPriceData object or None if all requests fail
    """
    # Try Etherscan first
    gas_data = await fetch_gas_prices_etherscan()
    if gas_data:
        return gas_data
    
    # Add support for other APIs here (Infura, Alchemy, etc.)
    
    gas_monitor_agent.logger.error("Failed to fetch gas prices from any API")
    return None


def should_notify(gas_level: GasLevel, previous_level: Optional[GasLevel]) -> bool:
    """
    Determine if a notification should be sent based on the gas level.
    
    Args:
        gas_level: Current gas level
        previous_level: Previous gas level
        
    Returns:
        True if a notification should be sent, False otherwise
    """
    if not ENABLE_NOTIFICATIONS:
        return False
    
    # Always notify on first check
    if previous_level is None:
        return True
    
    # Notify when gas level changes to LOW
    if gas_level == GasLevel.LOW and previous_level != GasLevel.LOW:
        return True
    
    # Notify when gas level changes significantly
    if (previous_level == GasLevel.LOW and gas_level != GasLevel.LOW) or \
       (previous_level == GasLevel.VERY_HIGH and gas_level != GasLevel.VERY_HIGH):
        return True
    
    return False


def get_notification_message(gas_data: GasPriceData, gas_level: GasLevel) -> str:
    """
    Generate a notification message based on the gas level.
    
    Args:
        gas_data: Gas price data
        gas_level: Gas level
        
    Returns:
        Notification message
    """
    if gas_level == GasLevel.LOW:
        return (f"🟢 LOW GAS ALERT: Ethereum gas prices are currently low at "
                f"{gas_data.propose_gas_price:.1f} Gwei. Good time for transactions!")
    
    elif gas_level == GasLevel.MEDIUM:
        return (f"🟡 Gas prices are moderate at {gas_data.propose_gas_price:.1f} Gwei. "
                f"Standard: {gas_data.safe_gas_price:.1f} Gwei, Fast: {gas_data.fast_gas_price:.1f} Gwei")
    
    elif gas_level == GasLevel.HIGH:
        return (f"🟠 Gas prices are high at {gas_data.propose_gas_price:.1f} Gwei. "
                f"Consider waiting for lower prices if not urgent.")
    
    else:  # VERY_HIGH
        return (f"🔴 Gas prices are very high at {gas_data.propose_gas_price:.1f} Gwei. "
                f"Recommend delaying non-urgent transactions.")


@gas_monitor_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the gas monitor agent on startup.
    """
    ctx.logger.info(f"Gas Monitor Agent started with address: {gas_monitor_agent.address}")
    
    # Initialize storage for gas price thresholds if it doesn't exist
    if not ctx.storage.get("thresholds"):
        ctx.storage.set("thresholds", {
            "low_threshold": LOW_THRESHOLD,
            "medium_threshold": MEDIUM_THRESHOLD,
            "high_threshold": HIGH_THRESHOLD
        })
    
    # Initialize storage for historical data if it doesn't exist
    if not ctx.storage.get("historical_data"):
        ctx.storage.set("historical_data", [])
    
    # Initialize storage for the previous gas level
    ctx.storage.set("previous_gas_level", None)
    
    # Log the current thresholds
    thresholds = ctx.storage.get("thresholds")
    ctx.logger.info(f"Gas price thresholds: Low < {thresholds['low_threshold']} Gwei, "
                   f"Medium < {thresholds['medium_threshold']} Gwei, "
                   f"High < {thresholds['high_threshold']} Gwei")


@gas_monitor_agent.on_interval(period=UPDATE_INTERVAL)
async def check_gas_prices(ctx: Context):
    """
    Check Ethereum gas prices at regular intervals.
    """
    ctx.logger.info("Checking current Ethereum gas prices...")
    
    # Fetch the latest gas prices
    gas_data = await fetch_gas_prices()
    
    if not gas_data:
        ctx.logger.error("Failed to fetch gas prices")
        return
    
    # Get the current thresholds
    thresholds = ctx.storage.get("thresholds")
    low_threshold = thresholds["low_threshold"]
    medium_threshold = thresholds["medium_threshold"]
    high_threshold = thresholds["high_threshold"]
    
    # Determine the gas level
    gas_level = gas_data.get_level(low_threshold, medium_threshold, high_threshold)
    
    # Log the gas prices
    ctx.logger.info(f"Current gas prices: Safe: {gas_data.safe_gas_price:.1f} Gwei, "
                   f"Average: {gas_data.propose_gas_price:.1f} Gwei, "
                   f"Fast: {gas_data.fast_gas_price:.1f} Gwei")
    ctx.logger.info(f"Gas level: {gas_level.value.upper()}")
    
    # Get the previous gas level
    previous_gas_level = ctx.storage.get("previous_gas_level")
    
    # Check if a notification should be sent
    if should_notify(gas_level, previous_gas_level):
        # Generate the notification message
        message = get_notification_message(gas_data, gas_level)
        
        # Create a notification
        notification = GasPriceNotification.create(gas_data, gas_level, message)
        
        # Log the notification
        ctx.logger.info(f"NOTIFICATION: {message}")
        
        # Store the notification
        notifications = ctx.storage.get("notifications", [])
        notifications.append(notification.dict())
        
        # Keep only the last 100 notifications to avoid excessive storage
        if len(notifications) > 100:
            notifications = notifications[-100:]
        
        ctx.storage.set("notifications", notifications)
    
    # Update the previous gas level
    ctx.storage.set("previous_gas_level", gas_level.value)
    
    # Update historical data
    historical_data = ctx.storage.get("historical_data", [])
    
    # Add the new gas price data to the historical data
    historical_data.append({
        "timestamp": gas_data.timestamp,
        "safe_gas_price": gas_data.safe_gas_price,
        "propose_gas_price": gas_data.propose_gas_price,
        "fast_gas_price": gas_data.fast_gas_price
    })
    
    # Keep only the last 1000 data points (approximately 16.7 hours at 1-minute intervals)
    if len(historical_data) > 1000:
        historical_data = historical_data[-1000:]
    
    # Save the updated historical data
    ctx.storage.set("historical_data", historical_data)


@gas_monitor_protocol.on_message(model=SetThresholdsRequest, replies={SetThresholdsResponse})
async def handle_set_thresholds(ctx: Context, sender: str, msg: SetThresholdsRequest):
    """
    Handle requests to set gas price thresholds.
    """
    thresholds = msg.thresholds
    ctx.logger.info(f"Received request to set thresholds from {sender}: {thresholds}")
    
    # Validate the thresholds
    if thresholds.low_threshold >= thresholds.medium_threshold:
        await ctx.send(sender, SetThresholdsResponse(
            success=False,
            message="Low threshold must be less than medium threshold"
        ))
        return
    
    if thresholds.medium_threshold >= thresholds.high_threshold:
        await ctx.send(sender, SetThresholdsResponse(
            success=False,
            message="Medium threshold must be less than high threshold"
        ))
        return
    
    # Update the thresholds
    ctx.storage.set("thresholds", {
        "low_threshold": thresholds.low_threshold,
        "medium_threshold": thresholds.medium_threshold,
        "high_threshold": thresholds.high_threshold
    })
    
    # Log the updated thresholds
    ctx.logger.info(f"Updated gas price thresholds: {thresholds}")
    
    # Send success response
    await ctx.send(sender, SetThresholdsResponse(
        success=True,
        message="Thresholds updated successfully"
    ))


@gas_monitor_protocol.on_message(model=GetGasPriceRequest, replies={GetGasPriceResponse})
async def handle_get_gas_price(ctx: Context, sender: str, msg: GetGasPriceRequest):
    """
    Handle requests to get the current gas price.
    """
    ctx.logger.info(f"Received request to get gas price from {sender}")
    
    # Fetch the latest gas prices
    gas_data = await fetch_gas_prices()
    
    if not gas_data:
        ctx.logger.error("Failed to fetch gas prices")
        return
    
    # Get the current thresholds
    thresholds = ctx.storage.get("thresholds")
    low_threshold = thresholds["low_threshold"]
    medium_threshold = thresholds["medium_threshold"]
    high_threshold = thresholds["high_threshold"]
    
    # Determine the gas level
    gas_level = gas_data.get_level(low_threshold, medium_threshold, high_threshold)
    
    # Send the response
    await ctx.send(sender, GetGasPriceResponse(
        gas_data=gas_data,
        gas_level=gas_level
    ))


@gas_monitor_protocol.on_message(model=GetHistoricalDataRequest, replies={GetHistoricalDataResponse})
async def handle_get_historical_data(ctx: Context, sender: str, msg: GetHistoricalDataRequest):
    """
    Handle requests to get historical gas price data.
    """
    ctx.logger.info(f"Received request to get historical data from {sender} for {msg.hours} hours")
    
    # Get the historical data
    historical_data = ctx.storage.get("historical_data", [])
    
    # Calculate the cutoff time
    cutoff_time = (datetime.utcnow() - timedelta(hours=msg.hours)).isoformat()
    
    # Filter the data to include only the requested time period
    filtered_data = [
        data for data in historical_data
        if data["timestamp"] >= cutoff_time
    ]
    
    # Calculate the average price
    if filtered_data:
        average_price = sum(data["propose_gas_price"] for data in filtered_data) / len(filtered_data)
    else:
        average_price = 0.0
    
    # Send the response
    await ctx.send(sender, GetHistoricalDataResponse(
        data=filtered_data,
        average_price=average_price
    ))


# Include the protocol in the agent
gas_monitor_agent.include(gas_monitor_protocol, publish_manifest=True)


if __name__ == "__main__":
    gas_monitor_agent.run()
