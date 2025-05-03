from uagents import Model
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import uuid4


class AlertType(str, Enum):
    """
    Enum representing different types of alerts that can be configured.
    """
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PERCENT_CHANGE = "percent_change"
    RSI_OVERBOUGHT = "rsi_overbought"
    RSI_OVERSOLD = "rsi_oversold"
    MACD_CROSSOVER = "macd_crossover"
    MACD_CROSSUNDER = "macd_crossunder"
    TREND_REVERSAL = "trend_reversal"
    SUPPORT_BREAKOUT = "support_breakout"
    RESISTANCE_BREAKOUT = "resistance_breakout"
    VOLUME_SPIKE = "volume_spike"


class AlertConfig(Model):
    """
    Model representing an alert configuration.
    """
    alert_id: str
    symbol: str
    alert_type: AlertType
    threshold: float
    active: bool = True
    description: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None
    
    @classmethod
    def create(cls, symbol: str, alert_type: AlertType, threshold: float, description: Optional[str] = None):
        """
        Factory method to create an AlertConfig with a generated ID.
        """
        return cls(
            alert_id=str(uuid4()),
            symbol=symbol,
            alert_type=alert_type,
            threshold=threshold,
            description=description
        )
    
    def __str__(self):
        desc = f" - {self.description}" if self.description else ""
        status = "ACTIVE" if self.active else "INACTIVE"
        return f"[{status}] {self.symbol} {self.alert_type.value.replace('_', ' ').title()} {self.threshold}{desc}"


class AlertNotification(Model):
    """
    Model representing an alert notification sent when an alert is triggered.
    """
    alert_id: str
    symbol: str
    alert_type: AlertType
    triggered_value: float
    threshold: float
    message: str
    timestamp: str
    
    def __str__(self):
        return f"ALERT: {self.symbol} - {self.message}"


class ConfigureAlertRequest(Model):
    """
    Request model for configuring a new alert or updating an existing one.
    """
    config: AlertConfig


class ConfigureAlertResponse(Model):
    """
    Response model for alert configuration requests.
    """
    success: bool
    alert_id: Optional[str] = None
    message: Optional[str] = None


class DeleteAlertRequest(Model):
    """
    Request model for deleting an alert.
    """
    alert_id: str


class DeleteAlertResponse(Model):
    """
    Response model for alert deletion requests.
    """
    success: bool
    message: Optional[str] = None


class ListAlertsRequest(Model):
    """
    Request model for listing all configured alerts.
    """
    symbol: Optional[str] = None  # If provided, filter alerts by symbol
    active_only: bool = False     # If true, only return active alerts


class ListAlertsResponse(Model):
    """
    Response model for listing alerts.
    """
    alerts: List[AlertConfig]
