from uagents import Model
from typing import List, Dict, Optional
from datetime import datetime


class PriceData(Model):
    """
    Model representing cryptocurrency price data.
    """
    symbol: str
    price: float
    timestamp: str
    volume_24h: Optional[float] = None
    percent_change_24h: Optional[float] = None
    market_cap: Optional[float] = None
    
    def __str__(self):
        return f"{self.symbol}: ${self.price:.2f} ({self.percent_change_24h:+.2f}% 24h)"


class PriceRequest(Model):
    """
    Request model for fetching price data for specific cryptocurrencies.
    """
    symbols: List[str]


class PriceResponse(Model):
    """
    Response model containing price data for requested cryptocurrencies.
    """
    prices: Dict[str, PriceData]
    source: str
    timestamp: str
    
    @classmethod
    def create(cls, prices: Dict[str, PriceData], source: str):
        """
        Factory method to create a PriceResponse with the current timestamp.
        """
        return cls(
            prices=prices,
            source=source,
            timestamp=datetime.utcnow().isoformat()
        )


class PriceUpdate(Model):
    """
    Model for broadcasting price updates to subscribed agents.
    """
    data: PriceData
