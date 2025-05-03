from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from uagents import Model


class GasLevel(str, Enum):
    """
    Enum representing different gas price levels.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class GasPriceData(Model):
    """
    Model representing Ethereum gas price data.
    """
    timestamp: str
    safe_gas_price: float  # Safe/Slow gas price in Gwei
    propose_gas_price: float  # Proposed/Average gas price in Gwei
    fast_gas_price: float  # Fast gas price in Gwei
    base_fee: Optional[float] = None  # Base fee in Gwei (EIP-1559)
    priority_fee: Optional[float] = None  # Priority fee in Gwei (EIP-1559)
    source: str  # Source of the gas price data (e.g., "Etherscan", "Infura")
    
    @classmethod
    def create(cls, safe_price: float, propose_price: float, fast_price: float, 
               source: str, base_fee: Optional[float] = None, priority_fee: Optional[float] = None):
        """
        Factory method to create a GasPriceData with the current timestamp.
        """
        return cls(
            timestamp=datetime.utcnow().isoformat(),
            safe_gas_price=safe_price,
            propose_gas_price=propose_price,
            fast_gas_price=fast_price,
            base_fee=base_fee,
            priority_fee=priority_fee,
            source=source
        )
    
    def get_level(self, low_threshold: float, medium_threshold: float, high_threshold: float) -> GasLevel:
        """
        Determine the gas price level based on the proposed gas price.
        
        Args:
            low_threshold: Threshold for low gas price
            medium_threshold: Threshold for medium gas price
            high_threshold: Threshold for high gas price
            
        Returns:
            GasLevel enum value
        """
        if self.propose_gas_price < low_threshold:
            return GasLevel.LOW
        elif self.propose_gas_price < medium_threshold:
            return GasLevel.MEDIUM
        elif self.propose_gas_price < high_threshold:
            return GasLevel.HIGH
        else:
            return GasLevel.VERY_HIGH


class GasPriceNotification(Model):
    """
    Model representing a gas price notification.
    """
    timestamp: str
    gas_level: GasLevel
    safe_gas_price: float
    propose_gas_price: float
    fast_gas_price: float
    message: str
    
    @classmethod
    def create(cls, gas_data: GasPriceData, gas_level: GasLevel, message: str):
        """
        Factory method to create a GasPriceNotification from GasPriceData.
        """
        return cls(
            timestamp=datetime.utcnow().isoformat(),
            gas_level=gas_level,
            safe_gas_price=gas_data.safe_gas_price,
            propose_gas_price=gas_data.propose_gas_price,
            fast_gas_price=gas_data.fast_gas_price,
            message=message
        )


class GasPriceThresholds(Model):
    """
    Model representing user-defined gas price thresholds.
    """
    low_threshold: float
    medium_threshold: float
    high_threshold: float
    
    def __str__(self):
        return (f"Gas Price Thresholds: Low < {self.low_threshold} Gwei, "
                f"Medium < {self.medium_threshold} Gwei, "
                f"High < {self.high_threshold} Gwei")


class SetThresholdsRequest(Model):
    """
    Request model for setting gas price thresholds.
    """
    thresholds: GasPriceThresholds


class SetThresholdsResponse(Model):
    """
    Response model for setting gas price thresholds.
    """
    success: bool
    message: str


class GetGasPriceRequest(Model):
    """
    Request model for getting current gas prices.
    """
    pass


class GetGasPriceResponse(Model):
    """
    Response model for getting current gas prices.
    """
    gas_data: GasPriceData
    gas_level: GasLevel


class GetHistoricalDataRequest(Model):
    """
    Request model for getting historical gas price data.
    """
    hours: int = 24  # Number of hours of historical data to retrieve


class GetHistoricalDataResponse(Model):
    """
    Response model for getting historical gas price data.
    """
    data: List[Dict[str, Any]]  # List of historical gas price data points
    average_price: float  # Average gas price over the requested period
