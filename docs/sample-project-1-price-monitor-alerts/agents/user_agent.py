import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.experimental.quota import QuotaProtocol, RateLimit

from protocols.price_data import PriceData, PriceRequest, PriceResponse
from protocols.analysis import (
    AnalysisRequest, 
    AnalysisResponse, 
    AnalysisResult,
    TrendDirection,
    SignalType,
    SignalStrength
)
from protocols.alerts import (
    AlertConfig,
    AlertNotification,
    AlertType,
    ConfigureAlertRequest,
    ConfigureAlertResponse,
    DeleteAlertRequest,
    DeleteAlertResponse,
    ListAlertsRequest,
    ListAlertsResponse
)

# Load environment variables
load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("USER_AGENT_SEED", "user-agent-seed")
AGENT_PORT = int(os.getenv("USER_AGENT_PORT", "8004"))
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"

# Other agent addresses (these would be set after the other agents are running)
PRICE_AGENT_ADDRESS = os.getenv("PRICE_AGENT_ADDRESS", "agent1qtawh5k0a6uns5dwa3sgf0gff945prv3zc44yvvlj0yv8utlt5h6xq89qm8")
ANALYSIS_AGENT_ADDRESS = os.getenv("ANALYSIS_AGENT_ADDRESS", "agent1qg82vxu3xpkle6tjgckmnf6t7u8jswk775yfytsasyd3q35cyue8zwdnzzr")
ALERT_AGENT_ADDRESS = os.getenv("ALERT_AGENT_ADDRESS", "agent1qd5ww7ul24ma54s4lqnv9sy42csqergzc9a4x0dpmwnl242hp54ewfsk6ay")

