import os
import asyncio
from datetime import datetime

from dotenv import load_dotenv
from uagents import Agent, Context

from models import (
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

# Client agent configuration
CLIENT_SEED = "gas-monitor-client-seed"
CLIENT_PORT = 8001
CLIENT_ENDPOINT = f"http://localhost:{CLIENT_PORT}/submit"

# Gas monitor agent address (this would be set after the gas monitor agent is running)
GAS_MONITOR_ADDRESS = os.getenv("GAS_MONITOR_ADDRESS", "")

# Create the client agent
client_agent = Agent(
    name="gas-monitor-client",
    seed=CLIENT_SEED,
    port=CLIENT_PORT,
    endpoint=CLIENT_ENDPOINT,
)


@client_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the client agent on startup.
    """
    ctx.logger.info(f"Gas Monitor Client started with address: {client_agent.address}")
    
    if not GAS_MONITOR_ADDRESS:
        ctx.logger.warning("Gas monitor agent address not configured. Set the GAS_MONITOR_ADDRESS environment variable.")
        return
    
    # Request the current gas price
    await request_gas_price(ctx)
    
    # Wait a bit for the response
    await asyncio.sleep(2)
    
    # Set custom thresholds
    await set_thresholds(ctx, 15.0, 40.0, 80.0)
    
    # Wait a bit for the response
    await asyncio.sleep(2)
    
    # Request historical data
    await request_historical_data(ctx, 1)  # Last hour


async def request_gas_price(ctx: Context):
    """
    Request the current gas price from the gas monitor agent.
    """
    if not GAS_MONITOR_ADDRESS:
        ctx.logger.error("Gas monitor agent address not configured")
        return
    
    ctx.logger.info("Requesting current gas price...")
    
    try:
        # Send request to gas monitor agent
        await ctx.send(GAS_MONITOR_ADDRESS, GetGasPriceRequest())
    except Exception as e:
        ctx.logger.error(f"Error requesting gas price: {e}")


async def set_thresholds(ctx: Context, low: float, medium: float, high: float):
    """
    Set custom gas price thresholds.
    
    Args:
        ctx: Agent context
        low: Low gas price threshold
        medium: Medium gas price threshold
        high: High gas price threshold
    """
    if not GAS_MONITOR_ADDRESS:
        ctx.logger.error("Gas monitor agent address not configured")
        return
    
    ctx.logger.info(f"Setting custom thresholds: Low={low}, Medium={medium}, High={high}")
    
    try:
        # Create thresholds
        thresholds = GasPriceThresholds(
            low_threshold=low,
            medium_threshold=medium,
            high_threshold=high
        )
        
        # Send request to gas monitor agent
        await ctx.send(GAS_MONITOR_ADDRESS, SetThresholdsRequest(thresholds=thresholds))
    except Exception as e:
        ctx.logger.error(f"Error setting thresholds: {e}")


async def request_historical_data(ctx: Context, hours: int = 24):
    """
    Request historical gas price data from the gas monitor agent.
    
    Args:
        ctx: Agent context
        hours: Number of hours of historical data to retrieve
    """
    if not GAS_MONITOR_ADDRESS:
        ctx.logger.error("Gas monitor agent address not configured")
        return
    
    ctx.logger.info(f"Requesting historical data for the last {hours} hours...")
    
    try:
        # Send request to gas monitor agent
        await ctx.send(GAS_MONITOR_ADDRESS, GetHistoricalDataRequest(hours=hours))
    except Exception as e:
        ctx.logger.error(f"Error requesting historical data: {e}")


@client_agent.on_message(model=GetGasPriceResponse)
async def handle_gas_price_response(ctx: Context, sender: str, msg: GetGasPriceResponse):
    """
    Handle gas price responses from the gas monitor agent.
    """
    gas_data = msg.gas_data
    gas_level = msg.gas_level
    
    ctx.logger.info(f"Received gas price response from {sender}")
    ctx.logger.info(f"Current gas prices: Safe: {gas_data.safe_gas_price:.1f} Gwei, "
                   f"Average: {gas_data.propose_gas_price:.1f} Gwei, "
                   f"Fast: {gas_data.fast_gas_price:.1f} Gwei")
    ctx.logger.info(f"Gas level: {gas_level.value.upper()}")


@client_agent.on_message(model=SetThresholdsResponse)
async def handle_set_thresholds_response(ctx: Context, sender: str, msg: SetThresholdsResponse):
    """
    Handle set thresholds responses from the gas monitor agent.
    """
    ctx.logger.info(f"Received set thresholds response from {sender}: {msg.message}")
    
    if msg.success:
        ctx.logger.info("Thresholds updated successfully")
    else:
        ctx.logger.error(f"Failed to update thresholds: {msg.message}")


@client_agent.on_message(model=GetHistoricalDataResponse)
async def handle_historical_data_response(ctx: Context, sender: str, msg: GetHistoricalDataResponse):
    """
    Handle historical data responses from the gas monitor agent.
    """
    ctx.logger.info(f"Received historical data response from {sender} with {len(msg.data)} data points")
    ctx.logger.info(f"Average gas price: {msg.average_price:.2f} Gwei")
    
    if msg.data:
        # Print the first and last data points
        first_data = msg.data[0]
        last_data = msg.data[-1]
        
        first_time = datetime.fromisoformat(first_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        last_time = datetime.fromisoformat(last_data["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        
        ctx.logger.info(f"First data point ({first_time}): {first_data['propose_gas_price']:.1f} Gwei")
        ctx.logger.info(f"Last data point ({last_time}): {last_data['propose_gas_price']:.1f} Gwei")
        
        # Calculate min and max prices
        min_price = min(data["propose_gas_price"] for data in msg.data)
        max_price = max(data["propose_gas_price"] for data in msg.data)
        
        ctx.logger.info(f"Min gas price: {min_price:.1f} Gwei, Max gas price: {max_price:.1f} Gwei")


if __name__ == "__main__":
    client_agent.run()
