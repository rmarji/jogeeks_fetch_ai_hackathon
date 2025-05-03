import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

from dotenv import load_dotenv
from uagents import Agent, Context
from uagents.experimental.quota import QuotaProtocol, RateLimit

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
from protocols.analysis import AnalysisResult, SignalType, TrendDirection

# Load environment variables
load_dotenv()

# Agent configuration
AGENT_SEED = os.getenv("ALERT_AGENT_SEED", "alert-agent-seed")
AGENT_PORT = int(os.getenv("ALERT_AGENT_PORT", "8003"))
AGENT_ENDPOINT = f"http://localhost:{AGENT_PORT}/submit"

# Create the agent
alert_agent = Agent(
    name="alert-agent",
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

# Create a protocol with rate limiting
alert_protocol = QuotaProtocol(
    storage_reference=alert_agent.storage,
    name="Alert-Protocol",
    version="0.1.0",
    default_rate_limit=RateLimit(window_size_minutes=1, max_requests=10),
)


def check_price_alerts(
    symbol: str, 
    price: float, 
    alerts: List[AlertConfig]
) -> List[AlertNotification]:
    """
    Check if any price-based alerts are triggered.
    
    Args:
        symbol: Cryptocurrency symbol
        price: Current price
        alerts: List of alert configurations
        
    Returns:
        List of triggered alert notifications
    """
    triggered_alerts = []
    timestamp = datetime.utcnow().isoformat()
    
    for alert in alerts:
        if alert.symbol != symbol or not alert.active:
            continue
        
        if alert.alert_type == AlertType.PRICE_ABOVE and price > alert.threshold:
            notification = AlertNotification(
                alert_id=alert.alert_id,
                symbol=symbol,
                alert_type=alert.alert_type,
                triggered_value=price,
                threshold=alert.threshold,
                message=f"{symbol} price is above ${alert.threshold:.2f} (Current: ${price:.2f})",
                timestamp=timestamp
            )
            triggered_alerts.append(notification)
            
        elif alert.alert_type == AlertType.PRICE_BELOW and price < alert.threshold:
            notification = AlertNotification(
                alert_id=alert.alert_id,
                symbol=symbol,
                alert_type=alert.alert_type,
                triggered_value=price,
                threshold=alert.threshold,
                message=f"{symbol} price is below ${alert.threshold:.2f} (Current: ${price:.2f})",
                timestamp=timestamp
            )
            triggered_alerts.append(notification)
    
    return triggered_alerts


def check_indicator_alerts(
    analysis: AnalysisResult, 
    alerts: List[AlertConfig]
) -> List[AlertNotification]:
    """
    Check if any technical indicator-based alerts are triggered.
    
    Args:
        analysis: Analysis result for a cryptocurrency
        alerts: List of alert configurations
        
    Returns:
        List of triggered alert notifications
    """
    triggered_alerts = []
    symbol = analysis.symbol
    timestamp = datetime.utcnow().isoformat()
    
    for alert in alerts:
        if alert.symbol != symbol or not alert.active:
            continue
        
        if alert.alert_type == AlertType.RSI_OVERBOUGHT and analysis.rsi and analysis.rsi > alert.threshold:
            notification = AlertNotification(
                alert_id=alert.alert_id,
                symbol=symbol,
                alert_type=alert.alert_type,
                triggered_value=analysis.rsi,
                threshold=alert.threshold,
                message=f"{symbol} RSI is overbought at {analysis.rsi:.2f} (Threshold: {alert.threshold:.2f})",
                timestamp=timestamp
            )
            triggered_alerts.append(notification)
            
        elif alert.alert_type == AlertType.RSI_OVERSOLD and analysis.rsi and analysis.rsi < alert.threshold:
            notification = AlertNotification(
                alert_id=alert.alert_id,
                symbol=symbol,
                alert_type=alert.alert_type,
                triggered_value=analysis.rsi,
                threshold=alert.threshold,
                message=f"{symbol} RSI is oversold at {analysis.rsi:.2f} (Threshold: {alert.threshold:.2f})",
                timestamp=timestamp
            )
            triggered_alerts.append(notification)
            
        elif alert.alert_type == AlertType.MACD_CROSSOVER and analysis.macd and analysis.macd_signal:
            # Check if MACD crossed above signal line
            if analysis.macd > analysis.macd_signal and analysis.macd > 0:
                notification = AlertNotification(
                    alert_id=alert.alert_id,
                    symbol=symbol,
                    alert_type=alert.alert_type,
                    triggered_value=analysis.macd,
                    threshold=analysis.macd_signal,
                    message=f"{symbol} MACD crossed above signal line (MACD: {analysis.macd:.4f}, Signal: {analysis.macd_signal:.4f})",
                    timestamp=timestamp
                )
                triggered_alerts.append(notification)
                
        elif alert.alert_type == AlertType.MACD_CROSSUNDER and analysis.macd and analysis.macd_signal:
            # Check if MACD crossed below signal line
            if analysis.macd < analysis.macd_signal and analysis.macd < 0:
                notification = AlertNotification(
                    alert_id=alert.alert_id,
                    symbol=symbol,
                    alert_type=alert.alert_type,
                    triggered_value=analysis.macd,
                    threshold=analysis.macd_signal,
                    message=f"{symbol} MACD crossed below signal line (MACD: {analysis.macd:.4f}, Signal: {analysis.macd_signal:.4f})",
                    timestamp=timestamp
                )
                triggered_alerts.append(notification)
                
        elif alert.alert_type == AlertType.TREND_REVERSAL:
            # Check if trend has reversed
            previous_trend = alert.additional_params.get("previous_trend") if alert.additional_params else None
            
            if previous_trend and previous_trend != analysis.trend.value:
                notification = AlertNotification(
                    alert_id=alert.alert_id,
                    symbol=symbol,
                    alert_type=alert.alert_type,
                    triggered_value=0.0,  # Not applicable for trend reversal
                    threshold=0.0,  # Not applicable for trend reversal
                    message=f"{symbol} trend reversed from {previous_trend.upper()} to {analysis.trend.value.upper()}",
                    timestamp=timestamp
                )
                triggered_alerts.append(notification)
                
                # Update the previous trend
                if not alert.additional_params:
                    alert.additional_params = {}
                alert.additional_params["previous_trend"] = analysis.trend.value
    
    return triggered_alerts


@alert_agent.on_event("startup")
async def startup(ctx: Context):
    """
    Initialize the alert agent on startup.
    """
    ctx.logger.info(f"Alert Agent started with address: {alert_agent.address}")
    
    # Initialize storage for alerts if it doesn't exist or is empty
    alerts = ctx.storage.get("alerts")
    if not alerts:
        ctx.storage.set("alerts", [])
        
        # Create some default alerts
        default_alerts = [
            AlertConfig.create(
                symbol="BTC",
                alert_type=AlertType.PRICE_ABOVE,
                threshold=80000.0,
                description="Bitcoin price above $80,000"
            ),
            AlertConfig.create(
                symbol="ETH",
                alert_type=AlertType.PRICE_BELOW,
                threshold=1600.0,
                description="Ethereum price below $1,600"
            ),
            AlertConfig.create(
                symbol="SOL",
                alert_type=AlertType.PRICE_ABOVE,
                threshold=100.0,
                description="Solana price above $100"
            )
        ]
        
        ctx.storage.set("alerts", [alert.dict() for alert in default_alerts])
        ctx.logger.info(f"Created {len(default_alerts)} default alerts")
    
    # Initialize storage for triggered alerts if it doesn't exist
    if not ctx.storage.get("triggered_alerts"):
        ctx.storage.set("triggered_alerts", [])
        
    # Initialize storage for pending alerts if it doesn't exist
    if not ctx.storage.get("pending_alerts"):
        ctx.storage.set("pending_alerts", [])
    
    # Initialize storage for subscribed user agents if it doesn't exist
    if not ctx.storage.get("subscribed_users"):
        ctx.storage.set("subscribed_users", [])
        
        # Add the user agent to subscribed users
        user_agent_address = os.getenv("USER_AGENT_ADDRESS")
        if user_agent_address:
            ctx.storage.set("subscribed_users", [user_agent_address])
            ctx.logger.info(f"Added user agent {user_agent_address} to subscribed users")


@alert_agent.on_message(model=AnalysisResult)
async def handle_analysis_result(ctx: Context, sender: str, msg: AnalysisResult):
    """
    Handle analysis results from the analysis agent and check for triggered alerts.
    """
    ctx.logger.info(f"Received analysis result for {msg.symbol} from {sender}")
    
    # Get the current alerts
    alerts = ctx.storage.get("alerts")
    if alerts is None:
        alerts = []
    
    ctx.logger.info(f"Found {len(alerts)} configured alerts")
    
    # Convert the list of dictionaries to AlertConfig objects
    alert_configs = [AlertConfig(**alert) if isinstance(alert, dict) else alert for alert in alerts]
    
    # Log the current price and configured alerts for this symbol
    symbol_alerts = [alert for alert in alert_configs if alert.symbol == msg.symbol]
    ctx.logger.info(f"Current price of {msg.symbol}: ${msg.current_price:.2f}")
    ctx.logger.info(f"Found {len(symbol_alerts)} alerts for {msg.symbol}")
    for alert in symbol_alerts:
        ctx.logger.info(f"Alert: {alert.symbol} {alert.alert_type.value} {alert.threshold}")
    
    # Check for price-based alerts
    price_alerts = check_price_alerts(msg.symbol, msg.current_price, alert_configs)
    ctx.logger.info(f"Found {len(price_alerts)} triggered price alerts for {msg.symbol}")
    
    # Check for indicator-based alerts
    indicator_alerts = check_indicator_alerts(msg, alert_configs)
    ctx.logger.info(f"Found {len(indicator_alerts)} triggered indicator alerts for {msg.symbol}")
    
    # Combine all triggered alerts
    triggered_alerts = price_alerts + indicator_alerts
    
    if triggered_alerts:
        ctx.logger.info(f"Triggered {len(triggered_alerts)} alerts for {msg.symbol}")
        
        # Store the triggered alerts
        all_triggered_alerts = ctx.storage.get("triggered_alerts")
        if all_triggered_alerts is None:
            all_triggered_alerts = []
        all_triggered_alerts.extend([alert.dict() for alert in triggered_alerts])
        
        # Keep only the last 100 triggered alerts to avoid excessive storage
        if len(all_triggered_alerts) > 100:
            all_triggered_alerts = all_triggered_alerts[-100:]
        
        ctx.storage.set("triggered_alerts", all_triggered_alerts)
        
        # Store the triggered alerts for later sending
        # This ensures we don't lose alerts if the user agent isn't ready yet
        pending_alerts = ctx.storage.get("pending_alerts")
        if pending_alerts is None:
            pending_alerts = []
        
        # Add the new triggered alerts to the pending alerts
        for alert in triggered_alerts:
            pending_alerts.append({
                "alert": alert.dict(),
                "attempts": 0,
                "last_attempt": datetime.utcnow().isoformat()
            })
        
        ctx.storage.set("pending_alerts", pending_alerts)
        
        # Try to send the pending alerts
        await send_pending_alerts(ctx)
    
    # Update the alerts with any changes (e.g., updated previous_trend)
    ctx.storage.set("alerts", [alert.dict() if hasattr(alert, 'dict') else alert for alert in alert_configs])


@alert_protocol.on_message(model=ConfigureAlertRequest, replies={ConfigureAlertResponse})
async def handle_configure_alert(ctx: Context, sender: str, msg: ConfigureAlertRequest):
    """
    Handle requests to configure a new alert or update an existing one.
    """
    alert_config = msg.config
    ctx.logger.info(f"Received alert configuration from {sender}: {alert_config}")
    
    # Get the current alerts
    alerts = ctx.storage.get("alerts")
    if alerts is None:
        alerts = []
    
    # Convert the list of dictionaries to AlertConfig objects
    alert_configs = [AlertConfig(**alert) if isinstance(alert, dict) else alert for alert in alerts]
    
    # Check if this is an update to an existing alert
    existing_alert_index = None
    for i, alert in enumerate(alert_configs):
        if alert.alert_id == alert_config.alert_id:
            existing_alert_index = i
            break
    
    if existing_alert_index is not None:
        # Update the existing alert
        alert_configs[existing_alert_index] = alert_config
        ctx.logger.info(f"Updated alert {alert_config.alert_id}")
        
        # Send success response
        await ctx.send(sender, ConfigureAlertResponse(
            success=True,
            alert_id=alert_config.alert_id,
            message=f"Alert updated successfully"
        ))
    else:
        # Add the new alert
        alert_configs.append(alert_config)
        ctx.logger.info(f"Added new alert {alert_config.alert_id}")
        
        # Send success response
        await ctx.send(sender, ConfigureAlertResponse(
            success=True,
            alert_id=alert_config.alert_id,
            message=f"Alert created successfully"
        ))
    
    # Save the updated alerts
    ctx.storage.set("alerts", [alert.dict() if hasattr(alert, 'dict') else alert for alert in alert_configs])


@alert_protocol.on_message(model=DeleteAlertRequest, replies={DeleteAlertResponse})
async def handle_delete_alert(ctx: Context, sender: str, msg: DeleteAlertRequest):
    """
    Handle requests to delete an alert.
    """
    alert_id = msg.alert_id
    ctx.logger.info(f"Received request to delete alert {alert_id} from {sender}")
    
    # Get the current alerts
    alerts = ctx.storage.get("alerts")
    if alerts is None:
        alerts = []
    
    # Convert the list of dictionaries to AlertConfig objects
    alert_configs = [AlertConfig(**alert) if isinstance(alert, dict) else alert for alert in alerts]
    
    # Find the alert to delete
    alert_to_delete = None
    for i, alert in enumerate(alert_configs):
        if alert.alert_id == alert_id:
            alert_to_delete = i
            break
    
    if alert_to_delete is not None:
        # Remove the alert
        deleted_alert = alert_configs.pop(alert_to_delete)
        ctx.logger.info(f"Deleted alert {alert_id}")
        
        # Save the updated alerts
        ctx.storage.set("alerts", [alert.dict() if hasattr(alert, 'dict') else alert for alert in alert_configs])
        
        # Send success response
        await ctx.send(sender, DeleteAlertResponse(
            success=True,
            message=f"Alert deleted successfully"
        ))
    else:
        # Alert not found
        ctx.logger.warning(f"Alert {alert_id} not found")
        
        # Send failure response
        await ctx.send(sender, DeleteAlertResponse(
            success=False,
            message=f"Alert not found"
        ))


@alert_protocol.on_message(model=ListAlertsRequest, replies={ListAlertsResponse})
async def handle_list_alerts(ctx: Context, sender: str, msg: ListAlertsRequest):
    """
    Handle requests to list all configured alerts.
    """
    ctx.logger.info(f"Received request to list alerts from {sender}")
    
    # Get the current alerts
    alerts = ctx.storage.get("alerts")
    if alerts is None:
        alerts = []
    
    # Convert the list of dictionaries to AlertConfig objects
    alert_configs = [AlertConfig(**alert) if isinstance(alert, dict) else alert for alert in alerts]
    
    # Filter alerts if requested
    if msg.symbol:
        alert_configs = [alert for alert in alert_configs if alert.symbol == msg.symbol]
    
    if msg.active_only:
        alert_configs = [alert for alert in alert_configs if alert.active]
    
    # Send the response
    await ctx.send(sender, ListAlertsResponse(alerts=alert_configs))


async def send_pending_alerts(ctx: Context):
    """
    Send pending alerts to subscribed users.
    This function will be called periodically to retry sending alerts that failed to deliver.
    """
    # Get the pending alerts
    pending_alerts = ctx.storage.get("pending_alerts")
    if not pending_alerts or len(pending_alerts) == 0:
        return
    
    # Get the subscribed users
    subscribed_users = ctx.storage.get("subscribed_users")
    if not subscribed_users or len(subscribed_users) == 0:
        return
    
    # Try to send each pending alert
    remaining_alerts = []
    for alert_data in pending_alerts:
        alert = AlertNotification(**alert_data["alert"])
        attempts = alert_data["attempts"]
        
        # Try to send the alert to each subscribed user
        success = True
        for user_address in subscribed_users:
            try:
                await ctx.send(user_address, alert)
                ctx.logger.info(f"Successfully sent alert to {user_address}: {alert.message}")
            except Exception as e:
                ctx.logger.error(f"Failed to send alert to {user_address}: {e}")
                success = False
        
        # If the alert was not successfully sent to all users, keep it in the pending alerts
        if not success:
            alert_data["attempts"] += 1
            alert_data["last_attempt"] = datetime.utcnow().isoformat()
            
            # Only keep alerts that have been attempted less than 10 times
            if alert_data["attempts"] < 10:
                remaining_alerts.append(alert_data)
            else:
                ctx.logger.warning(f"Dropping alert after 10 failed attempts: {alert.message}")
    
    # Update the pending alerts
    ctx.storage.set("pending_alerts", remaining_alerts)


@alert_agent.on_interval(period=30.0)
async def retry_pending_alerts(ctx: Context):
    """
    Periodically retry sending pending alerts.
    """
    await send_pending_alerts(ctx)


# Include the protocol in the agent
alert_agent.include(alert_protocol, publish_manifest=True)


if __name__ == "__main__":
    alert_agent.run()
