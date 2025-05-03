from uagents import Model
from typing import List, Dict, Optional
from enum import Enum


class TrendDirection(str, Enum):
    """
    Enum representing the direction of a price trend.
    """
    UP = "up"
    DOWN = "down"
    SIDEWAYS = "sideways"


class SignalStrength(str, Enum):
    """
    Enum representing the strength of a trading signal.
    """
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


class SignalType(str, Enum):
    """
    Enum representing the type of trading signal.
    """
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    NONE = "none"


class AnalysisResult(Model):
    """
    Model representing the result of technical analysis on a cryptocurrency.
    """
    symbol: str
    current_price: float
    timestamp: str
    
    # Technical indicators
    moving_avg_short: Optional[float] = None
    moving_avg_long: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    
    # Analysis results
    trend: TrendDirection
    signal: SignalType
    signal_strength: SignalStrength
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    prediction: Optional[str] = None
    
    def __str__(self):
        signal_str = f"{self.signal.value.upper()} ({self.signal_strength.value})" if self.signal != SignalType.NONE else "NONE"
        return f"{self.symbol}: Trend: {self.trend.value.upper()}, Signal: {signal_str}"


class AnalysisRequest(Model):
    """
    Request model for performing technical analysis on specific cryptocurrencies.
    """
    symbol: str
    include_prediction: bool = False
    indicators: List[str] = ["rsi", "macd", "moving_averages"]


class AnalysisResponse(Model):
    """
    Response model containing analysis results for requested cryptocurrencies.
    """
    results: List[AnalysisResult]