# Create the agent
user_agent = Agent(
    name="user-agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)


@user_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the user agent on startup.
    """
    ctx.logger.info(f"User Agent started with address: {user_agent.address}")
    
    # Initialize storage for preferences if it doesn't exist
    if not ctx.storage.get("preferences"):
        ctx.storage.set("preferences", {
            "cryptocurrencies": os.getenv("DEFAULT_CRYPTOCURRENCIES", "BTC,ETH,SOL,AVAX,DOT").split(","),
            "update_interval": int(os.getenv("PRICE_UPDATE_INTERVAL", "300")),
            "notification_enabled": True
        })
    
    # Initialize storage for received alerts if it doesn't exist
    if not ctx.storage.get("received_alerts"):
        ctx.storage.set("received_alerts", [])
    
    # Register with alert agent if address is available
    if ALERT_AGENT_ADDRESS:
        ctx.logger.info(f"Registering with alert agent at {ALERT_AGENT_ADDRESS}")
        
        # Store the alert agent address
        ctx.storage.set("alert_agent_address", ALERT_AGENT_ADDRESS)
        
        # We would need to implement a registration protocol
        # This is a placeholder for that functionality
        # await ctx.send(ALERT_AGENT_ADDRESS, RegisterRequest(agent_address=user_agent.address))


@user_agent.on_message(model=AlertNotification)
async def handle_alert_notification(ctx: Context, sender: str, msg: AlertNotification):
    """
    Handle alert notifications from the alert agent.
    """
    ctx.logger.info(f"Received alert notification: {msg}")
    
    # Store the received alert
    received_alerts = ctx.storage.get("received_alerts")
    if received_alerts is None:
        received_alerts = []
    received_alerts.append(msg.dict())
    
    # Keep only the last 100 alerts to avoid excessive storage
    if len(received_alerts) > 100:
        received_alerts = received_alerts[-100:]
    
    ctx.storage.set("received_alerts", received_alerts)
    
    # Check if notifications are enabled
    preferences = ctx.storage.get("preferences")
    if preferences is None:
        preferences = {}
    if preferences.get("notification_enabled", True):
        # In a real application, this could send a notification to the user
        # via email, SMS, push notification, etc.
        ctx.logger.info(f"NOTIFICATION: {msg.message}")


@user_agent.on_message(model=PriceResponse)
async def handle_price_response(ctx: Context, sender: str, msg: PriceResponse):
    """
    Handle price responses from the price agent.
    """
    ctx.logger.info(f"Received price data from {sender} for {len(msg.prices)} cryptocurrencies")
    
    # Store the latest prices
    ctx.storage.set("latest_prices", msg.dict())
    
    # Log the prices
    for symbol, price_data in msg.prices.items():
        ctx.logger.info(f"{symbol}: ${price_data.price:.2f} ({price_data.percent_change_24h:+.2f}% 24h)")


@user_agent.on_message(model=AnalysisResponse)
async def handle_analysis_response(ctx: Context, sender: str, msg: AnalysisResponse):
    """
    Handle analysis responses from the analysis agent.
    """
    ctx.logger.info(f"Received analysis results from {sender} for {len(msg.results)} cryptocurrencies")
    
    # Store the latest analysis results
    analysis_results = ctx.storage.get("analysis_results")
    if analysis_results is None:
        analysis_results = {}
    
    for result in msg.results:
        analysis_results[result.symbol] = result.dict()
        
        # Log the analysis result
        signal_str = f"{result.signal.value.upper()} ({result.signal_strength.value})" if result.signal != SignalType.NONE else "NONE"
        ctx.logger.info(f"{result.symbol}: Trend: {result.trend.value.upper()}, Signal: {signal_str}")
    
    ctx.storage.set("analysis_results", analysis_results)


async def request_price_data(ctx: Context, symbols: List[str]):
    """
    Request price data from the price agent.
    
    Args:
        ctx: Agent context
        symbols: List of cryptocurrency symbols to request prices for
    """
    if not PRICE_AGENT_ADDRESS:
        ctx.logger.error("Price agent address not configured")
        return
    
    ctx.logger.info(f"Requesting price data for: {', '.join(symbols)}")
    
    try:
        # Send price request to price agent
        await ctx.send(PRICE_AGENT_ADDRESS, PriceRequest(symbols=symbols))
    except Exception as e:
        ctx.logger.error(f"Error requesting price data: {e}")


async def request_analysis(ctx: Context, symbol: str):
    """
    Request technical analysis from the analysis agent.
    
    Args:
        ctx: Agent context
        symbol: Cryptocurrency symbol to request analysis for
    """
    if not ANALYSIS_AGENT_ADDRESS:
        ctx.logger.error("Analysis agent address not configured")
        return
    
    ctx.logger.info(f"Requesting analysis for: {symbol}")
    
    try:
        # Send analysis request to analysis agent
        await ctx.send(ANALYSIS_AGENT_ADDRESS, AnalysisRequest(
            symbol=symbol,
            include_prediction=True
        ))
    except Exception as e:
        ctx.logger.error(f"Error requesting analysis: {e}")


async def configure_alert(ctx: Context, alert_config: AlertConfig):
    """
    Configure a new alert or update an existing one.
    
    Args:
        ctx: Agent context
        alert_config: Alert configuration
    """
    if not ALERT_AGENT_ADDRESS:
        ctx.logger.error("Alert agent address not configured")
        return
    
    ctx.logger.info(f"Configuring alert for {alert_config.symbol}: {alert_config.alert_type.value}")
    
    try:
        # Send alert configuration to alert agent
        await ctx.send(ALERT_AGENT_ADDRESS, ConfigureAlertRequest(config=alert_config))
    except Exception as e:
        ctx.logger.error(f"Error configuring alert: {e}")


async def delete_alert(ctx: Context, alert_id: str):
    """
    Delete an alert.
    
    Args:
        ctx: Agent context
        alert_id: ID of the alert to delete
    """
    if not ALERT_AGENT_ADDRESS:
        ctx.logger.error("Alert agent address not configured")
        return
    
    ctx.logger.info(f"Deleting alert: {alert_id}")
    
    try:
        # Send delete request to alert agent
        await ctx.send(ALERT_AGENT_ADDRESS, DeleteAlertRequest(alert_id=alert_id))
    except Exception as e:
        ctx.logger.error(f"Error deleting alert: {e}")


async def list_alerts(ctx: Context, symbol: Optional[str] = None, active_only: bool = False):
    """
    List all configured alerts.
    
    Args:
        ctx: Agent context
        symbol: Optional symbol to filter alerts by
        active_only: Whether to only return active alerts
    """
    if not ALERT_AGENT_ADDRESS:
        ctx.logger.error("Alert agent address not configured")
        return
    
    ctx.logger.info("Requesting list of alerts")
    
    try:
        # Send list request to alert agent
        await ctx.send(ALERT_AGENT_ADDRESS, ListAlertsRequest(
            symbol=symbol,
            active_only=active_only
        ))
    except Exception as e:
        ctx.logger.error(f"Error listing alerts: {e}")


@user_agent.on_interval(period=60.0)
async def check_status(ctx: Context):
    """
    Periodically check the status of the system and request updates.
    """
    # Get user preferences
    preferences = ctx.storage.get("preferences")
    if preferences is None:
        preferences = {}
    cryptocurrencies = preferences.get("cryptocurrencies", ["BTC", "ETH"])
    
    # Request price data for all cryptocurrencies
    await request_price_data(ctx, cryptocurrencies)
    
    # Request analysis for each cryptocurrency
    for symbol in cryptocurrencies:
        await request_analysis(ctx, symbol)


# Example of how to create a price alert
async def create_price_alert_example(ctx: Context):
    """
    Example function to create a price alert.
    """
    # Create a price alert for Bitcoin
    alert_config = AlertConfig.create(
        symbol="BTC",
        alert_type=AlertType.PRICE_ABOVE,
        threshold=50000.0,
        description="Bitcoin price above $50,000"
    )
    
    await configure_alert(ctx, alert_config)


# Example of how to create an RSI alert
async def create_rsi_alert_example(ctx: Context):
    """
    Example function to create an RSI alert.
    """
    # Create an RSI alert for Ethereum
    alert_config = AlertConfig.create(
        symbol="ETH",
        alert_type=AlertType.RSI_OVERBOUGHT,
        threshold=70.0,
        description="Ethereum RSI overbought"
    )
    
    await configure_alert(ctx, alert_config)


if __name__ == "__main__":
    user_agent.run()
